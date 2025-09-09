#!/usr/bin/env python3
"""
Script para preparar o projeto para o GitHub
Cria estrutura limpa e organizada
"""

import os
import shutil
from pathlib import Path

def create_github_structure():
    """Cria estrutura limpa para o GitHub"""

    print("🚀 Preparando projeto para o GitHub...")

    # Cria diretório de exemplo para configuração
    os.makedirs("examples", exist_ok=True)

    # Cria arquivo de exemplo de configuração
    env_example = """# Configuração do IA-JUR
# Copie este arquivo para .env e configure suas chaves

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here

# Configurações Pinecone
PINECONE_INDEX_NAME=agentes-juridicos
PINECONE_ENVIRONMENT=production

# Configurações do Sistema
CHUNK_SIZE=1024
CHUNK_OVERLAP=0.15
MAX_CONTEXT_SIZE=10

# Configurações do Servidor
HOST=0.0.0.0
PORT=8001
DEBUG=False
"""

    with open("examples/.env.example", "w", encoding="utf-8") as f:
        f.write(env_example)

    # Cria README de exemplo
    readme_example = """# Exemplo de Uso - IA-JUR

## Configuração Rápida

1. Copie o arquivo de configuração:
```bash
cp examples/.env.example .env
```

2. Configure suas chaves de API no arquivo `.env`

3. Instale as dependências:
```bash
pip install -r requirements.txt
pip install -r web/requirements.txt
```

4. Execute o servidor:
```bash
cd web && python main.py
```

5. Acesse: http://localhost:8001

## Testando a Memória Contextual

1. Faça uma pergunta: "O servidor tem direito a pagamento de diárias para realizar perícia médica?"
2. Faça um follow-up: "Pode me explicar mais a fundo sobre isso?"
3. Observe como o sistema detecta automaticamente o follow-up e enriquece a resposta com contexto!
"""

    with open("examples/README.md", "w", encoding="utf-8") as f:
        f.write(readme_example)

    # Cria diretório de testes
    os.makedirs("tests", exist_ok=True)

    # Move arquivos de teste para o diretório correto
    test_files = [
        "test_basic_functionality.py",
        "test_simple.py"
    ]

    for test_file in test_files:
        if Path(test_file).exists():
            shutil.move(test_file, f"tests/{test_file}")
            print(f"✅ Movido: {test_file} -> tests/")

    print("✅ Estrutura do GitHub criada!")
    print("📁 Diretórios criados: examples/, tests/")
    print("📄 Arquivos de exemplo criados")

if __name__ == "__main__":
    create_github_structure()
