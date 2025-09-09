#!/usr/bin/env python3
"""
Servidor FastAPI estável com memória
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from contextlib import asynccontextmanager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis globais
orchestrator = None
context_manager = None

def configurar_llms():
    """Configura os LLMs para o agente pesquisador"""
    return {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'api_key': os.getenv('GEMINI_API_KEY'),
        'temperature': 0.1,
        'max_tokens': 4000
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global orchestrator, context_manager

    logger.info("🚀 Iniciando IA-JUR...")

    try:
        # Inicializa ContextManager primeiro (mais rápido)
        logger.info("📝 Inicializando ContextManager...")
        from src.memory.context_manager import ContextManager
        context_manager = ContextManager(max_context_size=10)
        logger.info("✅ ContextManager inicializado")

        # Inicializa orquestrador
        logger.info("🤖 Inicializando Orquestrador...")
        from src.agents.simple_orchestrator import SimpleLegalOrchestrator
        llm_configs = configurar_llms()
        orchestrator = SimpleLegalOrchestrator(llm_configs, output_dir='./respostas')
        logger.info("✅ Orquestrador inicializado")

        yield

    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {str(e)}")
        raise
    finally:
        logger.info("🛑 Finalizando IA-JUR...")

# Cria a aplicação FastAPI
app = FastAPI(
    title="IA-JUR - Agente de Pesquisa Jurídica",
    description="Sistema de pesquisa jurídica com IA e memória contextual",
    version="2.0.0",
    lifespan=lifespan
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ConsultaRequest(BaseModel):
    pergunta: str = Field(..., min_length=1, max_length=2000, description="Pergunta para o agente")

    @field_validator('pergunta')
    @classmethod
    def validate_pergunta(cls, v):
        if not v or not v.strip():
            raise ValueError('Pergunta não pode estar vazia')
        return v.strip()

class ConsultaResponse(BaseModel):
    resumo: str
    resposta_completa: str
    fontes: int
    duracao: float
    workflow_id: str
    timestamp: str
    contexto: Optional[Dict[str, Any]] = None

# Endpoints
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "IA-JUR - Agente de Pesquisa Jurídica",
        "version": "2.0.0",
        "status": "online",
        "features": ["pesquisa_juridica", "memoria_contextual"]
    }

@app.get("/api/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "orchestrator": "active" if orchestrator else "inactive",
        "context_manager": "active" if context_manager else "inactive"
    }

@app.get("/api/context")
async def get_context():
    """Obtém resumo do contexto atual"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="ContextManager não inicializado")

    summary = context_manager.get_context_summary()
    return {
        "context_summary": summary,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.delete("/api/context")
async def clear_context():
    """Limpa o contexto atual"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="ContextManager não inicializado")

    context_manager.clear_context()
    return {"message": "Contexto limpo com sucesso"}

@app.post("/api/consulta", response_model=ConsultaResponse)
async def consulta(consulta: ConsultaRequest):
    """Endpoint principal de consulta com memória contextual"""
    global orchestrator, context_manager

    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")

    if not context_manager:
        raise HTTPException(status_code=503, detail="ContextManager não inicializado")

    start_time = time.time()

    try:
        # Analisa contexto da consulta
        context_info = context_manager.get_context_for_query(consulta.pergunta)

        logger.info(f"🔍 Processando consulta: {consulta.pergunta[:100]}...")
        if context_info['is_followup']:
            logger.info(f"📝 Follow-up detectado (score: {context_info['followup_score']:.2f})")

            # Enriquece a consulta com contexto se for follow-up
            if context_info['relevant_history']:
                contexto_texto = "\n".join([
                    f"Pergunta anterior: {entry['user']}\nResposta: {entry['assistant'][:200]}..."
                    for entry in context_info['relevant_history']
                ])
                consulta_enriquecida = f"""
CONSULTA ATUAL: {consulta.pergunta}

CONTEXTO DAS CONVERSAS ANTERIORES:
{contexto_texto}

Por favor, responda à consulta atual considerando o contexto das conversas anteriores.
"""
                logger.info("📝 Consulta enriquecida com contexto")
            else:
                consulta_enriquecida = consulta.pergunta
        else:
            consulta_enriquecida = consulta.pergunta

        # Chama o orquestrador
        resultado = await orchestrator.process_query(consulta_enriquecida)

        end_time = time.time()
        duracao = end_time - start_time

        # Extrai informações do resultado
        resumo = resultado.get('summary', 'Resumo não disponível')
        resposta_completa = resultado.get('formatted_response', 'Resposta não disponível')
        fontes = resultado.get('sources_found', 0)
        workflow_id = resultado.get('metadata', {}).get('workflow_id', f"wf_{int(time.time())}")

        # Adiciona interação ao contexto
        context_manager.add_interaction(consulta.pergunta, resposta_completa)

        logger.info(f"✅ Consulta processada em {duracao:.2f}s")

        # Prepara resposta
        response_data = {
            "resumo": resumo,
            "resposta_completa": resposta_completa,
            "fontes": fontes,
            "duracao": duracao,
            "workflow_id": workflow_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Adiciona informações de contexto se for follow-up
        if context_info['is_followup']:
            response_data["contexto"] = {
                "is_followup": context_info['is_followup'],
                "followup_score": context_info['followup_score'],
                "relevant_history_count": len(context_info['relevant_history'])
            }

        return ConsultaResponse(**response_data)

    except Exception as e:
        logger.error(f"❌ Erro na consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "stable_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Desabilita reload para evitar travamentos
        log_level="info"
    )
