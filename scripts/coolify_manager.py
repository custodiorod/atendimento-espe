#!/usr/bin/env python3
"""
Clinic AI - Coolify SSH Manager

Script para gerenciar conexão SSH com o servidor Coolify
e executar comandos de forma segura.

Uso:
    python coolify_manager.py ps              # Lista containers
    python coolify_manager.py setup           # Executa setup completo
    python coolify_manager.py redis ping      # Testa Redis
    python coolify_manager.py logs <name>     # Ver logs
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
import argparse

# Configurações
COOLIFY_SERVER = "root@coolify.espe.cloud"
COOLIFY_HOST = "coolify.espe.cloud"

# Chave privada SSH (gerada pelo Coolify) - com quebras de linha corretas
SSH_PRIVATE_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDr83dHY2NrhFXE/f/NJUl2Q9AniFolgKoPjXMx618l7gAAAKBn/n9yZ/5/
cgAAAAtzc2gtZWQyNTUxOQAAACDr83dHY2NrhFXE/f/NJUl2Q9AniFolgKoPjXMx618l7gAA
AEBMMnY9YojGVdxIoedt3Eyw38ZJw5B5uKws8aTPHAvIMuvzd0djY2uEVcT9/80lSXZD0CeI
WiWAqg+NczHrXyXuAAAAF3BocHNlY2xpYi1nZW5lcmF0ZWQta2V5AQIDBAUG
-----END OPENSSH PRIVATE KEY-----
""".replace("\r\n", "\n")

# Chave pública correspondente (gerada pelo Coolify)
SSH_PUBLIC_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOvzd0djY2uEVcT9/80lSXZD0CeIWiWAqg+NczHrXyXu coolify-generated-ssh-key"


def create_temp_key_file() -> str:
    """Cria arquivo temporário com a chave privada."""
    key_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.key')
    key_file.write(SSH_PRIVATE_KEY)
    key_file.close()

    # Definir permissões corretas (no Windows pode não funcionar)
    try:
        os.chmod(key_file.name, 0o600)
    except Exception:
        pass

    return key_file.name


def run_ssh_command(command: str, key_file: str = None) -> tuple[int, str, str]:
    """
    Executa comando via SSH no servidor Coolify.

    Args:
        command: Comando a executar
        key_file: Caminho para arquivo de chave privada

    Returns:
        Tuple com (returncode, stdout, stderr)
    """
    if key_file is None:
        key_file = create_temp_key_file()
        cleanup = True
    else:
        cleanup = False

    try:
        ssh_cmd = [
            "ssh",
            "-i", key_file,
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            COOLIFY_SERVER,
            command
        ]

        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        return result.returncode, result.stdout, result.stderr

    finally:
        if cleanup:
            try:
                os.unlink(key_file)
            except Exception:
                pass


def command_ps(args):
    """Lista containers Docker."""
    print("\n[Containers] Containers Docker no Coolify:\n")
    code, out, err = run_ssh_command(
        "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'NAMES|clinic'"
    )
    if code == 0:
        print(out)
    else:
        print(f"Erro: {err}")


def command_setup(args):
    """Executa setup completo no servidor."""
    setup_script = Path(__file__).parent / "setup_coolify.sh"

    if not setup_script.exists():
        print(f"[ERROR] Script não encontrado: {setup_script}")
        return

    print("\n[Setup] Executando setup no servidor Coolify...\n")

    with open(setup_script) as f:
        script_content = f.read()

    key_file = create_temp_key_file()

    try:
        # Usar cat para passar o script
        ssh_cmd = f'bash -s << "EOF"\n{script_content}\nEOF'

        code, out, err = run_ssh_command(ssh_cmd, key_file)

        print(out)
        if err:
            print(f"[WARN]️  {err}")

        if code == 0:
            print("\n[OK] Setup completo!")
        else:
            print(f"\n[ERROR] Erro no setup (código: {code})")

    finally:
        try:
            os.unlink(key_file)
        except Exception:
            pass


def command_redis(args):
    """Comandos do Redis."""
    if args.args and args.args[0] == "ping":
        code, out, err = run_ssh_command(
            "docker exec clinic-ai-redis redis-cli -a clinicredis2024 ping"
        )
        print(out or err)
    elif args.args and args.args[0] == "cli":
        # Modo interativo
        key_file = create_temp_key_file()
        try:
            ssh_cmd = [
                "ssh", "-i", key_file,
                "-o", "StrictHostKeyChecking=no",
                COOLIFY_SERVER,
                "docker exec -it clinic-ai-redis redis-cli -a clinicredis2024"
            ]
            subprocess.run(ssh_cmd)
        finally:
            os.unlink(key_file)
    else:
        print("Uso: python coolify_manager.py redis [ping|cli]")


