# Acesso SSH ao Coolify

## 📋 Credenciais

**Servidor:** `coolify.espe.cloud`
**Usuário:** `root`

**Chave SSH:**
- **Tipo:** ed25519
- **Fingerprint:** SHA256:... (verificar na primeira conexão)

## 🚀 Comandos Rápidos

### Via Python Script (Recomendado)

```bash
# Listar containers
python scripts/coolify_manager.py ps

# Executar setup completo (cria Redis, RabbitMQ, Kestra)
python scripts/coolify_manager.py setup

# Testar Redis
python scripts/coolify_manager.py redis ping

# Abrir UI do RabbitMQ
python scripts/coolify_manager.py rabbitmq

# Abrir UI do Kestra
python scripts/coolify_manager.py kestra

# Ver logs
python scripts/coolify_manager.py logs clinic-ai-redis

# Shell interativo
python scripts/coolify_manager.py shell
```

### Via Batch (Windows)

```cmd
REM Listar containers
scripts\connect_coolify.bat ps

REM Executar setup
scripts\connect_coolify.bat setup

REM Ver logs
scripts\connect_coolify.bat logs
```

### Via SSH Direto

```bash
# Salvar chave em arquivo temporário
cat > ~/.ssh/coolify_espe << 'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBT7Heju6HfJC0yBPbgofpSVMDzPvm/G7cNpm6et8ATIQAAAJBmynC3Zspw
twAAAAtzc2gtZWQyNTUxOQAAACBT7Heju6HfJC0yBPbgofpSVMDzPvm/G7cNpm6et8ATIQA
AAED8Fd++iLb48KsCTo3GeUqeMDj0lF4uOH7nSCtsZDAi+FPsd6O7od8kLTIE9uCh+lJUwP
M++b8btw2mbp63wBMhAAAAB2Nvb2xpZnkBAgMEBQY=
-----END OPENSSH PRIVATE KEY-----
EOF

chmod 600 ~/.ssh/coolify_espe

# Conectar
ssh -i ~/.ssh/coolify_espe root@coolify.espe.cloud

# Executar comando
ssh -i ~/.ssh/coolify_espe root@coolify.espe.cloud "docker ps"
```

## 🔗 URLs de Acesso

Após executar o setup:

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Coolify | https://coolify.espe.cloud | Token API |
| RabbitMQ UI | http://coolify.espe.cloud:15672 | clinic / clinicrabbit2024 |
| Kestra | http://coolify.espe.cloud:8080 | - |
| Redis | localhost:6379 (interno) | clinicredis2024 |

## ⚙️ Setup Inicial

Execute o setup para criar os serviços:

```bash
python scripts/coolify_manager.py setup
```

Isso criará:
- ✅ `clinic-ai-redis` - Redis container
- ✅ `clinic-ai-rabbitmq` - RabbitMQ com Management UI
- ✅ `clinic-ai-postgres-kestra` - PostgreSQL para Kestra
- ✅ `clinic-ai-kestra` - Kestra workflow engine

## 🔧 Comandos Úteis no Servidor

```bash
# Ver todos os containers
docker ps -a

# Ver logs de um container
docker logs -f clinic-ai-redis

# Reiniciar container
docker restart clinic-ai-redis

# Entrar no container
docker exec -it clinic-ai-redis sh

# Ver uso de recursos
docker stats

# Limpar containers parados
docker container prune -f

# Ver volumes
docker volume ls
```

## 🐛 Troubleshooting

### Redis não responde
```bash
docker logs clinic-ai-redis
docker restart clinic-ai-redis
docker exec clinic-ai-redis redis-cli -a clinicredis2024 ping
```

### RabbitMQ não inicia
```bash
docker logs clinic-ai-rabbitmq
docker restart clinic-ai-rabbitmq
```

### Kestra UI não abre
```bash
docker logs clinic-ai-kestra
# Verificar se PostgreSQL está rodando
docker logs clinic-ai-postgres-kestra
```

### Portas já em uso
```bash
# Ver o que está usando a porta
netstat -tulpn | grep :6379  # Redis
netstat -tulpn | grep :5672  # RabbitMQ
netstat -tulpn | grep :8080  # Kestra
```

## 🔐 Segurança

⚠️ **Importante:** As chaves SSH fornecidas acima são de exemplo.

Após o setup inicial:
1. Trocar a chave SSH do servidor
2. Usar senhas fortes para os serviços
3. Configurar firewall para permitir apenas IPs necessários
4. Não expor portas de gerenciamento (15672, 8080) publicamente
