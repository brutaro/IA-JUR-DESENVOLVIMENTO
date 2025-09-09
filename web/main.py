#!/usr/bin/env python3
"""
IA-JUR - Sistema de Pesquisa Jurídica Inteligente
Backend FastAPI integrado com o agente de pesquisa existente
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Adiciona o diretório raiz ao path para importar os módulos do agente
sys.path.insert(0, str(Path(__file__).parent.parent))

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import uvicorn
import logging

# Importa o agente de pesquisa existente
from src.agents.simple_orchestrator import SimpleLegalOrchestrator
from src.memory.context_manager import ContextManager

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração do chat memory
CHAT_HISTORY_PATH = Path(__file__).parent.parent / ".cursor" / "memory" / "chat_history.json"

def load_chat_history() -> list:
    """Carrega o histórico de chat do arquivo JSON"""
    try:
        if CHAT_HISTORY_PATH.exists():
            with open(CHAT_HISTORY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Erro ao carregar chat history: {e}")
        return []

def save_chat_entry(user_message: str, assistant_response: str) -> None:
    """Salva uma nova entrada no chat history"""
    try:
        history = load_chat_history()

        # Adiciona nova entrada
        new_entry = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now().isoformat()
        }
        history.append(new_entry)

        # Mantém apenas as últimas 100 entradas
        if len(history) > 100:
            history = history[-100:]

        # Salva no arquivo
        CHAT_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CHAT_HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        logger.info(f"Chat entry salva: {len(history)} entradas no histórico")
    except Exception as e:
        logger.error(f"Erro ao salvar chat entry: {e}")

# Instância do orquestrador (inicializada lazy)
orchestrator = None

# Instância do gerenciador de contexto
context_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler para inicialização e cleanup"""
    # Startup
    logger.info("🚀 IA-JUR iniciando...")
    logger.info(f"📁 Diretório de trabalho: {os.getcwd()}")
    logger.info("🔧 Verificando dependências...")

    try:
        # Testa a inicialização do orquestrador
        get_orchestrator()

        # Inicializa o gerenciador de contexto
        get_context_manager()

        logger.info("✅ Sistema IA-JUR iniciado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        logger.warning("⚠️  O sistema pode não funcionar corretamente")

    yield

    # Shutdown
    logger.info("👋 Encerrando IA-JUR...")

# Configuração do FastAPI
app = FastAPI(
    title="IA-JUR",
    description="Sistema de Pesquisa Jurídica Inteligente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de templates e arquivos estáticos
# Usa caminhos absolutos para evitar problemas de diretório
current_dir = Path(__file__).parent
templates = Jinja2Templates(directory=str(current_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")

# Modelos Pydantic
class ConsultaRequest(BaseModel):
    """Modelo para requisição de consulta jurídica"""
    pergunta: str = Field(..., min_length=10, max_length=2000, description="Pergunta jurídica a ser processada")

    @field_validator('pergunta')
    @classmethod
    def validate_pergunta(cls, v):
        """Valida se a pergunta não está vazia e tem conteúdo relevante"""
        if not v or not v.strip():
            raise ValueError('Pergunta não pode estar vazia')
        if len(v.strip()) < 10:
            raise ValueError('Pergunta deve ter pelo menos 10 caracteres')
        return v.strip()

class ConsultaResponse(BaseModel):
    resumo: str
    resposta_completa: str
    fontes: int  # Número de fontes encontradas
    workflow_id: str
    duracao: float
    timestamp: str
    contexto: Optional[Dict[str, Any]] = None  # Informações de contexto

class MetricasResponse(BaseModel):
    total_consultas: int
    consultas_pesquisa: int
    tempo_medio: float
    fontes_totais: int
    uptime: str

# Variáveis globais para métricas
metrics = {
    "total_consultas": 0,
    "consultas_pesquisa": 0,
    "tempo_medio": 0.0,
    "fontes_totais": 0,
    "start_time": time.time(),
    "consultas_tempo": []
}

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

def get_orchestrator():
    """Inicializa o orquestrador de forma lazy"""
    global orchestrator
    if orchestrator is None:
        try:
            # Configura LLMs
            llm_configs = configurar_llms()

            # Cria orquestrador com configuração correta
            orchestrator = SimpleLegalOrchestrator(llm_configs, output_dir='./respostas')
            logger.info("✅ Orquestrador inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar orquestrador: {e}")
            raise
    return orchestrator

def get_context_manager():
    """Inicializa o gerenciador de contexto de forma lazy"""
    global context_manager
    if context_manager is None:
        try:
            # Cria gerenciador de contexto
            context_manager = ContextManager(
                max_context_size=10,
                memory_file=CHAT_HISTORY_PATH
            )
            logger.info("✅ ContextManager inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ContextManager: {e}")
            raise
    return context_manager


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal do IA-JUR"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/consulta", response_model=ConsultaResponse)
async def processar_consulta(consulta: ConsultaRequest):
    """
    Processa uma consulta jurídica usando o agente existente
    """
    global metrics

    if not consulta.pergunta.strip():
        raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")

    start_time = time.time()

    try:
        # Obtém o orquestrador e gerenciador de contexto
        orch = get_orchestrator()
        ctx_manager = get_context_manager()

        # Analisa contexto da consulta
        context_info = ctx_manager.get_context_for_query(consulta.pergunta)

        # Processa a consulta
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

        # Chama o orquestrador existente (é assíncrono)
        resultado = await orch.process_query(consulta_enriquecida)

        end_time = time.time()
        duracao = end_time - start_time

        # Extrai informações do resultado (mapeia campos corretos)
        resumo = resultado.get('summary', 'Resumo não disponível')
        resposta_completa = resultado.get('formatted_response', 'Resposta não disponível')
        fontes = resultado.get('sources_found', 0)  # Número real de fontes encontradas
        workflow_id = resultado.get('metadata', {}).get('workflow_id', f"wf_{int(time.time())}")

        # Atualiza métricas
        metrics["total_consultas"] += 1
        metrics["consultas_pesquisa"] += 1
        metrics["fontes_totais"] += fontes  # fontes é um número, não uma lista
        metrics["consultas_tempo"].append(duracao)

        # Calcula tempo médio (últimas 10 consultas)
        if len(metrics["consultas_tempo"]) > 10:
            metrics["consultas_tempo"] = metrics["consultas_tempo"][-10:]
        metrics["tempo_medio"] = sum(metrics["consultas_tempo"]) / len(metrics["consultas_tempo"])

        logger.info(f"✅ Consulta processada em {duracao:.2f}s")

        # Adiciona interação ao contexto (não bloqueia a resposta)
        try:
            ctx_manager.add_interaction(consulta.pergunta, resposta_completa)
        except Exception as e:
            logger.warning(f"Erro ao adicionar ao contexto: {e}")

        # Salva no chat history (mantém compatibilidade)
        try:
            save_chat_entry(consulta.pergunta, resposta_completa)
        except Exception as e:
            logger.warning(f"Erro ao salvar chat history: {e}")

        # Adiciona informações de contexto à resposta
        response_data = {
            'resumo': resumo,
            'resposta_completa': resposta_completa,
            'fontes': fontes,
            'workflow_id': workflow_id,
            'duracao': duracao,
            'timestamp': datetime.now().isoformat()
        }

        # Adiciona contexto se for follow-up (versão simplificada)
        if context_info.get('is_followup', False):
            response_data['contexto'] = {
                'is_followup': True,
                'followup_score': context_info.get('followup_score', 0.0),
                'context_size': context_info.get('context_window_size', 0)
            }

        return ConsultaResponse(**response_data)

    except Exception as e:
        end_time = time.time()
        duracao = end_time - start_time

        logger.error(f"❌ Erro ao processar consulta: {e}")

        # Retorna erro estruturado
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar consulta: {str(e)}"
        )

@app.get("/api/metricas", response_model=MetricasResponse)
async def obter_metricas():
    """
    Retorna métricas do sistema em tempo real
    """
    global metrics

    uptime = time.time() - metrics["start_time"]
    uptime_hours = int(uptime // 3600)
    uptime_minutes = int((uptime % 3600) // 60)
    uptime_str = f"{uptime_hours}h {uptime_minutes}m"

    return MetricasResponse(
        total_consultas=metrics["total_consultas"],
        consultas_pesquisa=metrics["consultas_pesquisa"],
        tempo_medio=round(metrics["tempo_medio"], 2),
        fontes_totais=metrics["fontes_totais"],
        uptime=uptime_str
    )

@app.get("/api/health")
async def health_check():
    """
    Verificação de saúde do sistema
    """
    try:
        # Testa se o orquestrador está funcionando
        orch = get_orchestrator()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "orchestrator": "operational",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }

@app.get("/api/info")
async def system_info():
    """
    Informações do sistema
    """
    return {
        "sistema": "IA-JUR",
        "versao": "1.0.0",
        "descricao": "Sistema de Pesquisa Jurídica Inteligente",
        "tecnologia": "FastAPI + Python + IA Gemini",
        "integracao": "Agente de Pesquisa Jurídica",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/chat-history")
async def get_chat_history():
    """
    Retorna o histórico de chat
    """
    try:
        history = load_chat_history()
        return {
            "total_entries": len(history),
            "history": history[-10:],  # Últimas 10 entradas
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter chat history: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter histórico de chat")

@app.get("/api/context")
async def get_context_info():
    """
    Retorna informações do contexto atual
    """
    try:
        ctx_manager = get_context_manager()
        context_summary = ctx_manager.get_context_summary()
        recent_queries = ctx_manager.get_recent_queries(limit=5)

        return {
            "context_summary": context_summary,
            "recent_queries": recent_queries,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter contexto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter informações de contexto")

@app.delete("/api/context")
async def clear_context():
    """
    Limpa o contexto de conversação
    """
    try:
        ctx_manager = get_context_manager()
        ctx_manager.clear_context()

        return {
            "message": "Contexto limpo com sucesso",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao limpar contexto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao limpar contexto")

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições"""
    start_time = time.time()

    # Processa a requisição
    response = await call_next(request)

    # Calcula duração
    duration = time.time() - start_time

    # Log da requisição
    logger.info(f"📝 {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")

    return response

# Tratamento de erros personalizado
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler para páginas não encontradas"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Página não encontrada",
            "path": request.url.path,
            "message": "A página solicitada não existe no IA-JUR"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler para erros internos"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "path": request.url.path,
            "message": "Ocorreu um erro interno no IA-JUR"
        }
    )

if __name__ == "__main__":
    logger.info("🚀 Iniciando IA-JUR...")
    logger.info(f"📁 Diretório: {os.getcwd()}")
    logger.info("🌐 Servidor web iniciando em http://localhost:8001")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
