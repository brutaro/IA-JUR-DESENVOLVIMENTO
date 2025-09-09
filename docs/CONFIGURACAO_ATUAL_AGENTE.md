# 🔧 Configuração Atual do Agente - Documentação Técnica Completa

## 📋 Informações Gerais

**Data de Criação**: 13 de Agosto de 2025  
**Versão**: 2.0-simplificada-restaurada  
**Status**: ✅ **SISTEMA TOTALMENTE OPERACIONAL**  
**Última Atualização**: Restauração completa do sistema  

## 🏗️ Arquitetura do Sistema Restaurado

### **Diagrama de Alto Nível**
```
┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│   Interface     │    │    Orquestrador      │    │   Agente         │
│   do Usuário    │───▶│    Simplificado      │───▶│   Pesquisador    │
│  (simple_main)  │    │ (simple_orchestrator)│    │ (research_agent) │
└─────────────────┘    └──────────────────────┘    └──────────────────┘
                                │                           │
                                ▼                           ▼
                       ┌─────────────────┐         ┌─────────────────┐
                       │   Glossário     │         │      LLM        │
                       │   Técnico       │         │  (Gemini 2.5)   │
                       └─────────────────┘         └─────────────────┘
                                │                           │
                                ▼                           ▼
                       ┌─────────────────┐         ┌─────────────────┐
                       │   Pinecone      │         │   Resposta      │
                       │ (Host Personalizado)      │   Formatada     │
                       └─────────────────┘         └─────────────────┘
```

## 🔑 Configurações de Chaves e APIs

### **1. Google Gemini API**
```bash
# Arquivo: .env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Configurações do LLM**:
- **Modelo**: `gemini-2.5-flash`
- **Provider**: Google
- **Temperature**: 0.1 (determinístico)
- **Max Tokens**: 6000
- **API Endpoint**: Automático via SDK

### **2. Pinecone Vector Database**
```bash
# Arquivo: .env
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=agentes-juridicos
PINECONE_ENVIRONMENT=us-east-1
```

**Configuração Especial**:
- **Host Personalizado**: `agentes-juridicos-10b89ab.svc.aped-4627-b74a.pinecone.io`
- **Índice**: `agentes-juridicos`
- **Ambiente**: `us-east-1` (configurado mas não usado)
- **Total de Vetores**: 6.967
- **Dimensões**: 768

## 🔍 Sistema de Retrieval do Pinecone

### **1. Implementação Atual**
O sistema usa uma **implementação personalizada** que contorna o SDK padrão do Pinecone devido a problemas de DNS.

### **2. Arquivo Principal**
```python
# src/tools/pinecone_search_tool.py
class PineconeSearchTool:
    def __init__(self):
        # Host personalizado que funciona
        self.custom_host = "agentes-juridicos-10b89ab.svc.aped-4627-b74a.pinecone.io"
        self.api_key = pinecone_api_key
```

### **3. Processo de Retrieval**
```python
def _query_pinecone_custom(self, vector: List[float], top_k: int = 5):
    # URL para query no host personalizado
    query_url = f"https://{self.custom_host}/query"
    
    # Headers necessários
    headers = {
        'Api-Key': self.api_key,
        'Content-Type': 'application/json'
    }
    
    # Payload da query
    payload = {
        'vector': vector,
        'topK': top_k,
        'includeMetadata': True
    }
    
    # Executa query via HTTP POST
    response = requests.post(query_url, headers=headers, json=payload, timeout=30)
```

### **4. Embedding Model**
```python
# Configurações do embedding
self.config = {
    'embedding_model': 'models/text-embedding-004',
    'top_k': 15,
    'similarity_threshold': 0.3,
    'final_result_count': 10,
    'task_type': 'retrieval_query'
}
```

### **5. Fluxo de Retrieval Completo**
```
1. Input Query → Texto da consulta
2. Embedding Generation → text-embedding-004 (768 dimensões)
3. HTTP POST → Host personalizado do Pinecone
4. Vector Search → Busca por similaridade
5. Results Filtering → Threshold 0.3+
6. Metadata Extraction → Metadados dos documentos
7. Response Formatting → Formato padronizado
```

## 🧠 Configuração do LLM (Gemini 2.5)

### **1. Inicialização**
```python
# src/agents/research_agent.py
def _create_llm_instance(self):
    import google.generativeai as genai
    
    api_key = self.llm_config.get('api_key') or os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(self.llm_config.get('model', 'gemini-2.5-flash'))
    return model
```

### **2. Configurações de Prompt**
```python
# Prompt para síntese específica e objetiva
synthesis_prompt = f"""
Você é um especialista jurídico. Com base nos documentos fornecidos, responda de forma OBJETIVA à pergunta:

"{query}"

DOCUMENTOS DISPONÍVEIS:
{context_text}

INSTRUÇÕES OBRIGATÓRIAS:
1. Responda de forma NATURAL e DIRETA, como um especialista jurídico
2. Extraia informações ESPECÍFICAS dos documentos
3. Cite as fontes usando o TÍTULO real da nota técnica
4. Use linguagem clara e profissional, sem expressões informais
5. Organize as informações de forma lógica e prática
6. Não use [DOCUMENTO X] - use sempre as referências reais
7. Não use expressões como "colega", "amigo", "prezado" - seja direto e objetivo
"""
```

## 🔄 Fluxo de Processamento Completo

### **1. Inicialização do Sistema**
```python
# simple_main.py
def configurar_llms():
    default_config = {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'api_key': os.getenv('GEMINI_API_KEY'),
        'temperature': 0.1,
        'max_tokens': 4000
    }
    
    llm_configs = {
        'default': default_config,
        'research': {
            **default_config,
            'temperature': 0.1,
            'max_tokens': 6000
        }
    }
