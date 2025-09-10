#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador Simplificado
Integra agente simples + memória modular
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .simple_research_agent import SimpleResearchAgent
from memory.context_manager import ContextManager


class SimpleOrchestrator:
    """Orquestrador simplificado com memória modular"""

    def __init__(self, llm_config: Dict[str, Any]):
        self.logger = logging.getLogger(f"Orchestrator.{self.__class__.__name__}")

        # Inicializa componentes
        self.research_agent = SimpleResearchAgent(llm_config)
        self.context_manager = ContextManager(max_interactions=10)

        self.logger.info("SimpleOrchestrator inicializado")

    async def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Processa query com memória modular"""
        start_time = datetime.now()

        try:
            self.logger.info(f"Processando query: {query[:50]}...")

            # 1. Obtém contexto da memória
            context_info = self.context_manager.get_context(query)

            # 2. Processa com agente simplificado
            result = await self.research_agent.process(query, context_info.get('context'))

            # 3. Adiciona contexto se for follow-up
            if context_info.get('is_followup'):
                result['context_info'] = {
                    'is_followup': True,
                    'context_summary': context_info.get('context_summary', '')
                }

            # 4. Salva interação na memória
            if 'synthesis' in result:
                await self.context_manager.add_interaction(
                    query=query,
                    response=result['synthesis'],
                    metadata={
                        'user_id': user_id,
                        'processing_time': result.get('processing_time', 0),
                        'total_documents': result.get('findings', {}).get('total_documents', 0)
                    }
                )

            # 5. Formata resposta final
            formatted_response = self._format_final_response(query, result, context_info)

            processing_time = (datetime.now() - start_time).total_seconds()
            formatted_response['processing_time'] = processing_time

            self.logger.info(f"Query processada em {processing_time:.2f}s")
            return formatted_response

        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}")
            return {
                'error': f"Erro durante processamento: {str(e)}",
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

    def _format_final_response(self, query: str, result: Dict[str, Any], context_info: Dict[str, Any]) -> Dict[str, Any]:
        """Formata resposta final"""

        # Extrai informações básicas
        synthesis = result.get('synthesis', 'Síntese não disponível')
        findings = result.get('findings', {})
        top_sources = findings.get('top_sources', [])

        # Formata resposta
        response = {
            'resumo_executivo': synthesis[:300] + "..." if len(synthesis) > 300 else synthesis,
            'resposta_completa': synthesis,
            'query_original': query,
            'fontes_consultadas': len(top_sources),
            'principais_fontes': [source['titulo'] for source in top_sources[:3]],
            'is_followup': context_info.get('is_followup', False)
        }

        # Adiciona contexto se for follow-up
        if context_info.get('is_followup'):
            response['contexto_anterior'] = context_info.get('context_summary', '')

        return response

    def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória"""
        return self.context_manager.get_memory_stats()

    def clear_memory(self):
        """Limpa memória"""
        self.context_manager.clear_memory()
        self.logger.info("Memória limpa pelo usuário")
