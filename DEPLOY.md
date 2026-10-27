# Publicar a previsão por IA

## 1. Backend no Render

Importe este repositório em Render → New → Blueprint. A configuração `render.yaml` prepara uma API Python com Gunicorn, PostgreSQL e HTTPS. O plano gratuito de PostgreSQL tem prazo de expiração definido pelo provedor; para conservar dados, faça backup e migre para banco persistente antes do prazo. Confirme os planos exibidos pelo Render antes de criar recursos.

No campo seguro `GEMINI_API_KEY`, informe sua chave do Google. A chave local `.env` não é enviada ao GitHub ou à Vercel. Use uma chave substituta se a anterior foi compartilhada publicamente. Não é necessário criar `.env` no Render.

Espere o serviço ficar saudável e copie a URL HTTPS REAL mostrada no painel (o nome pode receber um sufixo). O endpoint `/saude/` deve responder `{"status":"ok"}`. As migrações são aplicadas na inicialização; o banco novo começa vazio.

No Shell do serviço, execute `python manage.py createsuperuser` para criar o administrador Django. Pelo `/admin/`, crie um Usuario da aplicação, defina `is_defesa_civil`, e use senha devidamente hasheada: o ModelAdmin antigo não aplica hashing automaticamente. Alternativa no Shell Django: crie o Usuario com nome/email/data_nascimento e chame `set_password` e `save` sem imprimir a senha. O superusuário administrativo e o usuário da aplicação são modelos separados.

Execute `python manage.py verificar_previsao_ia` para validar uma chamada real ao Gemini. Sucesso nesse comando valida a integração com dados simulados, não a precisão hidrológica.

## 2. Frontend na Vercel

Mantenha Root Directory `hydrotech-frontend/hydrotech-vue`, preset Vite, build `npm run build`, output `dist`.

Em Settings → Environment Variables, defina `VITE_API_URL` com a URL HTTPS REAL do backend, sem barra final. Selecione Production. Faça Redeploy após alterar a variável: o Vite a incorpora no build. Nunca coloque GEMINI_API_KEY em variável VITE_.

O backend já permite a origem `https://hydro-tech-sand.vercel.app`. Se mudar de domínio, atualize `CORS_ALLOWED_ORIGINS` no Render. Previews da Vercel têm origens diferentes; não ficam autorizadas automaticamente.

## 3. Validação

- Abra `/login` diretamente e atualize a página: a reescrita SPA deve manter a aplicação acessível.
- Entre como Defesa Civil, crie um rio e um ponto e abra Dashboard.
- Clique em **Demonstração com dados simulados** e confirme a análise real Gemini identificada como demonstração.
- Sem medições registradas, **Analisar medições** deve indicar dados insuficientes.
- Cadastre leituras pelo endpoint documentado em `hydrotechDjango_core/backend/PREVISAO_IA.md` para usar o histórico real.

A configuração antiga de WhatsApp contém credencial no código do navegador e destinatários fixos; revogue essa credencial e migre o envio para backend antes de usar alertas reais. O modo de previsão por IA não envia mensagens.
