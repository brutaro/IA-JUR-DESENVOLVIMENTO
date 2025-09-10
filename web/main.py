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
from typing import Dict, Any, Optional, List, Union
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

# Importa o agente de pesquisa jurídica
from src.agents.research_agent import ResearchAgent

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

# Sistema simplificado não precisa de context_manager separado

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
        # Sistema simplificado não precisa de context_manager separado

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
    resposta_completa: Union[str, Dict[str, Any]]  # Suporta tanto texto quanto JSON estruturado
    fontes: int  # Número de fontes encontradas
    principais_fontes: List[str] = []  # Lista das principais fontes
    workflow_id: str
    duracao: float
    timestamp: str
    is_followup: bool = False  # Indica se é uma pergunta de follow-up
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

            # Cria agente de pesquisa jurídica
            orchestrator = ResearchAgent(llm_configs)
            logger.info("✅ Orquestrador inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar orquestrador: {e}")
            raise
    return orchestrator

# Função removida - sistema simplificado gerencia contexto internamente


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
        # Obtém o orquestrador simplificado
        orch = get_orchestrator()

        # Processa a consulta com agente de pesquisa jurídica
        logger.info(f"🔍 Processando consulta: {consulta.pergunta[:100]}...")
        resultado = await orch.process(consulta.pergunta)

        end_time = time.time()
        duracao = end_time - start_time

        # Extrai informações do resultado (mapeia campos do agente de pesquisa jurídica)
        synthesis = resultado.get('synthesis', 'Resposta não disponível')

        # Verifica se a resposta é JSON estruturado
        try:
            import json
            json_response = json.loads(synthesis)

            # Se for JSON válido, usa a estrutura estruturada
            if 'resposta_imediata' in json_response:
                resposta_completa = json_response
                fontes = json_response.get('total_documents', resultado.get('total_documents', 0))
                principais_fontes = json_response.get('principais_fontes', resultado.get('principais_fontes', []))
            else:
                # Fallback para formato antigo
                resposta_completa = synthesis
                fontes = resultado.get('total_documents', 0)
                principais_fontes = resultado.get('principais_fontes', [])

        except (json.JSONDecodeError, TypeError):
            # Se não for JSON válido, usa formato antigo
            resposta_completa = synthesis
            fontes = resultado.get('total_documents', 0)
            principais_fontes = resultado.get('principais_fontes', [])

        workflow_id = f"wf_{int(time.time())}"

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

        # Sistema simplificado gerencia contexto internamente

        # Salva no chat history (mantém compatibilidade)
        # IMPORTANTE: Salva apenas a pergunta original e a resposta completa
        try:
            save_chat_entry(consulta.pergunta, resposta_completa)
        except Exception as e:
            logger.warning(f"Erro ao salvar chat history: {e}")

        # Adiciona informações de contexto à resposta
        response_data = {
            'resposta_completa': resposta_completa,
            'fontes': fontes,
            'principais_fontes': principais_fontes,
            'workflow_id': workflow_id,
            'duracao': duracao,
            'timestamp': datetime.now().isoformat(),
            'is_followup': False
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
        orch = get_orchestrator()
        return {
            "status": "Agente ultra simplificado funcionando",
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
        return {
            "message": "Agente ultra simplificado não tem memória para limpar",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao limpar contexto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao limpar contexto")

@app.get("/api/arquivos-txt")
async def listar_arquivos_txt():
    """Lista os arquivos TXT salvos automaticamente"""
    try:
        import os
        from pathlib import Path

        # Diretório onde os arquivos TXT são salvos
        txt_dir = Path("respostas/respostas_txt")

        if not txt_dir.exists():
            return {"arquivos": []}

        arquivos = []
        for arquivo in txt_dir.glob("*.txt"):
            stat = arquivo.stat()
            arquivos.append({
                "nome": arquivo.name,
                "caminho": str(arquivo),
                "tamanho": stat.st_size,
                "data_modificacao": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "data_criacao": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })

        # Ordena por data de modificação (mais recente primeiro)
        arquivos.sort(key=lambda x: x["data_modificacao"], reverse=True)

        return {"arquivos": arquivos}

    except Exception as e:
        logger.error(f"Erro ao listar arquivos TXT: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar arquivos TXT")

@app.get("/api/download-txt/{nome_arquivo}")
async def download_arquivo_txt(nome_arquivo: str):
    """Download de arquivo TXT específico"""
    try:
        from pathlib import Path
        import os

        # Diretório onde os arquivos TXT são salvos
        txt_dir = Path("respostas/respostas_txt")
        arquivo_path = txt_dir / nome_arquivo

        if not arquivo_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")

        # Lê o conteúdo do arquivo
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        # Retorna o conteúdo para download
        from fastapi.responses import Response
        return Response(
            content=conteudo,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )

    except Exception as e:
        logger.error(f"Erro ao fazer download do arquivo {nome_arquivo}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao fazer download do arquivo")

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
