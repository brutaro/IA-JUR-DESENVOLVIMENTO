#!/usr/bin/env python3
"""
Servidor FastAPI simplificado para teste
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from contextlib import asynccontextmanager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis globais
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global orchestrator

    logger.info("🚀 Iniciando IA-JUR...")
    logger.info(f"📁 Diretório: {Path(__file__).parent}")

    try:
        # Importa e inicializa o orquestrador
        from src.agents.simple_orchestrator import SimpleOrchestrator
        orchestrator = SimpleOrchestrator()
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
    description="Sistema de pesquisa jurídica com IA",
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

# Endpoints
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "IA-JUR - Agente de Pesquisa Jurídica",
        "version": "2.0.0",
        "status": "online"
    }

@app.get("/api/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "orchestrator": "active" if orchestrator else "inactive"
    }

@app.post("/api/consulta", response_model=ConsultaResponse)
async def consulta(consulta: ConsultaRequest):
    """Endpoint principal de consulta"""
    global orchestrator

    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")

    start_time = time.time()

    try:
        logger.info(f"🔍 Processando consulta: {consulta.pergunta[:100]}...")

        # Chama o orquestrador
        resultado = await orchestrator.process_query(consulta.pergunta)

        end_time = time.time()
        duracao = end_time - start_time

        # Extrai informações do resultado
        resumo = resultado.get('summary', 'Resumo não disponível')
        resposta_completa = resultado.get('formatted_response', 'Resposta não disponível')
        fontes = resultado.get('sources_found', 0)
        workflow_id = resultado.get('metadata', {}).get('workflow_id', f"wf_{int(time.time())}")

        logger.info(f"✅ Consulta processada em {duracao:.2f}s")

        return ConsultaResponse(
            resumo=resumo,
            resposta_completa=resposta_completa,
            fontes=fontes,
            duracao=duracao,
            workflow_id=workflow_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    except Exception as e:
        logger.error(f"❌ Erro na consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
