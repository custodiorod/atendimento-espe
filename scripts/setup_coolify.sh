#!/bin/bash
# ============================================================
# CLINIC AI - COOLIFY SERVER SETUP
# ============================================================
# Este script configura os serviços necessários no servidor Coolify
# Uso: ./setup_coolify.sh
# ============================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando no servidor Coolify
if [ ! -f "/.dockerenv" ] && [ ! -d "/data/coolify" ]; then
    log_warn "Este script deve ser rodado no servidor Coolify"
    log_info "Use: ssh root@<server-ip> 'bash -s' < setup_coolify.sh"
    exit 1
fi

log_info "Iniciando setup do Clinic AI no Coolify..."

# ============================================================
# 1. CRIAR REDE DOCKER
# ============================================================
log_info "Criando rede Docker clinic-ai-network..."

docker network create clinic-ai-network 2>/dev/null || true

# ============================================================
# 2. CRIAR VOLUMES
# ============================================================
log_info "Criando volumes Docker..."

docker volume create clinic-ai-redis-data 2>/dev/null || true
docker volume create clinic-ai-rabbitmq-data 2>/dev/null || true
docker volume create clinic-ai-kestra-db 2>/dev/null || true
docker volume create clinic-ai-kestra-storage 2>/dev/null || true
docker volume create clinic-ai-kestra-flows 2>/dev/null || true

# ============================================================
# 3. REDIS
# ============================================================
log_info "Configurando Redis..."

docker run -d \
    --name clinic-ai-redis \
    --restart unless-stopped \
    --network clinic-ai-network \
    -v clinic-ai-redis-data:/data \
    -p 6379:6379 \
    redis:7-alpine \
    redis-server --requirepass clinicredis2024 \
    --appendonly yes

# ============================================================
# 4. RABBITMQ
# ============================================================
log_info "Configurando RabbitMQ..."

docker run -d \
    --name clinic-ai-rabbitmq \
    --restart unless-stopped \
    --network clinic-ai-network \
    -v clinic-ai-rabbitmq-data:/var/lib/rabbitmq \
    -e RABBITMQ_DEFAULT_USER=clinic \
    -e RABBITMQ_DEFAULT_PASS=clinicrabbit2024 \
    -e RABBITMQ_DEFAULT_VHOST=/ \
    -p 5672:5672 \
    -p 15672:15672 \
    rabbitmq:3.13-management

# ============================================================
# 5. KESTRA (PostgreSQL + Kestra)
# ============================================================
log_info "Configurando PostgreSQL para Kestra..."

docker run -d \
    --name clinic-ai-postgres-kestra \
    --restart unless-stopped \
    --network clinic-ai-network \
    -v clinic-ai-kestra-db:/var/lib/postgresql/data \
    -e POSTGRES_DB=kestra \
    -e POSTGRES_USER=kestra \
    -e POSTGRES_PASSWORD=kestrapassword \
    postgres:16-alpine

# Esperar PostgreSQL estar pronto
log_info "Aguardando PostgreSQL..."
sleep 10

log_info "Configurando Kestra..."

docker run -d \
    --name clinic-ai-kestra \
    --restart unless-stopped \
    --network clinic-ai-network \
    -v clinic-ai-kestra-storage:/app/storage \
    -v clinic-ai-kestra-flows:/app/flows \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e KESTRA_CONFIGURATION_PATH=/app/kestra.yml \
    -p 8080:8080 \
    kestra/kestra:latest

# ============================================================
# 6. VERIFICAR SERVIÇOS
# ============================================================
log_info "Verificando serviços..."

sleep 5

echo ""
echo "============================================================"
echo "STATUS DOS SERVIÇOS"
echo "============================================================"

echo ""
echo "📦 Redis:"
docker ps --filter "name=clinic-ai-redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📦 RabbitMQ:"
docker ps --filter "name=clinic-ai-rabbitmq" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📦 PostgreSQL Kestra:"
docker ps --filter "name=clinic-ai-postgres-kestra" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📦 Kestra:"
docker ps --filter "name=clinic-ai-kestra" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# ============================================================
# 7. INFORMAÇÕES DE CONEXÃO
# ============================================================
echo ""
echo "============================================================"
echo "CREDENCIAIS DE ACESSO"
echo "============================================================"

echo ""
echo "🔴 Redis:"
echo "   URL: redis://:clinicredis2024@localhost:6379/0"
echo "   Host (interno): clinic-ai-redis"
echo "   Porta: 6379"
echo "   Password: clinicredis2024"

echo ""
echo "🟢 RabbitMQ:"
echo "   URL: amqp://clinic:clinicrabbit2024@localhost:5672/"
echo "   Management UI: http://localhost:15672"
echo "   User: clinic"
echo "   Password: clinicrabbit2024"

echo ""
echo "🔵 Kestra:"
echo "   URL: http://localhost:8080"
echo "   PostgreSQL:"
echo "     Host: clinic-ai-postgres-kestra"
echo "     Database: kestra"
echo "     User: kestra"
echo "     Password: kestrapassword"

echo ""
echo "============================================================"
echo "✅ SETUP COMPLETO!"
echo "============================================================"
echo ""
echo "Para conectar via SSH de fora:"
echo "  ssh -i <chave-privada> root@coolify.espe.cloud"
echo ""