```

### **2. Orquestração**
```python
# src/agents/simple_orchestrator.py
class SimpleLegalOrchestrator:
    def __init__(self, llm_configs, output_dir=None):
        self._initialize_research_agent()
        self.glossary = GlossaryIntegration()
        self.metrics = {'total_queries': 0, 'research_queries': 0}
```

### **3. Processamento da Query**
```python
async def process_query(self, query: str):
    # 1. Cria contexto
    context = AgentContext(session_id=workflow_id, ...)
    
    # 2. Processa com glossário
    processed_query = self.glossary.processar_query_completa(query)
    
    # 3. Executa pesquisa
    result = await self._execute_research(query, context)
    
    # 4. Formata resposta
    formatted_result = self._format_research_response(result, query)
    
    # 5. Salva em TXT
    txt_file_path = self._save_response_to_txt(formatted_result, workflow_id, "research")
```

## 📁 Estrutura de Arquivos Atual

### **Arquivos Principais**
```
├── simple_main.py                          # Interface principal
├── src/
│   ├── agents/
│   │   ├── base_agent.py                  # Classe base
│   │   ├── research_agent.py              # Agente pesquisador
│   │   └── simple_orchestrator.py         # Orquestrador
│   ├── tools/
│   │   └── pinecone_search_tool.py        # Ferramenta Pinecone (personalizada)
│   ├── glossary/
│   │   └── technical_glossary.py          # Glossário técnico
│   ├── integration/
│   │   └── glossary_integration.py        # Integração do glossário
│   ├── preprocessing/
│   │   └── query_preprocessor.py          # Pré-processamento
│   └── postprocessing/
│       └── query_postprocessor.py         # Pós-processamento
```

### **Arquivos de Configuração**
```
├── .env                                    # Variáveis de ambiente
├── requirements.txt                        # Dependências Python
└── pyproject.toml                         # Configuração do projeto
```

## 📊 Métricas e Performance

### **1. Performance Atual**
- **Tempo de Embedding**: 0.3-1.3 segundos
- **Tempo de Busca**: 0.6 segundos
- **Tempo Total**: 12-15 segundos
- **Taxa de Sucesso**: 100%

### **2. Capacidades do Sistema**
- **Base de Conhecimento**: 6.967 documentos
- **Dimensões dos Vetores**: 768
- **Threshold de Similaridade**: 0.3+
- **Resultados por Busca**: 5-15 documentos
- **Scores Típicos**: 60-80%

## 🚨 Pontos Críticos da Configuração

### **1. Host Personalizado do Pinecone**
- **CRÍTICO**: O sistema depende do host `agentes-juridicos-10b89ab.svc.aped-4627-b74a.pinecone.io`
- **Motivo**: Problemas de DNS com hosts padrão do Pinecone
- **Solução Implementada**: Bypass do SDK via HTTP direto

### **2. Configuração do Embedding**
- **Modelo**: `text-embedding-004` (Google)
- **Dimensões**: 768 (fixo)
- **Task Type**: `retrieval_query`

### **3. Configuração do LLM**
- **Modelo**: `gemini-2.5-flash`
- **Temperature**: 0.1 (determinístico)
- **Max Tokens**: 6000

## 🔧 Dependências e Versões

### **1. Python**
- **Versão**: 3.10.13
- **Arquitetura**: x86_64 (macOS)

### **2. Pacotes Principais**
```bash
google-generativeai>=0.3.0    # Gemini API
pinecone-client>=2.2.4        # Pinecone SDK (não usado atualmente)
python-dotenv>=1.0.0          # Variáveis de ambiente
requests                       # HTTP requests (para Pinecone personalizado)
numpy                          # Processamento numérico
```

### **3. Estrutura de Diretórios**
```
agente-pesquisa-juridica-v2.0/
├── .venv/                    # Ambiente virtual
├── src/                      # Código fonte
├── docs/                     # Documentação
├── respostas/                # Respostas geradas
├── origem/                   # Documentos originais
└── testes/                   # Testes do sistema
```

## ✅ Status de Funcionamento

### **1. Componentes Operacionais**
- ✅ **Interface Principal** (`simple_main.py`)
- ✅ **Orquestrador** (`simple_orchestrator.py`)
- ✅ **Agente Pesquisador** (`research_agent.py`)
- ✅ **Ferramenta Pinecone** (versão personalizada)
- ✅ **LLM Gemini** (2.5 Flash)
- ✅ **Glossário Técnico**
- ✅ **Sistema de Arquivos TXT**

### **2. Funcionalidades Testadas**
- ✅ **Conexão Pinecone** (host personalizado)
- ✅ **Geração de Embeddings** (text-embedding-004)
- ✅ **Busca Vetorial** (similaridade)
- ✅ **Síntese com LLM** (Gemini 2.5)
- ✅ **Formatação de Respostas**
- ✅ **Salvamento em TXT**
- ✅ **Métricas do Sistema**

## 🎯 Resumo da Configuração

O sistema está configurado com uma **arquitetura simplificada e robusta** que:

1. **Usa host personalizado** do Pinecone para contornar problemas de DNS
2. **Implementa retrieval direto** via HTTP para máxima confiabilidade
3. **Utiliza Gemini 2.5 Flash** para síntese de alta qualidade
4. **Mantém simplicidade** com apenas 3 componentes principais
5. **Preserva funcionalidade completa** de pesquisa jurídica

**Status**: ✅ **SISTEMA TOTALMENTE OPERACIONAL E DOCUMENTADO**

---

**Última Atualização**: 13 de Agosto de 2025  
**Responsável**: Restauração do sistema  
**Versão**: 2.0-simplificada-restaurada
