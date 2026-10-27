# Previsão de tempo até o limite crítico

Implementação experimental para apresentação acadêmica. O Gemini analisa uma sequência de leituras por ponto e estima horas até o limite de emergência. Uma referência numérica pela mediana das inclinações entre pares verifica a plausibilidade da resposta. Não é um modelo hidrológico validado, nem deve orientar sozinho decisões operacionais.

## Configuração

Backend, na pasta `hydrotechDjango_core/backend`:

1. Configure `GEMINI_API_KEY` como segredo do servidor ou no `.env` local ignorado pelo Git. Nunca use `VITE_` para chaves secretas. A chave não deve entrar no repositório nem nos logs.
2. Opcional: `GEMINI_MODEL=gemini-2.5-flash` (padrão). A conta precisa ter acesso ao modelo e quota disponível.
3. Execute `python manage.py migrate` e inicie o Django.
4. Execute `python manage.py verificar_previsao_ia`. Este teste faz uma chamada REAL ao Google com dados fictícios; não grava medições e termina com erro se a integração não funcionar.
5. Execute `python manage.py test rios.test_previsao` para os testes automatizados isolados da rede. Esses testes usam respostas simuladas do provedor; não comprovam acesso real ao Gemini.

Para Vercel, configure `VITE_API_URL` com a URL HTTPS da API hospedada e faça novo build. No backend configure `CORS_ALLOWED_ORIGINS` incluindo a origem da Vercel, além de `ALLOWED_HOSTS`, banco persistente e segredo Django adequado. Hospedar somente o frontend não publica o backend.

## Uso

Entre com usuário marcado como Defesa Civil no Django Admin, acesse Dashboard e use o cartão **Previsão por IA · Gemini** em cada ponto cadastrado:

- **Analisar medições** consulta o histórico persistido do ponto; não usa os valores aleatórios dos gráficos antigos.
- **Demonstração com dados simulados** envia um cenário determinístico ao Gemini, claramente marcado e sem salvar valores no histórico real. Não envia alertas WhatsApp.
- Não há consulta automática ao abrir a página. As consultas são limitadas por usuário e respostas válidas ficam em cache por 5 minutos.

O banco recebe leituras pelo endpoint autenticado `POST /pontos-risco/{id}/medicoes/`, reservado a Defesa Civil. Corpo JSON:

```json
{"nivel": 2.1, "registrado_em": "2026-10-27T14:00:00-03:00"}
```

O horário deve ser atual ou passado, o nível deve ser finito entre 0 e 100 metros. Reenvio idêntico é idempotente; valor diferente no mesmo horário recebe 409. Sensores ainda precisam de integração para enviar essas leituras. Não coloque JWT de operador em firmware público.

`POST /pontos-risco/{id}/previsao/` com `{"demonstracao": false}` usa até 72 leituras das últimas 6 horas. Requer pelo menos 6 leituras em 20 minutos e última leitura há no máximo 30 minutos. O limite crítico é `limite_emergencia` do ponto. Projeções além de 24 horas são omitidas. Nível já crítico recebe estado explícito sem aguardar IA; tendência estável ou descendente não gera um prazo inventado.

Quando aplicável, Gemini recebe somente níveis, horários, limite e referência numérica. Não recebe nomes, telefones ou dados pessoais. A resposta JSON precisa ter prazo válido, tendência e explicação; divergências superiores a 50% da referência (com tolerância mínima de 15 minutos) são rejeitadas. Esta tolerância é uma regra de plausibilidade, NÃO um intervalo estatístico de confiança. Falhas de autenticação, quota, timeout e resposta inválida não são apresentadas como sucesso de IA.

## Limitações

- A interface indica que os gráficos preexistentes são simulados. A previsão real usa exclusivamente a tabela `Medicao`.
- Favoritos, WhatsApp e descrições de rios preexistentes não fazem parte desta previsão.
- O limite de uso e cache padrão Django são locais ao processo. Para múltiplos workers, configure cache compartilhado (como Redis) e limites no gateway antes de escalar.
- Não há calibração com séries hidrológicas reais, chuva, vazão ou relevo. Não se apresenta porcentagem de confiança inventada. A projeção depende da manutenção da tendência recente.
- A suíte geral preexistente ainda descobre `test_gemini.py`, que encerra a descoberta sem chave. Execute a suíte específica acima para esta funcionalidade.
