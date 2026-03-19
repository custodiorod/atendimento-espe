# Clinic AI - Guia de Configuração

Este guia ajuda você a configurar o Sistema de Atendimento com IA para Clínica ESPE.

## 🚀 Status Atual

- ✅ **FASE 1:** Infraestrutura definida (Docker Compose para Redis, RabbitMQ, Kestra)
- ✅ **FASE 2:** Estrutura Python criada (config, modelos, utilitários)
- ✅ **FASE 3:** Script SQL do Supabase pronto

## 📋 Próximos Passos

### 1. Criar Projeto Supabase

1. Acesse https://supabase.com
2. Crie um novo projeto
3. Copie as credenciais:
   - Project URL
   - anon/public key
   - service_role key

### 2. Executar Script SQL no Supabase

1. No painel do Supabase, vá em **SQL Editor**
2. Clique em **New Query**
3. Copie o conteúdo de `scripts/init_supabase.sql`
4. Cole e execute o script
5. Verifique se todas as tabelas foram criadas em **Table Editor**

### 3. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```bash
cp env.example .env
```

Preencha as variáveis obrigatórias:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OPENROUTER_API_KEY`
- `UAZAPI_BASE_URL`, `UAZAPI_TOKEN`, `UAZAPI_INSTANCE`
- `DOCTORALIA_API_KEY`
- `KOMMO_ACCESS_TOKEN`, `KOMMO_PIPELINE_ID`
- `OPENPIX_API_KEY`
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`

### 4. Instalar Dependências Python

```bash
pip install -e .
```

### 5. Testar API Localmente

```bash
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000

### 6. Deploy no Coolify

#### 6.1 Criar Aplicação (via interface)
1. No Coolify, clique em **New Application**
2. Selecione **Git**
3. Conecte seu repositório
4. Configure:
   - **Build Pack**: Python
   - **Port**: 8000
   - **Environment Variables**: Cole do arquivo `.env`

#### 6.2 Criar Serviços (Docker Compose)
1. No Coolify, clique em **New Service**
2. Selecione **Docker Compose**
3. Cole o conteúdo de `docker-compose.services.yml`
4. Deploy

## 📁 Estrutura Criada

```
clinic-ai/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configurações (pydantic-settings)
│   ├── database/
│   │   ├── supabase.py      # Cliente Supabase
│   │   └── models/          # Modelos Pydantic
│   └── utils/               # Utilitários (phone, dates, etc)
├── scripts/
│   └── init_supabase.sql    # Script SQL para criar tabelas
├── docker-compose.services.yml  # Redis, RabbitMQ, Kestra
├── Dockerfile               # Imagem da aplicação
├── pyproject.toml           # Dependências Python
├── env.example              # Variáveis de ambiente
└── SETUP.md                 # Este arquivo
```

## 🔍 Verificação

### Health Check
```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "app": "clinic-ai",
  "version": "0.1.0",
  "environment": "production"
}
```

### Testar Supabase Connection
```python
from app.database import get_supabase

db = get_supabase()
response = db.table('contacts').select('*').limit(1).execute()
print(response)
```

## 📝 Checklist de Configuração

- [ ] Projeto Supabase criado
- [ ] Script SQL executado (15 tabelas criadas)
- [ ] Variáveis de ambiente configuradas
- [ ] Dependências Python instaladas
- [ ] API rodando localmente
- [ ] Deploy no Coolify realizado
- [ ] Serviços (Redis, RabbitMQ, Kestra) rodando
- [ ] Webhooks configurados (Uazapi, Doctoralia, etc)

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs no Coolify
2. Verifique as variáveis de ambiente
3. Teste a conexão com Supabase
4. Consulte o README.md principal para arquitetura completa
