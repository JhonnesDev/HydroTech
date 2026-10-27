import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch, Mock

import requests
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from usuarios.models import Usuario
from rios.models import Medicao, PontoRisco, Rios
from rios.services.previsao import reference, forecast, ForecastError


def readings(slope=.2, last=2):
    now = timezone.now()
    return [{'horario': now-timedelta(minutes=(11-i)*5), 'nivel': last-slope*(11-i)/12} for i in range(12)]


class ForecastTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.point = SimpleNamespace(pk=1, limite_emergencia=3.5)

    def test_rising_reference(self):
        result = reference(readings(), 3.5)
        self.assertEqual(result['horas_referencia'], 7.5)
        self.assertEqual(result['tendencia'], 'subindo')

    def test_stable_falling_insufficient_stale_critical_horizon(self):
        for slope in [0, -.2]:
            self.assertEqual(reference(readings(slope), 3.5)['status'], 'sem_cruzamento')
        self.assertEqual(reference([], 3.5)['status'], 'dados_insuficientes')
        self.assertEqual(reference(readings()[:3], 3.5)['status'], 'dados_desatualizados')
        self.assertEqual(reference(readings()[-3:], 3.5)['status'], 'dados_insuficientes')
        self.assertEqual(reference(readings(last=4), 3.5)['status'], 'limite_atingido')
        self.assertEqual(reference(readings(.02), 3.5)['status'], 'fora_do_horizonte')

    @patch.dict('os.environ', {'GEMINI_API_KEY': ''})
    @patch('rios.services.previsao.requests.post')
    def test_no_key_never_fakes_ai(self, post):
        result = forecast(self.point, readings())
        self.assertIsNone(result['ia'])
        self.assertEqual(result['status_ia'], 'nao_configurada')
        post.assert_not_called()

    def response(self, hours=7.5):
        data = {'horas_estimadas': hours, 'tendencia': 'subindo',
                'justificativa': 'Nível em elevação.', 'limitacoes': 'Condicionado à tendência.'}
        return Mock(status_code=200, json=lambda: {'candidates': [{'content': {'parts': [{'text': json.dumps(data)}]}}]})

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-only'})
    @patch('rios.services.previsao.requests.post')
    def test_ai_response_and_cache(self, post):
        post.return_value = self.response()
        rows = readings()
        result = forecast(self.point, rows)
        self.assertEqual(result['ia']['horas_estimadas'], 7.5)
        forecast(self.point, rows)
        self.assertEqual(post.call_count, 1)
        self.assertNotIn('key=', post.call_args.args[0])

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-only'})
    @patch('rios.services.previsao.requests.post')
    def test_failures_and_unreliable_predictions(self, post):
        for code in [400, 403, 429, 500]:
            post.return_value = Mock(status_code=code)
            with self.assertRaises(ForecastError):
                forecast(self.point, readings())
        for hours in [True, -1, float('nan'), 23]:
            post.return_value = self.response(hours)
            with self.assertRaises(ForecastError):
                forecast(self.point, readings())
        post.side_effect = requests.Timeout()
        with self.assertRaises(ForecastError):
            forecast(self.point, readings())


class EndpointTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = Usuario.objects.create(nome='Defesa', email='defesa@example.com', data_nascimento='2000-01-01', is_defesa_civil=True)
        rio = Rios.objects.create(nome='Rio Teste', cidade='Cidade', estado='SP', risco_inundacao=2, criado_por=self.user)
        self.point = PontoRisco.objects.create(rio=rio, latitude=0, longitude=0, descricao='Ponto Teste', nivel_risco=2, criado_por=self.user)
        self.client = APIClient()
        self.url = f'/pontos-risco/{self.point.pk}/previsao/'
        self.read_url = f'/pontos-risco/{self.point.pk}/medicoes/'

    def test_permissions(self):
        self.assertEqual(self.client.post(self.url).status_code, 401)
        self.user.is_defesa_civil = False
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(self.url).status_code, 403)

    @patch.dict('os.environ', {'GEMINI_API_KEY': ''})
    def test_demo_is_separate_and_real_has_no_data(self):
        self.client.force_authenticate(self.user)
        result = self.client.post(self.url, {'demonstracao': True}, format='json')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['origem'], 'demonstracao')
        self.assertEqual(Medicao.objects.count(), 0)
        self.assertEqual(self.client.post(self.url).data['status'], 'dados_insuficientes')

    def test_ingestion_validation_idempotency_conflict(self):
        self.client.force_authenticate(self.user)
        payload = {'nivel': 2, 'registrado_em': timezone.now().isoformat()}
        self.assertEqual(self.client.post(self.read_url, payload).status_code, 201)
        self.assertEqual(self.client.post(self.read_url, payload).status_code, 200)
        payload['nivel'] = 3
        self.assertEqual(self.client.post(self.read_url, payload).status_code, 409)
        for value in [-1, 101, 'NaN']:
            payload['nivel'] = value
            self.assertEqual(self.client.post(self.read_url, payload).status_code, 400)
        payload.update(nivel=2, registrado_em=(timezone.now()+timedelta(hours=1)).isoformat())
        self.assertEqual(self.client.post(self.read_url, payload).status_code, 400)

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-only'})
    @patch('rios.services.previsao.requests.post')
    def test_persisted_history_to_ai_endpoint(self, post):
        self.client.force_authenticate(self.user)
        for row in readings():
            Medicao.objects.create(ponto=self.point, nivel=row['nivel'], registrado_em=row['horario'])
        data = {'horas_estimadas': 7.5, 'tendencia': 'subindo',
                'justificativa': 'Elevação de 0,2 m/h.', 'limitacoes': 'Somente se a tendência continuar.'}
        post.return_value = Mock(status_code=200, json=lambda: {'candidates': [{'content': {'parts': [{'text': json.dumps(data)}]}}]})
        result = self.client.post(self.url)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['origem'], 'medicoes')
        self.assertEqual(result.data['ia']['horas_estimadas'], 7.5)
        self.assertEqual(result.data['quantidade_leituras'], 12)
        self.assertEqual(self.client.post(self.url, {'demonstracao': 'invalid'}).status_code, 400)
