# 🌐 Sistema de Agentes Jurídicos - Versão Web

## 📋 Visão Geral

Sistema de pesquisa jurídica inteligente com frontend web e API para deploy na Railway. Focado no agente pesquisador, desenvolvido para máxima simplicidade e acessibilidade web. O sistema utiliza inteligência artificial para responder consultas jurídicas com base em uma base de conhecimento especializada.

## 🎯 Características Principais

- **🌐 Frontend Web**: Interface web moderna e responsiva
- **🚀 API Railway**: Deploy automatizado na plataforma Railway
- **🔍 Agente Pesquisador Inteligente**: Processa consultas jurídicas usando LLM (Gemini 2.5 Flash)
- **📊 Busca Vetorial**: Integração com Pinecone para busca semântica avançada
- **📚 Glossário Técnico**: Expansão automática de termos jurídicos ambíguos
- **💾 Salvamento Automático**: Respostas salvas em arquivos TXT com metadados
- **🎨 Interface Dupla**: Web + CLI para máxima flexibilidade

## 🏗️ Arquitetura

```
🌐 Frontend Web → API Railway → simple_orchestrator.py → research_agent.py → LLM → Resposta
👤 CLI Interface → simple_main.py → simple_orchestrator.py → research_agent.py → LLM → Resposta
```

### **Componentes Principais**

- **`simple_main.py`**: Interface principal do usuário
- **`simple_orchestrator.py`**: Orquestrador simplificado
- **`research_agent.py`**: Agente pesquisador (componente principal)
- **`base_agent.py`**: Classe base para agentes

## 🚀 Como Usar

### **1. Instalação**
```bash
# Clone o repositório
git clone [URL_DO_REPOSITORIO]
cd agente-pesquisa-juridica-web

# Instale as dependências
pip install -r requirements.txt
```

### **2. Configuração**
```bash
# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API
```

### **3. Execução**
```bash
python simple_main.py
```

### **4. Menu do Sistema**
```
🤖 SISTEMA DE AGENTES JURÍDICOS - VERSÃO SIMPLIFICADA
======================================================================

Escolha uma opção:

1. 🔍 Fazer uma pergunta jurídica (Pesquisa)
2. 📊 Ver métricas do sistema
3. ❌ Sair
```

## 🔧 Configurações

### **LLM (Gemini 2.5 Flash)**
- **Modelo**: gemini-2.5-flash
- **Temperature**: 0.1 (determinístico)
- **Max Tokens**: 6000 para pesquisa

### **Integrações**
- **Pinecone**: Busca vetorial com text-embedding-004
- **Glossário Técnico**: 24 termos jurídicos organizados
- **Processamento**: Pré e pós-processamento de queries

## 📁 Estrutura do Projeto

```
agente-pesquisa-juridica-web/
├── simple_main.py                 # Interface CLI principal
├── web/                           # Frontend web
│   ├── static/                    # Arquivos estáticos
│   ├── templates/                 # Templates HTML
│   └── app.py                     # Aplicação Flask/FastAPI
├── api/                           # API para Railway
│   ├── main.py                    # Endpoint principal
│   ├── routes/                    # Rotas da API
│   └── requirements.txt           # Dependências da API
├── src/
│   ├── agents/
│   │   ├── base_agent.py         # Classe base
│   │   ├── simple_orchestrator.py # Orquestrador simplificado
│   │   └── research_agent.py     # Agente pesquisador
│   ├── glossary/
│   │   └── technical_glossary.py # Glossário técnico
│   ├── tools/
│   │   └── pinecone_search_tool.py # Ferramenta de busca
│   ├── preprocessing/
│   │   └── query_preprocessor.py # Pré-processamento
│   └── postprocessing/
│       └── query_postprocessor.py # Pós-processamento
├── respostas/
│   └── respostas_txt/            # Arquivos TXT gerados
├── docs/                          # Documentação
└── backup_agents/                 # Backup dos agentes removidos
```

## 📊 Funcionalidades

### **✅ Implementadas**
- Pesquisa jurídica inteligente
- Busca vetorial no Pinecone
- Expansão automática de termos
- Respostas estruturadas e profissionais
- Salvamento automático em TXT
- Métricas de uso do sistema

### **❌ Não Disponíveis (Sistema Simplificado)**
- Triagem automática de documentos
- Análise específica de precedentes
- Geração de notas técnicas completas
- Workflow multi-estágio

## 🧪 Testes

### **Teste Básico**
```bash
# Teste de importação
python -c "from src.agents.simple_orchestrator import SimpleLegalOrchestrator; print('✅ OK')"

# Teste do agente pesquisador
python -c "from src.agents.research_agent import UnifiedResearchAgent; print('✅ OK')"
```

### **Teste Completo**
```bash
python simple_main.py
# Escolha opção 1 e faça uma consulta
```

## 📈 Performance

- **Tempo de Resposta**: 12-15 segundos (média)
- **Precisão da Busca**: Scores 0.75+ (alta relevância)
- **Fontes Encontradas**: 5-10 documentos por consulta
- **Qualidade da Resposta**: Profissional e estruturada

## 🔍 Exemplo de Uso

### **Consulta de Exemplo**
```
O DNIT pode pagar ARTs a arquitetos?
```

### **Resposta Gerada**
- Análise jurídica completa
- Citação de fontes específicas
- Recomendações práticas
- Arquivo TXT com metadados

## 📚 Documentação Técnica

- **`docs/SIMPLIFICACAO_SISTEMA.md`**: Detalhes da simplificação
- **`docs/ESTADO_ATUAL_SISTEMA.md`**: Estado atual do sistema
- **`docs/GLOSSARIO_TECNICO_IMPLEMENTADO.md`**: Documentação do glossário

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Teste o sistema
5. Envie um pull request

## 📞 Suporte

- **Issues**: Use o sistema de issues do GitHub
- **Documentação**: Consulte a pasta `docs/`
- **Backup**: Agentes removidos estão em `backup_agents/`

## 📄 Licença

Este projeto está sob a licença [INSERIR_LICENÇA].

---

**Versão**: 2.0-simplificada
**Status**: ✅ Sistema operacional e funcional
**Última Atualização**: Agosto 2025
