#!/usr/bin/env python3
"""
Servidor FastAPI Simplificado para Teste
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IA-JUR Simple", version="1.0.0")

class ConsultaRequest(BaseModel):
    pergunta: str

class ConsultaResponse(BaseModel):
    resposta: str
    status: str

@app.get("/")
async def root():
    return {"message": "IA-JUR Simple Server", "status": "running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "message": "Server is running"}

@app.post("/api/consulta", response_model=ConsultaResponse)
async def consulta_simples(consulta: ConsultaRequest):
    """Consulta simplificada para teste"""
    try:
        logger.info(f"Processando: {consulta.pergunta[:50]}...")

        # Resposta simulada
        resposta = f"Resposta para: {consulta.pergunta}"

        return ConsultaResponse(
            resposta=resposta,
            status="success"
        )
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor simples...")
    uvicorn.run(
        "simple_server:app",
        host="127.0.0.1",
        port=8002,
        reload=False,
        log_level="info"
    )
