#!/usr/bin/env python3
"""
IA-JUR - Sistema de Pesquisa Jurídica Inteligente
Backend FastAPI integrado com o agente de pesquisa existente
"""

import os
import sys
import time
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from collections import deque, defaultdict

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

# Módulo de memória por sessão - 10 iterações por sessão
session_memories = defaultdict(lambda: deque(maxlen=10))

# Rate limiting para evitar sobrecarga (baseado no MCP Memory Service)
last_context_update = defaultdict(float)
CONTEXT_UPDATE_COOLDOWN = 2.0  # 2 segundos entre atualizações de contexto

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

# Funções do módulo de memória por sessão
def add_to_memory(session_id: str, pergunta: str, resposta: Union[str, Dict[str, Any]]):
    """Adiciona uma interação à memória da conversa da sessão"""
    try:
        session_memories[session_id].append({
            'pergunta': pergunta,
            'resposta': resposta,
            'timestamp': datetime.now().isoformat()
        })
        logger.info(f"Memória da sessão {session_id[:8]} atualizada: {len(session_memories[session_id])}/10 interações")
    except Exception as e:
        logger.error(f"Erro ao adicionar à memória: {e}")

def get_context(session_id: str):
    """Retorna o contexto atual da conversa da sessão"""
    return list(session_memories[session_id])

def is_followup(session_id: str) -> bool:
    """Verifica se é uma pergunta de follow-up na sessão"""
    return len(session_memories[session_id]) > 0

def clear_memory(session_id: str = None):
    """Limpa a memória da conversa (sessão específica ou todas)"""
    if session_id:
        session_memories[session_id].clear()
        logger.info(f"Memória da sessão {session_id[:8]} limpa")
    else:
        session_memories.clear()
        logger.info("Todas as memórias de sessão limpas")

def format_context_for_agent(context: List[Dict], current_question: str) -> str:
    """Formata o contexto de forma otimizada baseado no MCP Memory Service"""
    if not context:
        return ""

    # Detecta tópicos da pergunta atual para filtrar contexto relevante
    current_topics = extract_topics(current_question)

    # Filtra apenas interações relevantes (últimas 3 + relevantes por tópico)
    relevant_interactions = filter_relevant_context(context, current_topics)

    if not relevant_interactions:
        return ""

    # Formato compacto e eficiente
    context_text = "\n\n🧠 **Contexto da Conversa**\n"

    for interaction in relevant_interactions[-3:]:  # Máximo 3 interações
        pergunta = interaction.get('pergunta', '')
        resposta = interaction.get('resposta', '')

        # Extrai apenas o essencial da resposta
        if isinstance(resposta, dict) and 'resposta_imediata' in resposta:
            resposta_texto = resposta.get('resposta_imediata', {}).get('conteudo', '')[:100]
        else:
            resposta_texto = str(resposta)[:100]

        context_text += f"• **P**: {pergunta}\n"
        context_text += f"  **R**: {resposta_texto}...\n\n"

    context_text += "Use este contexto para responder de forma consistente e contextualizada.\n"

    return context_text

def extract_topics(question: str) -> List[str]:
    """Extrai tópicos principais da pergunta para filtragem de contexto"""
    question_lower = question.lower()
    topics = []

    # Palavras-chave jurídicas comuns
    legal_keywords = {
        'art': ['art', 'anotação', 'responsabilidade', 'técnica'],
        'rrt': ['rrt', 'registro', 'responsabilidade'],
        'trt': ['trt', 'termo', 'responsabilidade'],
        'servidor': ['servidor', 'público', 'federal', 'estadual'],
        'dnit': ['dnit', 'departamento', 'infraestrutura'],
        'crea': ['crea', 'conselho', 'engenharia', 'arquitetura'],
        'pagamento': ['pagamento', 'custeio', 'taxa', 'valor'],
        'cargo': ['cargo', 'função', 'atribuição', 'competência']
    }

    for topic, keywords in legal_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            topics.append(topic)

    return topics

