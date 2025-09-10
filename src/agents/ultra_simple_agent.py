#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Ultra Simplificado
Apenas: Query → Pinecone → Gemini → Resposta
SEM memória, SEM contexto, SEM complicações
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.pinecone_search_tool import PineconeSearchTool


class UltraSimpleAgent:
    """Agente ultra simplificado - apenas o essencial"""

    def __init__(self, llm_config: Dict[str, Any]):
        self.logger = logging.getLogger(f"Agent.{self.__class__.__name__}")
        self.llm_config = llm_config
        self.llm_client = self._create_llm_instance()
        self.search_tool = PineconeSearchTool()

        self.logger.info("Agente ultra simplificado inicializado")

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

    async def process(self, query: str) -> Dict[str, Any]:
        """Processa consulta ultra simplificada"""
        start_time = datetime.now()

        try:
            self.logger.info(f"Iniciando processamento ultra simples: {query[:50]}...")

            # 1. Busca direta no Pinecone
            self.logger.info("1. Buscando no Pinecone...")
            pinecone_results = self.search_tool.search(query, top_k=5)
            self.logger.info(f"   Pinecone retornou {len(pinecone_results)} resultados")

            # 2. Prepara contexto como no agente em produção
            self.logger.info("2. Preparando contexto...")
            context_text = ""
            for i, result in enumerate(pinecone_results, 1):
                content_preview = result.conteudo[:3000]
                context_text += f"""
{result.titulo}:
Relevância: {result.score:.1%}
Conteúdo: {content_preview}
"""

            # 3. Prompt exato do agente em produção
            self.logger.info("3. Criando prompt...")
            prompt = f"""Você é um especialista jurídico. Com base nos documentos fornecidos, responda de forma OBJETIVA à pergunta:

"{query}"

DOCUMENTOS DISPONÍVEIS:
{context_text}

INSTRUÇÕES OBRIGATÓRIAS:
1. Responda de forma NATURAL e DIRETA, como um especialista jurídico
2. Extraia informações ESPECÍFICAS dos documentos (listas, procedimentos, requisitos)
3. Cite as fontes usando o TÍTULO real da nota técnica, ex: "conforme Nota Técnica 180/2022"
4. Use linguagem clara e profissional, sem expressões informais
5. Organize as informações de forma lógica e prática
6. Não use [DOCUMENTO X] - use sempre as referências reais
7. Não use expressões como "colega", "amigo", "prezado" - seja direto e objetivo

FORMATO DA RESPOSTA:
- Resposta direta e natural à pergunta
- Informações práticas organizadas
- Referências às notas técnicas pelo número/título real

RESPOSTA:"""

            # 4. Chama Gemini
            self.logger.info("4. Chamando Gemini...")
            response = self.llm_client.generate_content(prompt)
            self.logger.info("5. Gemini respondeu!")

            # 5. Formata resposta completa
            synthesis = response.text if response else "Erro na resposta"

            # 6. Resumo executivo removido conforme solicitado

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                'query': query,
                'synthesis': synthesis,
                'processing_time': processing_time,
                'total_documents': len(pinecone_results),
                'principais_fontes': [f"{r.titulo} (Relevância: {r.score:.1%})" for r in pinecone_results[:3]]
            }

        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}")
            return {
                'error': f"Erro: {str(e)}",
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
