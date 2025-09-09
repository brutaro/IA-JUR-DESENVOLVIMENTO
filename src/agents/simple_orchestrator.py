#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Orchestrator - Orquestrador Simples para Agente Pesquisador
Sistema simplificado focado na pesquisa jurídica
"""

import asyncio
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
from pathlib import Path

from .base_agent import AgentContext
from .research_agent import UnifiedResearchAgent

# Integração mínima do glossário
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from integration.glossary_integration import GlossaryIntegration

class SimpleLegalOrchestrator:
    """Orquestrador simples focado no agente pesquisador"""

    def __init__(self, llm_configs: Dict[str, Dict[str, Any]], output_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        # Configurações dos LLMs
        self.llm_configs = llm_configs

        # Diretório de saída
        self.output_dir = Path(output_dir) if output_dir else Path('./respostas')
        self.output_dir.mkdir(exist_ok=True)

        # Inicializa apenas o agente pesquisador
        self._initialize_research_agent()

        # Integração mínima do glossário
        self.glossary = GlossaryIntegration()

        # Métricas simplificadas
        self.metrics = {
            'total_queries': 0,
            'research_queries': 0
        }

    def _initialize_research_agent(self):
        """Inicializa apenas o agente pesquisador"""
        self.logger.info("Inicializando agente pesquisador...")

        try:
            # Agente de Pesquisa
            research_config = self.llm_configs.get('research', self.llm_configs.get('default', {}))
            research_config['provider'] = 'gemini'
            self.research_agent = UnifiedResearchAgent(research_config)

            self.logger.info("Agente pesquisador inicializado com sucesso!")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar agente pesquisador: {e}")
            raise

    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processa consulta usando apenas o agente pesquisador:

        1. Agente Orquestrador identifica a pergunta
        2. Roteia para o agente pesquisador
        3. Formatação e entrega ao usuário (JSON + TXT)
        """

        start_time = datetime.now()
        workflow_id = f"research_workflow_{start_time.strftime('%Y%m%d_%H%M%S')}"

        self.logger.info(f"Iniciando processamento: {query[:100]}...")

        # Atualiza métricas
        self.metrics['total_queries'] += 1
        self.metrics['research_queries'] += 1

        try:
            # Cria contexto para o agente
            context = AgentContext(
                session_id=workflow_id,
                original_query=query,
                current_stage="research",
                accumulated_context={},
                messages_history=[],
                metadata={}
            )

            # Processa com glossário (expansão de termos)
            try:
                processed_query = self.glossary.processar_query_completa(query)
                query_expandida = processed_query.get('query_expandida', query)
                context.accumulated_context['query_expandida'] = query_expandida
                self.logger.info(f"Query expandida: {query_expandida}")
            except Exception as e:
                self.logger.warning(f"Erro no glossário, usando query original: {e}")
                query_expandida = query

            # Executa pesquisa
            result = await self._execute_research(query, context)

            # Formata resposta
            formatted_result = self._format_research_response(result, query)

            # Calcula duração
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Adiciona metadados ANTES de salvar o arquivo TXT
            formatted_result['metadata'] = {
                'workflow_id': workflow_id,
                'duration': duration,
                'question_type': 'research',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }

            # Salva em arquivo TXT (agora com metadados)
            txt_file_path = self._save_response_to_txt(formatted_result, workflow_id, "research")

            self.logger.info(f"Processamento concluído em {duration:.2f}s")

            return formatted_result

        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}")
            return {
                'status': 'error',
                'message': f"Erro no processamento: {str(e)}",
                'question_type': 'research'
            }

    async def _execute_research(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Executa pesquisa usando o agente pesquisador"""
        # Usa query expandida se disponível
        query_to_use = context.accumulated_context.get('query_expandida', query)
        self.logger.info(f"Query para pesquisa: {query_to_use}")

        try:
            result = await self.research_agent.process(query_to_use)

            # Extrai a resposta estruturada do LLM
            structured_response = result.get('structured_response', {})
            executive_summary = structured_response.get('executive_summary', 'Síntese não disponível')

            return {
                'status': 'completed',
                'agent_type': 'research',
                'result': result,
                'summary': executive_summary,
                'sources_found': result.get('metrics', {}).get('total_sources', 0)
            }
        except Exception as e:
            self.logger.error(f"Erro na pesquisa: {e}")
            return {
                'status': 'error',
                'agent_type': 'research',
                'error': str(e)
            }

    def _format_response(self, result: Dict[str, Any], question_type: str, original_query: str) -> Dict[str, Any]:
        """Formata resposta final de forma clara e direta"""

        if result.get('status') == 'error':
            return {
                'status': 'error',
                'message': f"Erro no processamento: {result.get('error', 'Erro desconhecido')}",
                'question_type': question_type
            }

        # Para o sistema simplificado, sempre formata como pesquisa
        return self._format_research_response(result, original_query)

    def _format_research_response(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Formata resposta de pesquisa em estilo documental"""
        research_result = result.get('result', {})

        # Obtém informações detalhadas da pesquisa
        structured_response = research_result.get('structured_response', {})
        executive_summary = structured_response.get('executive_summary', result.get('summary', 'Síntese não disponível'))
        top_sources = structured_response.get('top_sources', [])

        # Formata fontes principais
        sources_text = ""
        if top_sources:
            sources_text = "\n".join([
                f"- {source.get('titulo', 'Título não disponível')} (Relevância: {source.get('score', 0):.1%})"
                for source in top_sources[:3]
            ])
        else:
            sources_text = "Nenhuma fonte específica identificada"

        return {
            'status': 'completed',
            'type': 'research',
            'query': query,
            'sources_found': result.get('sources_found', 0),
            'summary': executive_summary,
            'formatted_response': f"""
# RESPOSTA À PERGUNTA

## Consulta Realizada
{query}

## Resultado da Pesquisa
{executive_summary}

## Fontes Consultadas
{result.get('sources_found', 0)} fontes encontradas

## Principais Fontes
{sources_text}
            """.strip()
        }

    def _save_response_to_txt(self, formatted_result: Dict[str, Any], workflow_id: str, question_type: str) -> Path:
        """Salva a resposta formatada em arquivo TXT"""

        # Cria diretório de respostas se não existir
        responses_dir = self.output_dir / 'respostas_txt'
        responses_dir.mkdir(exist_ok=True)

        # Gera nome do arquivo com formato solicitado
        query = formatted_result.get('query', 'consulta')
        # Extrai palavras-chave da pergunta (primeiras 20 caracteres, sem pontuação)
        palavras_chave = query[:20].replace(' ', '_').replace('?', '').replace('!', '').replace('.', '').replace(',', '').replace(':', '').replace(';', '')
        data = datetime.now().strftime('%Y%m%d')
        hora = datetime.now().strftime('%H%M%S')
        filename = f"({palavras_chave}_{data}_{hora}).txt"
        file_path = responses_dir / filename

        # Conteúdo do arquivo TXT
        txt_content = self._generate_txt_content(formatted_result)

        # Salva arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)

        return file_path

    def _generate_txt_content(self, formatted_result: Dict[str, Any]) -> str:
        """Gera conteúdo do arquivo TXT baseado na resposta formatada"""

        # Obtém a resposta formatada
        formatted_response = formatted_result.get('formatted_response', '')
        query = formatted_result.get('query', '')
        question_type = formatted_result.get('type', 'unknown')

        # Gera cabeçalho do arquivo
        header = f"""
SISTEMA DE AGENTES JURÍDICOS - RESPOSTA GERADA
{'=' * 60}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Tipo: {question_type.upper()}
Consulta: {query}
{'=' * 60}

"""

        # Gera rodapé com metadados
        metadata = formatted_result.get('metadata', {})
        workflow_id = metadata.get('workflow_id', 'N/A')
        duration = metadata.get('duration', 0)
        question_type_meta = metadata.get('question_type', 'N/A')
        start_time = metadata.get('start_time', 'N/A')
        end_time = metadata.get('end_time', 'N/A')

        # Formata as datas para melhor legibilidade
        if start_time != 'N/A':
            try:
                start_dt = datetime.fromisoformat(start_time)
                start_formatted = start_dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                start_formatted = start_time
        else:
            start_formatted = 'N/A'

        if end_time != 'N/A':
            try:
                end_dt = datetime.fromisoformat(end_time)
                end_formatted = end_dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                end_formatted = end_time
        else:
            end_formatted = 'N/A'

        footer = f"""

{'=' * 60}
METADADOS DA CONSULTA
{'=' * 60}
🆔 Workflow ID: {workflow_id}
⏱️  Duração do Processamento: {duration:.2f} segundos
🎯 Tipo de Consulta: {question_type_meta.upper()}
🕐 Início: {start_formatted}
🕐 Conclusão: {end_formatted}
{'=' * 60}
"""

        # Conteúdo completo
        full_content = header + formatted_response + footer

        return full_content

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do sistema"""
        return {
            'total_queries': self.metrics['total_queries'],
            'research_queries': self.metrics['research_queries']
        }
