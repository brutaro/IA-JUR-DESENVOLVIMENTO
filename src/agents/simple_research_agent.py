#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Pesquisa Simplificado
Fluxo direto: Query → Pinecone → Gemini → Resposta
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.pinecone_search_tool import PineconeSearchTool


@dataclass
class SearchResult:
    """Resultado de busca simplificado"""
    titulo: str
    conteudo: str
    score: float
    metadata: Dict[str, Any]


class SimpleResearchAgent:
    """Agente de pesquisa simplificado - fluxo direto"""

    def __init__(self, llm_config: Dict[str, Any]):
        self.logger = logging.getLogger(f"Agent.{self.__class__.__name__}")
        self.llm_config = llm_config
        self.llm_client = self._create_llm_instance()
        self.search_tool = PineconeSearchTool()

        self.logger.info("Agente de pesquisa simplificado inicializado")

    def _create_llm_instance(self):
        """Cria uma instância do LLM, usando Gemini 2.5"""
        try:
            import google.generativeai as genai
            import os
            from dotenv import load_dotenv

            load_dotenv()

            # Tenta API key do config primeiro, depois do ambiente
            api_key = self.llm_config.get('api_key') or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

            if not api_key:
                self.logger.error("API key do Gemini não encontrada no config nem no ambiente")
                return None

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(self.llm_config.get('model', 'gemini-2.5-flash'))
            self.logger.info(f"Instância do LLM Gemini criada: {self.llm_config.get('model', 'gemini-2.5-flash')}")
            return model

        except ImportError:
            self.logger.error("google-generativeai não está instalado")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao criar instância Gemini: {e}")
            return None

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Processa consulta com fluxo simplificado"""
        start_time = datetime.now()

        try:
            self.logger.info(f"Iniciando pesquisa simplificada: {query[:50]}...")

            # 1. Busca direta no Pinecone
            pinecone_results = self.search_tool.search(query, top_k=10)
            self.logger.info(f"Pinecone retornou {len(pinecone_results)} resultados")

            # 2. Converte para formato simplificado
            self.logger.info("Convertendo resultados do Pinecone...")
            search_results = []
            for i, result in enumerate(pinecone_results):
                self.logger.info(f"Convertendo resultado {i+1}: {result.titulo[:50]}...")
                search_results.append(SearchResult(
                    titulo=result.titulo,
                    conteudo=result.conteudo,
                    score=result.score,
                    metadata=result.metadata
                ))
            self.logger.info(f"Conversão concluída: {len(search_results)} resultados")

            # 3. Síntese direta com Gemini
            self.logger.info("Iniciando síntese...")
            synthesis = await self._synthesize_direct(query, search_results, context)
            self.logger.info("Síntese concluída")

            # 4. Resposta estruturada
            response = self._format_response(query, search_results, synthesis)

            processing_time = (datetime.now() - start_time).total_seconds()
            response['processing_time'] = processing_time

            self.logger.info(f"Pesquisa concluída em {processing_time:.2f}s")
            return response

        except Exception as e:
            self.logger.error(f"Erro na pesquisa: {e}")
            return {
                'error': f"Erro durante pesquisa: {str(e)}",
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

    async def _synthesize_direct(self, query: str, results: List[SearchResult], context: Optional[Dict] = None) -> str:
        """Síntese direta com Gemini - sem complicações"""

        # Prepara contexto dos documentos
        context_text = ""
        for i, result in enumerate(results[:5], 1):  # Top 5 resultados
            context_text += f"\n--- DOCUMENTO {i} ---\n"
            context_text += f"Título: {result.titulo}\n"
            context_text += f"Score: {result.score:.3f}\n"
            context_text += f"Conteúdo: {result.conteudo[:2000]}...\n"

        # Prompt simplificado e direto
        synthesis_prompt = f"""Você é um especialista jurídico. Analise os documentos e responda à pergunta.

PERGUNTA: {query}

DOCUMENTOS ENCONTRADOS:
{context_text}

INSTRUÇÕES:
1. Leia cada documento completamente
2. Extraia informações relevantes à pergunta
3. Cite artigos, parágrafos e itens específicos quando disponíveis
4. Use as referências reais dos documentos
5. Para listas, use bullet points (•) ao invés de asteriscos (*)
6. Seja objetivo e direto
7. NÃO diga "não há informações" se os documentos contêm dados relevantes

RESPOSTA:"""

        try:
            self.logger.info("Iniciando síntese com Gemini...")
            response = self.llm_client.generate_content(synthesis_prompt)
            self.logger.info("Síntese concluída")
            return response.text if response else "Síntese não disponível"
        except Exception as e:
            self.logger.error(f"Erro na síntese: {e}")
            return "Erro na síntese"

    def _format_response(self, query: str, results: List[SearchResult], synthesis: str) -> Dict[str, Any]:
        """Formata resposta final"""

        # Top sources para referência
        top_sources = []
        for result in results[:5]:
            top_sources.append({
                'titulo': result.titulo,
                'score': result.score,
                'metadata': result.metadata
            })

        return {
            'query': query,
            'synthesis': synthesis,
            'findings': {
                'total_documents': len(results),
                'top_sources': top_sources,
                'average_score': sum(r.score for r in results) / len(results) if results else 0
            },
            'agent_info': {
                'name': 'SimpleResearchAgent',
                'version': '1.0.0',
                'simplified_flow': True
            }
        }
