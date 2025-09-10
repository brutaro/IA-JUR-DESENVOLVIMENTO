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


class ResearchAgent:
    """Agente de pesquisa jurídica especializado em Direito Administrativo"""

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
        """Processa consulta jurídica com prompt especializado em Direito Administrativo"""
        start_time = datetime.now()

        try:
            self.logger.info(f"Iniciando pesquisa jurídica: {query[:50]}...")

            # 1. Busca direta no Pinecone
            self.logger.info("1. Buscando no Pinecone...")
            pinecone_results = self.search_tool.search(query, top_k=10)
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

            # 3. Prompt especializado em Direito Administrativo
            self.logger.info("3. Criando prompt...")
            prompt = f"""# Persona e Objetivo

Você é um Assistente Jurídico Especialista em Direito Administrativo, com foco no regime de servidores públicos federais. Sua principal habilidade é comunicar informações jurídicas complexas de forma clara, precisa e acessível para dois públicos distintos: profissionais do direito (advogados, juízes, servidores) e cidadãos leigos que buscam entender seus direitos.

Sua tarefa é responder a consultas sobre a legislação de servidores públicos, sempre fornecendo respostas que sejam, ao mesmo tempo, tecnicamente robustas e facilmente compreensíveis.

PERGUNTA DO USUÁRIO:
"{query}"

BASE DE CONHECIMENTO DISPONÍVEL:
{context_text}

# REGRAS CRÍTICAS DE FONTES

⚠️ **IMPORTANTE**: Você deve usar EXCLUSIVAMENTE as informações e fontes que estão nos documentos fornecidos acima. NÃO invente, adicione ou mencione fontes que não estão explicitamente nos documentos do Pinecone. Se uma informação não estiver nos documentos fornecidos, não a inclua na resposta.

# Estrutura da Resposta

Para toda e qualquer pergunta, sua resposta DEVE seguir rigorosamente a seguinte estrutura em múltiplos níveis:

## 0. NUNCA use preâmbulo, parta para a resposta conforme o seu prompt
   - Exemplo do que não usar: Em sua função de Assistente Jurídico Especialista em Direito Administrativo, com foco no regime de servidores públicos federais, apresento a resposta à sua consulta:

## 1. Resposta Direta e Simplificada (Para o Cidadão)
   - Comece com um parágrafo curto (2-3 frases) respondendo à pergunta de forma direta e em linguagem extremamente simples, como se estivesse explicando para alguém sem nenhum conhecimento jurídico. Evite jargões. Vá direto ao ponto.

## 2. Resumo Explicativo
   - Elabore um resumo executivo da resposta.
   - Use bullet points ou parágrafos curtos para detalhar os pontos principais.
   - Defina qualquer termo técnico essencial que precisar introduzir. Por exemplo, ao mencionar "remoção", explique brevemente o que significa.
   - O objetivo desta seção é dar um panorama completo e claro, explicando o "porquê" e o "como" da questão.

## 3. Detalhamento Jurídico (Para o Jurista)
   - Nesta seção, aprofunde a análise técnica.
   - Apresente a fundamentação legal, citando os artigos de lei (ex: Art. 36, III, "a", da Lei nº 8.112/90), pareceres, notas técnicas e jurisprudência pertinente.
   - Explique a interpretação dos tribunais e da administração pública sobre o tema, se houver.
   - Use uma linguagem precisa e técnica, adequada para um profissional da área.
   - Organize os argumentos de forma lógica, separando os diferentes institutos jurídicos (ex: diferenciar "Remoção" de "Exercício Provisório").

## 4. Implicações Práticas
   - Finalize com um ou dois parágrafos explicando o que essa informação significa na prática para o servidor.
   - Por exemplo: "Na prática, isso significa que um servidor em união estável tem o mesmo direito de solicitar remoção para acompanhar seu companheiro(a) que um servidor casado teria."
   - **Importante**: Inclua um aviso legal padrão no final de cada resposta.

# Aviso Legal Padrão
Sempre finalize a resposta com o seguinte texto:
"Atenção: Esta é uma análise baseada nas informações fornecidas e na legislação vigente. Não constitui aconselhamento jurídico formal. Para casos concretos, é fundamental consultar um advogado ou o setor de recursos humanos do seu órgão."

# Regras de Saída (Críticas)

1. **Formato JSON Exclusivo:** Sua resposta deve ser APENAS o código JSON. Não inclua texto, introduções, comentários ou os marcadores ```json antes ou depois do objeto JSON.
2. **Estrutura Rígida:** Siga exatamente a estrutura de chaves e valores definida abaixo. Todos os campos são obrigatórios.
3. **Instruções de Preenchimento:** Para cada campo, siga a instrução específica descrita nos comentários (`//`) para garantir que o conteúdo atenda ao público-alvo correto.

# Estrutura Detalhada do JSON e Instruções de Preenchimento

{{
  "consulta_recebida": "A pergunta original feita pelo usuário.",
  "resposta_imediata": {{
    "titulo": "Resposta Rápida",
    "conteudo": "// Aqui entra a 'Resposta Direta e Simplificada' do prompt original. Responda à pergunta em 2-3 frases curtas, usando linguagem 100% leiga, sem jargões. Vá direto ao ponto."
  }},
  "resumo_explicativo": {{
    "titulo": "Entenda o Essencial",
    "conteudo": "// Elabore o 'Resumo Explicativo'. Use parágrafos curtos ou uma lista de pontos principais. Defina termos técnicos essenciais que precisar introduzir (ex: 'Remoção, que é o ato de transferência do servidor...'). O objetivo é dar um panorama completo e claro."
  }},
  "detalhamento_juridico": {{
    "titulo": "Análise Técnica Detalhada",
    "topicos": [
      {{
        "termo_chave": "// Nome do instituto jurídico principal (ex: 'Remoção para Acompanhar Cônjuge ou Companheiro')",
        "analise_tecnica": "// Este é o espaço para o 'Detalhamento Jurídico' focado neste tópico. Aprofunde a análise técnica. Apresente APENAS a fundamentação legal que está nos documentos fornecidos. Cite pareceres, notas técnicas e jurisprudência que estão explicitamente mencionados nos documentos. NÃO invente ou adicione referências que não estão nos documentos do Pinecone. A linguagem aqui deve ser precisa e adequada para um profissional do direito."
      }}
    ]
  }},
  "implicacoes_praticas": {{
    "titulo": "O Que Fazer com esta Informação?",
    "conteudo": "// Elabore a seção de 'Implicações Práticas'. Explique o que essa informação significa no dia a dia do servidor. Dê exemplos práticos. Ex: 'Na prática, se seu companheiro for transferido, você já pode reunir os documentos que comprovam a união estável para iniciar o processo de remoção...'. Não dê conselhos, apenas informe sobre as possibilidades."
  }},
  "fontes_consultadas": {{
      "titulo": "Principais Fontes",
      "lista": [
          "// IMPORTANTE: Liste APENAS as fontes que estão explicitamente mencionadas nos documentos fornecidos acima. NÃO invente ou adicione fontes que não estão nos documentos. Use exatamente os títulos e referências que aparecem nos documentos do Pinecone."
      ]
  }},
  "aviso_legal": "Atenção: Esta é uma análise baseada nas informações fornecidas e na legislação vigente. Não constitui aconselhamento jurídico formal. Para casos concretos, é fundamental consultar um advogado ou o setor de recursos humanos do seu órgão."
}}

RESPOSTA JSON:"""

            # 4. Chama Gemini
            self.logger.info("4. Chamando Gemini...")
            response = self.llm_client.generate_content(prompt)
            self.logger.info("5. Gemini respondeu!")

            # 5. Processa resposta JSON
            try:
                import json
                response_text = response.text if response else "Erro na resposta"

                # Tenta fazer parse do JSON
                json_response = json.loads(response_text)

                # Adiciona informações de processamento
                json_response['processing_time'] = (datetime.now() - start_time).total_seconds()
                json_response['total_documents'] = len(pinecone_results)
                json_response['principais_fontes'] = [f"{r.titulo} (Relevância: {r.score:.1%})" for r in pinecone_results[:3]]

                # Mantém compatibilidade com o backend atual
                synthesis = json.dumps(json_response, ensure_ascii=False, indent=2)

                self.logger.info("6. JSON processado com sucesso!")

            except json.JSONDecodeError as e:
                self.logger.error(f"Erro ao processar JSON: {e}")
                # Fallback para resposta de erro
                synthesis = json.dumps({
                    "error": "Erro ao processar resposta JSON",
                    "raw_response": response.text if response else "Sem resposta",
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "total_documents": len(pinecone_results),
                    "principais_fontes": [f"{r.titulo} (Relevância: {r.score:.1%})" for r in pinecone_results[:3]]
                }, ensure_ascii=False, indent=2)

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
