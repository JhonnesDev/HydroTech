"""Gemini forecasts with a numerical reference, validated output and explicit provenance."""
import hashlib
import json
import math
import os
from datetime import timedelta
from statistics import median

import requests
from django.core.cache import cache
from django.utils import timezone

NOTICE = 'Estimativa experimental, condicionada à tendência observada. Não substitui avaliação da Defesa Civil.'


class ForecastError(Exception):
    pass


def reference(readings, critical, now=None):
    now = now or timezone.now()
    result = {'status': 'dados_insuficientes', 'horas_referencia': None,
              'tendencia': None, 'taxa_m_h': None, 'nivel_atual': None,
              'limite_critico': critical, 'quantidade_leituras': len(readings)}
    if not readings:
        return result
    result['nivel_atual'] = readings[-1]['nivel']
    result['ultima_leitura'] = readings[-1]['horario'].isoformat()
    if now - readings[-1]['horario'] > timedelta(minutes=30):
        result['status'] = 'dados_desatualizados'
        return result
    if readings[-1]['nivel'] >= critical:
        result.update(status='limite_atingido', horas_referencia=0)
        return result
    if len(readings) < 6 or readings[-1]['horario'] - readings[0]['horario'] < timedelta(minutes=20):
        return result
    # Median of pairwise slopes reduces sensitivity to isolated sensor spikes.
    slopes = [(b['nivel'] - a['nivel']) / ((b['horario'] - a['horario']).total_seconds() / 3600)
              for i, a in enumerate(readings) for b in readings[i + 1:]
              if b['horario'] > a['horario']]
    slope = median(slopes)
    trend = 'subindo' if slope > .01 else 'baixando' if slope < -.01 else 'estavel'
    result.update(tendencia=trend, taxa_m_h=round(slope, 4))
    if trend != 'subindo':
        result['status'] = 'sem_cruzamento'
        return result
    hours = (critical - readings[-1]['nivel']) / slope
    if hours > 24:
        result['status'] = 'fora_do_horizonte'
        return result
    result.update(status='previsao_disponivel', horas_referencia=round(hours, 3))
    return result


def demo_readings(point, now=None):
    now = now or timezone.now()
    # Explicit deterministic classroom scenario, never persisted as sensor data.
    base = max(0, point.limite_emergencia - 1)
    return [{'horario': now - timedelta(minutes=(11-i)*5),
             'nivel': round(max(0, base - (11-i)*.02), 3)} for i in range(12)]


def forecast(point, readings, demo=False):
    result = reference(readings, point.limite_emergencia)
    result.update(origem='demonstracao' if demo else 'medicoes', aviso=NOTICE,
                  gerado_em=timezone.now().isoformat(), ia=None)
    if result['status'] != 'previsao_disponivel':
        return result
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        result['status_ia'] = 'nao_configurada'
        return result
    model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    if not model.replace('-', '').replace('.', '').isalnum():
        raise ForecastError('Modelo Gemini inválido na configuração do servidor.')
    payload_data = {'limite_critico_m': point.limite_emergencia,
                    'referencia': result['horas_referencia'], 'demonstracao': demo,
                    'leituras': [{'horario': r['horario'].isoformat(), 'nivel_m': r['nivel']} for r in readings]}
    # Demo timestamps change each click; use relative times for a stable cache key.
    identity = {'model': model, 'point': point.pk, 'critical': point.limite_emergencia,
                'demo': demo, 'readings': ([r['nivel'] for r in readings] if demo else payload_data['leituras'])}
    cache_key = 'forecast:' + hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached:
        result.update(ia=cached, status_ia='disponivel')
        return result
    schema = {'type': 'OBJECT', 'properties': {
        'horas_estimadas': {'type': 'NUMBER'},
        'tendencia': {'type': 'STRING', 'enum': ['subindo']},
        'justificativa': {'type': 'STRING'},
        'limitacoes': {'type': 'STRING'}},
        'required': ['horas_estimadas', 'tendencia', 'justificativa', 'limitacoes']}
    prompt = ('Analise a série temporal de nível de água em metros. Estime o número de horas até o limite crítico, '
              'condicionado à manutenção da tendência. Use somente os números fornecidos, sem inventar chuva, '
              'previsão meteorológica ou dados regionais. A referência é uma verificação independente de tendência. '
              'Explique em português em até 350 caracteres por campo, explicitando incertezas. '
              'Não dê ordens de evacuação nem afirme segurança. Dados: ' + json.dumps(payload_data))
    try:
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
            headers={'x-goog-api-key': key},
            json={'contents': [{'parts': [{'text': prompt}]}],
                  'generationConfig': {'temperature': .1, 'maxOutputTokens': 2048,
                                       'responseMimeType': 'application/json', 'responseSchema': schema}},
            timeout=(5, 35))
        if response.status_code != 200:
            messages = {400: 'Chave ou requisição Gemini inválida.', 401: 'Autenticação Gemini recusada.',
                        403: 'Acesso ao Gemini recusado.', 429: 'Limite de uso do Gemini atingido.'}
            raise ForecastError(messages.get(response.status_code, 'Gemini indisponível. Tente novamente.'))
        parts = response.json()['candidates'][0]['content']['parts']
        data = json.loads(''.join(p.get('text', '') for p in parts if not p.get('thought')))
        hours = data['horas_estimadas']
        if isinstance(hours, bool) or not isinstance(hours, (int, float)) or not math.isfinite(hours) or not 0 < hours <= 24:
            raise ValueError('hours')
        if data['tendencia'] != 'subindo' or any(not isinstance(data[f], str) or not data[f].strip() or len(data[f]) > 1200 for f in ['justificativa', 'limitacoes']):
            raise ValueError('schema')
        ref = result['horas_referencia']
        if abs(hours - ref) > max(.25, ref * .5):
            raise ForecastError('A estimativa da IA divergiu da tendência. Aguarde novas leituras.')
        data['horas_estimadas'] = round(hours, 2)
        data['modelo'] = model
        cache.set(cache_key, data, 300)
        result.update(ia=data, status_ia='disponivel')
        return result
    except requests.RequestException:
        raise ForecastError('Falha de conexão com Gemini. Tente novamente.') from None
    except (ValueError, KeyError, IndexError, TypeError):
        raise ForecastError('Gemini retornou uma análise inválida. Tente novamente.') from None
