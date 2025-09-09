#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Agentes Jurídicos - Versão Simplificada
Focado no agente pesquisador para máxima simplicidade
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent / 'src'))

# Import após configuração do path
try:
    from agents.simple_orchestrator import SimpleLegalOrchestrator
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Verifique se o diretório src/agents existe e contém os "
          "arquivos necessários")
    sys.exit(1)

def configurar_llms():
    """Configura os LLMs para o agente pesquisador"""
    # Configuração padrão usando Gemini
    default_config = {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'api_key': os.getenv('GEMINI_API_KEY'),
        'temperature': 0.1,
        'max_tokens': 4000
    }

    # Configurações específicas para o agente pesquisador
    llm_configs = {
        'default': default_config,
        'research': {
            **default_config,
            'temperature': 0.1,
            'max_tokens': 6000
        }
    }

    return llm_configs

def exibir_menu():
    """Exibe o menu principal do sistema"""
    print("\n" + "=" * 70)
    print("🤖 SISTEMA DE AGENTES JURÍDICOS - VERSÃO SIMPLIFICADA")
    print("=" * 70)
    print("\nEscolha uma opção:")
    print("\n1. 🔍 Fazer uma pergunta jurídica (Pesquisa)")
    print("2. 📊 Ver métricas do sistema")
    print("3. ❌ Sair")
    print("\n" + "=" * 70)

def obter_consulta_usuario():
    """Obtém a consulta do usuário"""
    print("\n📝 Digite sua consulta jurídica:")
    print("(Pressione Enter duas vezes para confirmar)")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    consulta = "\n".join(lines)

    if not consulta.strip():
        print("❌ Consulta vazia. Tente novamente.")
        return obter_consulta_usuario()

    return consulta

async def processar_consulta(consulta: str):
    """Processa a consulta usando o orquestrador simplificado"""
    try:
        # Configura LLMs
        llm_configs = configurar_llms()

        # Cria orquestrador
        orchestrator = SimpleLegalOrchestrator(llm_configs, output_dir='./respostas')

        print("\n🔄 Processando consulta...")
        print("⏳ Isso pode levar alguns segundos...")

        # Processa consulta
        resultado = await orchestrator.process_query(consulta)

        if resultado.get('status') == 'error':
            print(f"\n❌ Erro no processamento: {resultado.get('message', 'Erro desconhecido')}")
            return

        # Exibe resultados
        exibir_resultados(resultado, consulta)

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("Verifique se as configurações estão corretas")

def exibir_resultados(resultado: Dict, consulta: str = None):
    """Exibe os resultados da consulta"""
    print("\n" + "=" * 70)
    print("📋 RESULTADOS DA CONSULTA")
    print("=" * 70)

    if consulta:
        print(f"\n🔍 Consulta realizada:")
        print(f"   {consulta}")

    # Exibe resumo
    summary = resultado.get('summary', 'Resumo não disponível')
    print(f"\n📝 Resumo da pesquisa:")
    print(f"   {summary}")

    # Exibe fontes encontradas
    sources_found = resultado.get('sources_found', 0)
    print(f"\n📚 Fontes consultadas:")
    print(f"   {sources_found} fontes encontradas")

    # Exibe metadados
    metadata = resultado.get('metadata', {})
    if metadata:
        duration = metadata.get('duration', 0)
        workflow_id = metadata.get('workflow_id', 'N/A')

        print(f"\n⏱️  Tempo de processamento: {duration:.2f} segundos")
        print(f"🆔 ID do workflow: {workflow_id}")

    # Exibe resposta formatada
    formatted_response = resultado.get('formatted_response', '')
    if formatted_response:
        print(f"\n📄 Resposta completa:")
        print("=" * 50)
        print(formatted_response)
        print("=" * 50)

    print(f"\n✅ Consulta processada com sucesso!")
    print(f"💾 Resposta salva em arquivo TXT na pasta 'respostas/respostas_txt/'")

def exibir_metricas(orchestrator):
    """Exibe métricas do sistema"""
    try:
        metricas = orchestrator.get_metrics()

        print("\n" + "=" * 50)
        print("📊 MÉTRICAS DO SISTEMA")
        print("=" * 50)

        print(f"\n🔢 Total de consultas: {metricas.get('total_queries', 0)}")
        print(f"🔍 Consultas de pesquisa: {metricas.get('research_queries', 0)}")

        print("\n" + "=" * 50)

    except Exception as e:
        print(f"\n❌ Erro ao obter métricas: {e}")

async def main():
    """Função principal do sistema"""
    print("🚀 Iniciando Sistema de Agentes Jurídicos...")

    while True:
        try:
            exibir_menu()
            opcao = input("\nEscolha uma opção (1-3): ").strip()

            if opcao == "1":
                # Pesquisa jurídica
                consulta = obter_consulta_usuario()
                await processar_consulta(consulta)

            elif opcao == "2":
                # Métricas do sistema
                try:
                    llm_configs = configurar_llms()
                    orchestrator = SimpleLegalOrchestrator(llm_configs)
                    exibir_metricas(orchestrator)
                except Exception as e:
                    print(f"\n❌ Erro ao obter métricas: {e}")

            elif opcao == "3":
                # Sair
                print("\n👋 Encerrando sistema...")
                print("✅ Obrigado por usar o Sistema de Agentes Jurídicos!")
                break

            else:
                print("\n❌ Opção inválida. Escolha 1, 2 ou 3.")

        except KeyboardInterrupt:
            print("\n\n👋 Sistema interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("Tente novamente ou escolha a opção 3 para sair.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
