#!/usr/bin/env python3
"""
Script de inicialização do IA-JUR
Sistema de Pesquisa Jurídica Inteligente
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Função principal de inicialização"""
    print("🚀 IA-JUR - Sistema de Pesquisa Jurídica Inteligente")
    print("=" * 60)

    # Verifica se estamos no diretório correto
    current_dir = Path.cwd()
    web_dir = current_dir / "web"

    if not web_dir.exists():
        print("❌ Erro: Execute este script do diretório raiz do projeto")
        print(f"   Diretório atual: {current_dir}")
        print(f"   Diretório web esperado: {web_dir}")
        return 1

    # Muda para o diretório web
    os.chdir(web_dir)
    print(f"📁 Diretório web: {web_dir}")

    # Verifica se as dependências estão instaladas
    print("🔧 Verificando dependências...")
    try:
        import fastapi
        import uvicorn
        import jinja2
        print("✅ Dependências web instaladas")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("💡 Instale as dependências com: pip install -r web/requirements.txt")
        return 1

    # Verifica se o sistema principal está funcionando
    print("🔍 Verificando sistema principal...")
    try:
        sys.path.insert(0, str(current_dir))
        from src.agents.simple_orchestrator import SimpleLegalOrchestrator
        print("✅ Sistema principal funcionando")
    except ImportError as e:
        print(f"❌ Erro no sistema principal: {e}")
        print("💡 Verifique se o sistema CLI está funcionando")
        return 1

    # Inicia o servidor
    print("🌐 Iniciando servidor web...")
    print("📍 URL: http://localhost:8001")
    print("📚 Documentação: http://localhost:8001/docs")
    print("🔄 Pressione Ctrl+C para parar")
    print("-" * 60)

    try:
        # Inicia o servidor FastAPI
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8001",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