def filter_relevant_context(context: List[Dict], current_topics: List[str]) -> List[Dict]:
    """Filtra contexto relevante baseado nos tópicos atuais"""
    if not current_topics:
        return context[-2:]  # Retorna apenas as últimas 2 se não há tópicos específicos

    relevant = []

    # Prioriza interações com tópicos similares
    for interaction in context:
        pergunta = interaction.get('pergunta', '').lower()
        if any(topic in pergunta for topic in current_topics):
            relevant.append(interaction)

    # Se não encontrou tópicos similares, pega as últimas 2
    if not relevant:
        relevant = context[-2:]

    return relevant

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
    session_id: Optional[str] = Field(None, description="ID da sessão para memória contextual")

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

    # Gera ou usa session_id
    session_id = consulta.session_id or str(uuid.uuid4())

    start_time = time.time()

    try:
        # Obtém o orquestrador simplificado
        orch = get_orchestrator()

        # Obtém contexto da sessão
        context = get_context(session_id)
        is_followup_question = is_followup(session_id)

        # Formata pergunta com contexto se houver (otimizado com rate limiting)
        pergunta_com_contexto = consulta.pergunta
        current_time = time.time()

        if context and is_followup_question:
            # Rate limiting para evitar sobrecarga
            if current_time - last_context_update[session_id] > CONTEXT_UPDATE_COOLDOWN:
                context_text = format_context_for_agent(context, consulta.pergunta)
                if context_text:  # Só adiciona se há contexto relevante
                    pergunta_com_contexto = consulta.pergunta + context_text
                    last_context_update[session_id] = current_time
                    logger.info(f"📝 Consulta com contexto otimizado: {len(context)} interações, {len(context_text)} chars")
            else:
                logger.info(f"⏱️ Rate limiting ativo para sessão {session_id[:8]}")

        # Processa a consulta com agente de pesquisa jurídica
        logger.info(f"🔍 Processando consulta: {consulta.pergunta[:100]}...")
        resultado = await orch.process(pergunta_com_contexto)

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
            else:
                # Fallback para formato antigo
                resposta_completa = synthesis
                fontes = resultado.get('total_documents', 0)

        except (json.JSONDecodeError, TypeError):
            # Se não for JSON válido, usa formato antigo
            resposta_completa = synthesis
            fontes = resultado.get('total_documents', 0)

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

        # Adiciona à memória da conversa da sessão
        add_to_memory(session_id, consulta.pergunta, resposta_completa)

        # Obtém contexto atualizado
        context_atualizado = get_context(session_id)

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
            'workflow_id': workflow_id,
            'duracao': duracao,
            'timestamp': datetime.now().isoformat(),
            'is_followup': is_followup_question,
            'session_id': session_id,
            'contexto': {
                'memoria_atual': len(session_memories[session_id]),
                'total_interacoes': len(session_memories[session_id]),
                'sessao': session_id[:8]
            }
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
async def get_context_info(session_id: Optional[str] = None):
    """
    Retorna informações do contexto atual
    """
    try:
        if not session_id:
            return {
                "status": "Módulo de memória por sessão ativo",
                "total_sessoes": len(session_memories),
                "sessoes_ativas": list(session_memories.keys())[:5],  # Primeiras 5 sessões
                "timestamp": datetime.now().isoformat()
            }

        context = get_context(session_id)
        return {
            "status": "Módulo de memória ativo",
            "session_id": session_id,
            "memoria_atual": len(session_memories[session_id]),
            "max_interacoes": 10,
            "contexto": context,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter contexto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter informações de contexto")

@app.delete("/api/context")
async def clear_context(session_id: Optional[str] = None):
    """
    Limpa o contexto de conversação (sessão específica ou todas)
    """
    try:
        clear_memory(session_id)
        if session_id:
            return {
                "message": f"Memória da sessão {session_id[:8]} limpa com sucesso",
                "session_id": session_id,
                "memoria_atual": 0,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "message": "Todas as memórias de sessão limpas com sucesso",
                "total_sessoes_limpas": len(session_memories),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Erro ao limpar contexto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao limpar contexto")

@app.get("/api/memory")
async def get_memory_info(session_id: Optional[str] = None):
    """
    Retorna informações detalhadas da memória
    """
    try:
        if not session_id:
            return {
                "total_sessoes": len(session_memories),
                "sessoes_ativas": [
                    {
                        "session_id": sid[:8],
                        "interacoes": len(mem),
                        "memoria_cheia": len(mem) >= 10
                    }
                    for sid, mem in list(session_memories.items())[:10]
                ],
                "timestamp": datetime.now().isoformat()
            }

        context = get_context(session_id)
        return {
            "session_id": session_id,
            "total_interacoes": len(session_memories[session_id]),
            "max_interacoes": 10,
            "memoria_cheia": len(session_memories[session_id]) >= 10,
            "interacoes": context,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter informações da memória: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter informações da memória")

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
