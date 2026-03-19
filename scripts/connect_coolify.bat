@echo off
REM ============================================================
REM CLINIC AI - COOLIFY SSH CONNECTION HELPER
REM ============================================================
REM Uso: connect_coolify.bat [comando]
REM
REM Exemplos:
REM   connect_coolify.bat              - Abre shell interativo
REM   connect_coolify.bat ps            - Lista containers
REM   connect_coolify.bat setup         - Executa setup
REM ============================================================

setlocal

REM Configurações
set SERVER=root@coolify.espe.cloud
set KEY_FILE=%USERPROFILE%\.ssh\coolify_espe
set SCRIPT_DIR=%~dp0

REM Criar arquivo de chave temporária
set TEMP_KEY=%TEMP%\coolify_espe_key

REM Chave privada (substituir pela chave real)
set PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZWQyNTUxOQAAACBT7Heju6HfJC0yBPbgofpSVMDzPvm/G7cNpm6et8ATIQAAAJBmynC3ZspwtwAAAAtzc2gtZWQyNTUxOQAAACBT7Heju6HfJC0yBPbgofpSVMDzPvm/G7cNpm6et8ATIQAAAED8Fd++iLb48KsCTo3GeUqeMDj0lF4uOH7nSCtsZDAi+FPsd6O7od8kLTIE9uCh+lJUwPM++b8btw2mbp63wBMhAAAAB2Nvb2xpZnkBAgMEBQY=
-----END OPENSSH PRIVATE KEY-----

REM Criar arquivo de chave temporária
echo %PRIVATE_KEY% > %TEMP_KEY%

REM Definir permissões corretas (no Windows pode não funcionar, tentar mesmo assim)
echo Chave temporária criada em: %TEMP_KEY%

REM Verificar argumentos
if "%1"=="" (
    echo.
    echo Conectando ao Coolify...
    echo Pressione Ctrl+D para sair
    echo.
    ssh -i %TEMP_KEY% -o StrictHostKeyChecking=no %SERVER%
) else if "%1"=="ps" (
    ssh -i %TEMP_KEY% -o StrictHostKeyChecking=no %SERVER% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
) else if "%1"=="logs" (
    ssh -i %TEMP_KEY% -o StrictHostKeyChecking=no %SERVER% "docker logs -f --tail=100 clinic-ai-api"
) else if "%1"=="setup" (
    echo.
    echo Executando setup no servidor Coolify...
    echo.
    cat "%SCRIPT_DIR%setup_coolify.sh" | ssh -i %TEMP_KEY% -o StrictHostKeyChecking=no %SERVER% "bash -s"
) else if "%1"=="redis" (
    ssh -i %TEMP_KEY% -o StrictHostKeyChecking=no %SERVER% "docker exec -it clinic-ai-redis redis-cli -a clinicredis2024 ping"
) else if "%1"=="rabbitmq" (
    echo Management UI: http://coolify.espe.cloud:15672
    echo User: clinic
    echo Password: clinicrabbit2024
    start http://coolify.espe.cloud:15672
) else if "%1"=="kestra" (
    echo Kestra UI: http://coolify.espe.cloud:8080
    start http://coolify.espe.cloud:8080
) else (
    ssh -i %TEMP_KEY% -o StrictHostKeyChecking=no %SERVER% %*
)

REM Limpar chave temporária
del %TEMP_KEY% 2>nul

endlocal