def command_rabbitmq(args):
    """Abre UI do RabbitMQ."""
    print("\n[RabbitMQ] RabbitMQ Management UI:")
    print(f"   URL: http://{COOLIFY_HOST}:15672")
    print("   User: clinic")
    print("   Password: clinicrabbit2024")
    print()

    # Tentar abrir navegador
    try:
        import webbrowser
        webbrowser.open(f"http://{COOLIFY_HOST}:15672")
        print("Abrindo navegador...")
    except Exception:
        pass


def command_kestra(args):
    """Abre UI do Kestra."""
    print("\n[Kestra] Kestra UI:")
    print(f"   URL: http://{COOLIFY_HOST}:8080")
    print()

    try:
        import webbrowser
        webbrowser.open(f"http://{COOLIFY_HOST}:8080")
        print("Abrindo navegador...")
    except Exception:
        pass


def command_logs(args):
    """Ver logs de um container."""
    if not args.args:
        print("Uso: python coolify_manager.py logs <container_name>")
        return

    container = args.args[0]
    follow = "--follow" if "--follow" in args.args else ""

    key_file = create_temp_key_file()
    try:
        ssh_cmd = [
            "ssh", "-i", key_file,
            "-o", "StrictHostKeyChecking=no",
            COOLIFY_SERVER,
            f"docker logs {follow} --tail=100 {container}"
        ]
        subprocess.run(ssh_cmd)
    finally:
        os.unlink(key_file)


def command_shell(args):
    """Abre shell interativo no servidor."""
    key_file = create_temp_key_file()
    try:
        ssh_cmd = [
            "ssh", "-i", key_file,
            "-o", "StrictHostKeyChecking=no",
            COOLIFY_SERVER
        ]
        subprocess.run(ssh_cmd)
    finally:
        os.unlink(key_file)


def command_install_key(args):
    """Instala a chave pública no authorized_keys do servidor."""
    print("\n[SSH Key] Instalando chave pública no servidor Coolify...\n")

    key_file = create_temp_key_file()

    try:
        # Comando para adicionar chave ao authorized_keys
        ssh_cmd = (
            f"mkdir -p ~/.ssh && "
            f"chmod 700 ~/.ssh && "
            f"echo '{SSH_PUBLIC_KEY}' >> ~/.ssh/authorized_keys && "
            f"chmod 600 ~/.ssh/authorized_keys && "
            f"echo 'Chave instalada com sucesso!' && "
            f"cat ~/.ssh/authorized_keys"
        )

        code, out, err = run_ssh_command(ssh_cmd, key_file)

        print(out)
        if err:
            print(f"[WARN]️  {err}")

        if code == 0:
            print("\n[OK] Chave pública instalada no servidor!")
            print(f"   Chave: {SSH_PUBLIC_KEY}")
        else:
            print(f"\n[ERROR] Erro ao instalar chave (código: {code})")

    finally:
        try:
            os.unlink(key_file)
        except Exception:
            pass


def command_test(args):
    """Testa a conexão SSH com o servidor."""
    print("\n[Test] Testando conexao SSH com o Coolify...\n")

    key_file = create_temp_key_file()

    try:
        code, out, err = run_ssh_command("echo 'Conexão OK!' && whoami && hostname", key_file)

        if code == 0:
            print(f"[OK] {out.strip()}")
            print("\nConexão SSH estabelecida com sucesso!")
        else:
            print(f"[ERROR] Erro na conexão: {err}")

    finally:
        try:
            os.unlink(key_file)
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Clinic AI - Coolify SSH Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python coolify_manager.py ps              Lista containers
  python coolify_manager.py setup           Executa setup
  python coolify_manager.py redis ping      Testa Redis
  python coolify_manager.py rabbitmq        Abre UI RabbitMQ
  python coolify_manager.py kestra          Abre UI Kestra
  python coolify_manager.py logs clinic-ai-api  Ver logs
  python coolify_manager.py shell           Shell interativo
  python coolify_manager.py test            Testa conexão SSH
  python coolify_manager.py install-key     Instala chave pública no servidor
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    subparsers.add_parser("ps", help="Lista containers Docker")
    subparsers.add_parser("setup", help="Executa setup no servidor")
    subparsers.add_parser("test", help="Testa conexão SSH")
    subparsers.add_parser("install-key", help="Instala chave pública no servidor")

    redis_parser = subparsers.add_parser("redis", help="Comandos Redis")
    redis_parser.add_argument("args", nargs="*", default=[], help="Argumentos Redis")

    subparsers.add_parser("rabbitmq", help="Abre UI do RabbitMQ")
    subparsers.add_parser("kestra", help="Abre UI do Kestra")

    logs_parser = subparsers.add_parser("logs", help="Ver logs de container")
    logs_parser.add_argument("args", nargs="*", default=[], help="Nome do container + opções")

    subparsers.add_parser("shell", help="Abre shell interativo")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "ps": command_ps,
        "setup": command_setup,
        "redis": command_redis,
        "rabbitmq": command_rabbitmq,
        "kestra": command_kestra,
        "logs": command_logs,
        "shell": command_shell,
        "test": command_test,
        "install-key": command_install_key,
    }

    command_func = commands.get(args.command)
    if command_func:
        command_func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
