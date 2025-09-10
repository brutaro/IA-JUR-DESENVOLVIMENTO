#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Research Agent - Agente Unificado de Pesquisa Jurídica
Combina o melhor dos agentes de pesquisa anteriores com integração Pinecone
"""

from typing import Dict, List, Any, Union, Tuple
import re
import time
import logging
from datetime import datetime

from .base_agent import BaseAgent
from src.tools.pinecone_search_tool import PineconeSearchTool
import asyncio


class UnifiedResearchAgent(BaseAgent):
    """Agente unificado especializado em pesquisa jurídica com Pinecone"""

    def __init__(self, llm_config: Dict[str, Any]):
        super().__init__(
            name="UnifiedResearchAgent",
            role="Pesquisador Jurídico Unificado",
            llm_config=llm_config,
            tools=None
        )

        # Instância da ferramenta de busca Pinecone
        try:
            self.search_tool = PineconeSearchTool()
            self.logger.info("Ferramenta de busca Pinecone inicializada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar ferramenta Pinecone: {e}")
            self.search_tool = None

        # Configurações específicas de pesquisa
        self.max_search_iterations = 5
        self.min_sources_per_category = 3
        self.similarity_threshold = 0.7  # Threshold para relevância

        # Cria instância do LLM
        self.llm_client = self._create_llm_instance()

        # Cache para resultados de busca
        self._search_cache = {}

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

    def get_capabilities(self) -> List[str]:
        return [
            "Pesquisa vetorial avançada com Pinecone",
            "Análise de jurisprudência e precedentes",
            "Busca por legislação específica",
            "Identificação de entendimentos consolidados",
            "Síntese inteligente de resultados",
            "Categorização automática de fontes",
            "Cache inteligente de resultados"
        ]

    async def process(self, input_data: Union[str, Dict]) -> Dict[str, Any]:
        """Processa a pesquisa jurídica unificada"""

        # Obtém informações do agente
        agent_info = {
            'description': 'Agente unificado especializado em pesquisa jurídica com Pinecone',
            'capabilities': self.get_capabilities(),
            'search_engine': 'Pinecone + text-embedding-004',
            'best_for': [
                'Pesquisas semanticamente precisas',
                'Análise de jurisprudência e precedentes',
                'Identificação de entendimentos consolidados',
                'Busca contextual em notas técnicas',
                'Síntese de posicionamentos administrativos'
            ]
        }

        # Extrai informações do input
        if isinstance(input_data, str):
            query = input_data
            triage_context = {}
        else:
            query = input_data.get('query', '')
            triage_context = input_data.get('triage_context', {})

        start_time = datetime.now()

        self.log_activity("Iniciando pesquisa jurídica unificada", {
            'query_length': len(query),
            'has_triage_context': bool(triage_context),
            'search_engine': 'Pinecone'
        })

        if not self.search_tool:
            return {
                'error': 'Ferramenta de busca Pinecone não disponível',
                'agent_info': agent_info
            }

        try:
            # Cache temporariamente desabilitado para debug
            # cache_key = f"{query}_{len(str(triage_context))}"
            # if cache_key in self._search_cache:
            #     cached_result = self._search_cache[cache_key]
            #     self.logger.info("Resultado encontrado em cache")
            #     return cached_result

            # Etapa 1: Análise e expansão da consulta
            query_analysis = await self._analyze_query(query, triage_context)

            # Etapa 2: Pesquisa estruturada no Pinecone
            search_results = await self._execute_pinecone_search(query_analysis)
            # Etapa 3: Análise e categorização dos resultados
            categorized_results = await self._categorize_results(search_results)

            # Etapa 4: Síntese inteligente usando LLM
            synthesis = await self._synthesize_findings(query, categorized_results)

            # Etapa 5: Gera resposta estruturada
            structured_response = await self._generate_structured_response(
                query, query_analysis, categorized_results, synthesis
            )

            # Atualiza contexto
            self.update_context('research_results', categorized_results)
            self.update_context('synthesis', synthesis)
            self.update_context('structured_response', structured_response)

            # Calcula métricas
            processing_time = (datetime.now() - start_time).total_seconds()
            total_sources = len(search_results)
            relevant_sources = len([r for r in search_results if r.score >= self.similarity_threshold])
            confidence_level = self._calculate_confidence(categorized_results)

            # Prepara resposta final
            result = {
                'agent_info': agent_info,
                'query_analysis': query_analysis,
                'search_results': [
                    {
                        'documento_id': r.documento_id,
                        'titulo': r.titulo,
                        'score': r.score,
                        'conteudo_preview': r.conteudo[:200] + '...' if len(r.conteudo) > 200 else r.conteudo,
                        'metadata': r.metadata
                    } for r in search_results
                ],
                'documents': [
                    {
                        'id': r.documento_id,
                        'title': r.titulo,
                        'content': r.conteudo,
                        'score': r.score,
                        'metadata': r.metadata
                    } for r in search_results
                ],  # Adiciona chave documents para compatibilidade
                'categorized_results': categorized_results,
                'synthesis': synthesis,
                'structured_response': structured_response,
                'metrics': {
                    'processing_time': processing_time,
                    'total_sources': total_sources,
                    'relevant_sources': relevant_sources,
                    'relevance_rate': relevant_sources / total_sources if total_sources > 0 else 0,
                    'confidence_level': confidence_level,
                    'search_engine': 'Pinecone',
                    'embedding_model': 'text-embedding-004'
                },
                'recommendations': self._generate_recommendations(categorized_results, confidence_level)
            }

            # Cache desabilitado temporariamente
            # self._search_cache[cache_key] = result

            self.log_activity("Pesquisa jurídica concluída", {
                'total_sources': total_sources,
                'relevant_sources': relevant_sources,
                'confidence': confidence_level,
                'processing_time': processing_time
            })

            return result

        except Exception as e:
            error_result = {
                'error': f"Erro durante pesquisa: {str(e)}",
                'agent_info': agent_info,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            self.logger.error(f"Erro na pesquisa: {e}")
            return error_result

    async def _analyze_query(self, query: str, triage_context: Dict) -> Dict[str, Any]:
        """Analisa e expande a consulta para melhorar a busca"""

        # Extrai termos-chave básicos
        keywords = self._extract_keywords(query)

        # Identifica tipo de consulta jurídica
        query_type = self._identify_query_type(query)

        # Gera variações da consulta
        query_variants = self._generate_query_variants(query, keywords)

        return {
            'original_query': query,
            'keywords': keywords,
            'query_type': query_type,
            'query_variants': query_variants,
            'triage_context': triage_context,
            'analysis_timestamp': datetime.now().isoformat()
        }

    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai palavras-chave relevantes da consulta"""
        # Remove pontuação e converte para minúsculas
        clean_query = re.sub(r'[^\w\s]', ' ', query.lower())

        # Lista de stopwords jurídicas
        stopwords = {
            'sobre', 'acerca', 'quanto', 'como', 'quando', 'onde', 'por', 'para',
            'em', 'de', 'da', 'do', 'das', 'dos', 'na', 'no', 'nas', 'nos',
            'a', 'o', 'as', 'os', 'e', 'ou', 'mas', 'que', 'se', 'é', 'foi',
            'será', 'pode', 'deve', 'tem', 'há', 'sua', 'seu', 'suas', 'seus'
        }

        # Extrai palavras significativas
        words = clean_query.split()
        keywords = [word for word in words if len(word) > 2 and word not in stopwords]

        return keywords[:10]  # Limita a 10 palavras-chave

    def _identify_query_type(self, query: str) -> str:
        """Identifica o tipo de consulta jurídica"""
        query_lower = query.lower()

        if any(term in query_lower for term in ['licença', 'férias', 'afastamento']):
            return 'licenças_afastamentos'
        elif any(term in query_lower for term in ['progressão', 'promoção', 'evolução']):
            return 'progressao_funcional'
        elif any(term in query_lower for term in ['indenização', 'auxílio', 'ajuda de custo']):
            return 'indenizacoes_auxilios'
        elif any(term in query_lower for term in ['aposentadoria', 'abono permanência']):
            return 'aposentadoria_pensao'
        elif any(term in query_lower for term in ['acumulação', 'cargo', 'função']):
            return 'acumulacao_cargos'
        else:
            return 'consulta_geral'

    def _generate_query_variants(self, query: str, keywords: List[str]) -> List[str]:
        """Gera variações simples da query para busca mais abrangente"""
        variants = [query]  # Consulta original

        # Consulta só com palavras-chave (máximo 1 variação)
        if keywords:
            keyword_query = ' '.join(keywords[:5])  # Máximo 5 palavras-chave
            variants.append(keyword_query)

        # Consulta com sinônimos comuns (máximo 1 variação)
        synonyms_map = {
            'servidor': ['funcionário'],
            'licença': ['afastamento'],
            'indenização': ['auxílio'],
            'progressão': ['promoção']
        }

        for original, synonyms in synonyms_map.items():
            if original in query.lower():
                variant = query.lower().replace(original, synonyms[0])
                variants.append(variant)
                break  # Apenas uma substituição

        return list(set(variants))[:3]  # Máximo 3 variações

    async def _execute_pinecone_search(self, query_analysis: Dict) -> List:
        """Executa busca no Pinecone usando as variações da consulta"""
        all_results = []

        # Busca para cada variação da consulta
        for variant in query_analysis['query_variants']:
            try:
                results = self.search_tool.search(variant, top_k=5)
                all_results.extend(results)

                # Pequena pausa para não sobrecarregar
                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.warning(f"Erro na busca para '{variant}': {e}")

        # Remove duplicatas baseado no documento_id
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result.documento_id not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result.documento_id)

        # Ordena por score (melhor primeiro)
        unique_results.sort(key=lambda x: x.score, reverse=True)

        return unique_results[:15]  # Limita a 15 melhores resultados

    async def _categorize_results(self, search_results: List) -> Dict[str, Any]:
        """Categoriza os resultados por relevância e tipo"""

        high_relevance = [r for r in search_results if r.score >= 0.6]  # Reduzido de 0.8 para 0.6
        medium_relevance = [r for r in search_results if 0.4 <= r.score < 0.6]
        low_relevance = [r for r in search_results if 0.3 <= r.score < 0.4]

        # Categoriza por tipo de documento/assunto
        by_topic = {}
        for result in search_results:
            # Extrai tópico do metadata ou título
            topic = self._extract_topic(result)
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(result)

        return {
            'by_relevance': {
                'high': high_relevance,
                'medium': medium_relevance,
                'low': low_relevance
            },
            'by_topic': by_topic,
            'total_results': len(search_results),
            'relevance_distribution': {
                'high': len(high_relevance),
                'medium': len(medium_relevance),
                'low': len(low_relevance)
            }
        }

    def _extract_topic(self, result) -> str:
        """Extrai o tópico principal do resultado"""
        titulo = result.titulo.lower() if result.titulo else ''

        if any(term in titulo for term in ['licença', 'afastamento']):
            return 'licenças_afastamentos'
        elif any(term in titulo for term in ['progressão', 'promoção']):
            return 'progressao_funcional'
        elif any(term in titulo for term in ['indenização', 'auxílio']):
            return 'indenizacoes_auxilios'
        elif any(term in titulo for term in ['aposentadoria', 'abono']):
            return 'aposentadoria_beneficios'
        else:
            return 'outros'

    async def _synthesize_findings(self, query: str, categorized_results: Dict) -> Dict[str, Any]:
        """Sintetiza os achados usando o LLM"""

        high_rel = categorized_results['by_relevance']['high']

        if not high_rel:
            return {
                'synthesis_text': f"Nenhum documento altamente relevante encontrado para '{query}'.",
                'sources_analyzed': 0,
                'synthesis_timestamp': datetime.now().isoformat()
            }

        # Prepara contexto dos documentos mais relevantes para o LLM
        context_docs = []
        for i, doc in enumerate(high_rel[:5]):  # Máximo 5 documentos
            # Tenta diferentes campos de conteúdo
            content = getattr(doc, 'conteudo', '') or getattr(doc, 'content', '')
            content_preview = content[:1500] if content else "Conteúdo não disponível"

            context_docs.append(f"""
DOCUMENTO {i+1}:
Título: {doc.titulo}
Processo: {getattr(doc, 'metadata', {}).get('numero_processo', 'N/A')}
Relevância: {doc.score:.1%}
Conteúdo: {content_preview}
""")

        context_text = '\n'.join(context_docs)

        # Prompt para síntese específica e objetiva
        synthesis_prompt = f"""
Você é um especialista jurídico. Com base nos documentos fornecidos, responda de forma OBJETIVA à pergunta:

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

        try:
            if hasattr(self, 'llm_client') and self.llm_client:
                # Usa o LLM para síntese
                response = self.llm_client.generate_content(synthesis_prompt)
                synthesis_text = response.text.strip()
            else:
                # Fallback sem LLM
                synthesis_text = f"Encontrados {len(high_rel)} documentos relevantes sobre '{query}'. Para resposta específica, consulte os documentos: {', '.join([d.titulo for d in high_rel[:3]])}."
        except Exception as e:
            self.logger.error(f"Erro na síntese com LLM: {e}")
            synthesis_text = f"Encontrados {len(high_rel)} documentos relevantes sobre '{query}'. Para resposta específica, consulte os documentos."

        return {
            'synthesis_text': synthesis_text,
            'sources_analyzed': len(high_rel),
            'synthesis_timestamp': datetime.now().isoformat()
        }

    async def _generate_structured_response(self, query: str, query_analysis: Dict,
                                          categorized_results: Dict, synthesis: Dict) -> Dict[str, Any]:
        """Gera resposta estruturada final"""

        return {
            'executive_summary': synthesis.get('synthesis_text', 'Síntese não disponível'),
            'search_strategy': {
                'original_query': query,
                'keywords_used': query_analysis['keywords'],
                'query_variants': len(query_analysis['query_variants']),
                'search_engine': 'Pinecone + text-embedding-004'
            },
            'findings': {
                'total_documents': categorized_results['total_results'],
                'high_relevance': len(categorized_results['by_relevance']['high']),
                'topics_covered': list(categorized_results['by_topic'].keys()),
                'relevance_distribution': categorized_results['relevance_distribution']
            },
            'top_sources': [
                {
                    'titulo': r.titulo,
                    'score': r.score,
                    'preview': r.conteudo[:150] + '...' if len(r.conteudo) > 150 else r.conteudo
                }
                for r in categorized_results['by_relevance']['high'][:3]
            ]
        }

    def _calculate_confidence(self, categorized_results: Dict) -> float:
        """Calcula nível de confiança nos resultados"""
        high_rel = len(categorized_results['by_relevance']['high'])
        total = categorized_results['total_results']

        if total == 0:
            return 0.0

        # Confiança baseada na proporção de resultados altamente relevantes
        confidence = (high_rel / total) * 100
        return min(confidence, 100.0)

    def _generate_recommendations(self, categorized_results: Dict, confidence: float) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []

        if confidence >= 80:
            recommendations.append("✅ Alta confiança nos resultados encontrados")
        elif confidence >= 60:
            recommendations.append("⚠️ Confiança moderada - considere refinar a busca")
        else:
            recommendations.append("❌ Baixa confiança - recomenda-se busca manual adicional")

        high_rel = len(categorized_results['by_relevance']['high'])
        if high_rel >= 5:
            recommendations.append("📚 Fontes suficientes para análise robusta")
        elif high_rel >= 2:
            recommendations.append("📖 Fontes adequadas para análise básica")
        else:
            recommendations.append("🔍 Poucas fontes relevantes - ampliar busca")

        topics = len(categorized_results['by_topic'])
        if topics >= 3:
            recommendations.append("🎯 Consulta abrange múltiplos aspectos do tema")

        return recommendations
