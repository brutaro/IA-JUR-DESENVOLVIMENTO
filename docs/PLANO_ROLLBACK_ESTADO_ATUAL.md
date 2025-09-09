# 🔄 PLANO DE ROLLBACK - ESTADO ATUAL DO SISTEMA

## 📋 Informações do Plano

**Data de Criação**: 13 de Agosto de 2025  
**Versão do Sistema**: 2.0-simplificada-restaurada  
**Status**: ✅ **SISTEMA TOTALMENTE OPERACIONAL**  
**Tipo**: Plano de Rollback (READ-ONLY)  
**Responsável**: Documentação para modificações futuras  

## ⚠️ AVISO IMPORTANTE

**ESTE ARQUIVO É READ-ONLY**  
**NÃO MODIFIQUE ESTE DOCUMENTO**  
**É O PLANO DE ROLLBACK OFICIAL**  

---

## 🎯 Objetivo do Plano de Rollback

Este documento contém **todas as informações necessárias** para restaurar o sistema ao estado atual (totalmente operacional) caso seja necessário após modificações futuras.

## 🔧 Estado Atual Documentado

### **1. Configuração das APIs**

#### **Google Gemini API**
```bash
# Arquivo: .env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

#### **Pinecone Vector Database**
```bash
# Arquivo: .env
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=agentes-juridicos
PINECONE_ENVIRONMENT=us-east-1
```

### **2. Host Personalizado do Pinecone**
```bash
# HOST CRÍTICO - NÃO ALTERAR
CUSTOM_PINECONE_HOST=agentes-juridicos-10b89ab.svc.aped-4627-b74a.pinecone.io
```

### **3. Configurações do LLM**
```python
# Configurações que FUNCIONAM
LLM_CONFIG = {
    'provider': 'gemini',
    'model': 'gemini-2.5-flash',
    'temperature': 0.1,
    'max_tokens': 6000
}
```

### **4. Configurações do Embedding**
```python
# Configurações que FUNCIONAM
EMBEDDING_CONFIG = {
    'model': 'models/text-embedding-004',
    'dimensions': 768,
    'task_type': 'retrieval_query'
}
```

## 📁 Arquivos Críticos para Rollback

### **1. Arquivos Principais (NÃO ALTERAR)**
```
src/tools/pinecone_search_tool.py          # CRÍTICO - Ferramenta Pinecone personalizada
src/agents/research_agent.py               # CRÍTICO - Agente pesquisador
src/agents/simple_orchestrator.py          # CRÍTICO - Orquestrador
simple_main.py                             # CRÍTICO - Interface principal
```

### **2. Arquivos de Configuração (NÃO ALTERAR)**
```
.env                                       # CRÍTICO - Variáveis de ambiente
requirements.txt                           # CRÍTICO - Dependências
```

### **3. Arquivos de Suporte (MANTER)**
```
src/glossary/technical_glossary.py
src/integration/glossary_integration.py
src/preprocessing/query_preprocessor.py
src/postprocessing/query_postprocessor.py
src/agents/base_agent.py
```

## 🔄 Procedimento de Rollback Completo

### **FASE 1: Backup dos Arquivos Atuais**

```bash
# 1. Criar backup completo do estado atual
mkdir -p backup_estado_atual_$(date +%Y%m%d_%H%M%S)

# 2. Backup dos arquivos críticos
cp -r src/ backup_estado_atual_*/src/
cp simple_main.py backup_estado_atual_*/
cp .env backup_estado_atual_*/
cp requirements.txt backup_estado_atual_*/
cp pyproject.toml backup_estado_atual_*/

# 3. Backup da documentação
cp -r docs/ backup_estado_atual_*/docs/
```

### **FASE 2: Restauração dos Arquivos Críticos**

```bash
# 1. Restaurar ferramenta Pinecone personalizada
cp backup_estado_atual_*/src/tools/pinecone_search_tool.py src/tools/

# 2. Restaurar agente pesquisador
cp backup_estado_atual_*/src/agents/research_agent.py src/agents/

# 3. Restaurar orquestrador
cp backup_estado_atual_*/src/agents/simple_orchestrator.py src/agents/

# 4. Restaurar interface principal
cp backup_estado_atual_*/simple_main.py .

# 5. Restaurar configurações
cp backup_estado_atual_*/.env .
cp backup_estado_atual_*/requirements.txt .
```

### **FASE 3: Verificação da Restauração**

```bash
# 1. Testar importações
python -c "import sys; sys.path.append('src'); from tools.pinecone_search_tool import PineconeSearchTool; print('✅ PineconeSearchTool restaurado')"

# 2. Testar agente
python -c "import sys; sys.path.append('src'); from agents.research_agent import UnifiedResearchAgent; print('✅ UnifiedResearchAgent restaurado')"

# 3. Testar orquestrador
python -c "import sys; sys.path.append('src'); from agents.simple_orchestrator import SimpleLegalOrchestrator; print('✅ SimpleLegalOrchestrator restaurado')"

# 4. Testar sistema completo
python test_simple.py
```

## 🚨 Pontos Críticos de Falha

### **1. Host Personalizado do Pinecone**
- **PROBLEMA**: Se o host `agentes-juridicos-10b89ab.svc.aped-4627-b74a.pinecone.io` for alterado
- **SINTOMA**: Erro "Failed to connect" ou "NameResolutionError"
- **SOLUÇÃO**: Restaurar arquivo `src/tools/pinecone_search_tool.py` original

### **2. Configuração do Embedding**
- **PROBLEMA**: Se o modelo `text-embedding-004` for alterado
- **SINTOMA**: Erro "Model not found" ou dimensões incorretas
- **SOLUÇÃO**: Restaurar configuração original no arquivo da ferramenta

### **3. Configuração do LLM**
- **PROBLEMA**: Se o modelo `gemini-2.5-flash` for alterado
- **SINTOMA**: Erro "Model not available" ou respostas inconsistentes
- **SOLUÇÃO**: Restaurar configuração original no arquivo do agente

### **4. Estrutura de Arquivos**
- **PROBLEMA**: Se a estrutura de diretórios for alterada
- **SINTOMA**: Erro "Module not found" ou importação falha
- **SOLUÇÃO**: Restaurar estrutura completa do backup

## 🔍 Diagnóstico de Problemas

### **1. Verificar Status do Pinecone**
```bash
# Teste de conectividade
python test_pinecone_host_override.py

# Resultado esperado: ✅ Conexão bem-sucedida
```

### **2. Verificar Status do LLM**
```bash
# Teste de LLM
python -c "import google.generativeai as genai; print('✅ Gemini disponível')"

# Resultado esperado: ✅ Gemini disponível
```

### **3. Verificar Sistema Completo**
```bash
# Teste do sistema
python test_simple.py

# Resultado esperado: ✅ Sistema funcionando
```

## 📊 Métricas de Sucesso do Rollback

### **1. Conectividade**
- ✅ Pinecone responde (HTTP 200)
- ✅ Host personalizado acessível
- ✅ API key válida

### **2. Funcionalidade**
- ✅ Embeddings gerados (768 dimensões)
- ✅ Busca vetorial funcionando
- ✅ LLM respondendo
- ✅ Sistema processando queries

### **3. Performance**
- ✅ Tempo de embedding: 0.3-1.3s
- ✅ Tempo de busca: 0.6s
- ✅ Tempo total: 12-15s
- ✅ Taxa de sucesso: 100%

## 🛠️ Ferramentas de Rollback

### **1. Scripts de Backup Automático**
```bash
#!/bin/bash
# backup_sistema.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_estado_atual_$DATE"

mkdir -p "$BACKUP_DIR"
cp -r src/ "$BACKUP_DIR"/src/
cp simple_main.py "$BACKUP_DIR"/
cp .env "$BACKUP_DIR"/
cp requirements.txt "$BACKUP_DIR"/
cp pyproject.toml "$BACKUP_DIR"/
cp -r docs/ "$BACKUP_DIR"/docs/

echo "Backup criado em: $BACKUP_DIR"
```

### **2. Scripts de Restauração Automática**
```bash
#!/bin/bash
# restore_sistema.sh
BACKUP_DIR="$1"

if [ -z "$BACKUP_DIR" ]; then
    echo "Uso: $0 <diretorio_backup>"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Diretório de backup não encontrado: $BACKUP_DIR"
    exit 1
fi

echo "Restaurando sistema do backup: $BACKUP_DIR"

cp -r "$BACKUP_DIR"/src/ src/
cp "$BACKUP_DIR"/simple_main.py .
cp "$BACKUP_DIR"/.env .
cp "$BACKUP_DIR"/requirements.txt .
cp "$BACKUP_DIR"/pyproject.toml .

echo "Sistema restaurado. Execute: python test_simple.py"
```

## 📋 Checklist de Rollback

### **Antes de Modificações**
- [ ] Backup completo do sistema atual
- [ ] Documentação do estado atual
- [ ] Teste de funcionamento
- [ ] Identificação de arquivos críticos

### **Durante Modificações**
- [ ] Manter backup acessível
- [ ] Testar cada modificação
- [ ] Documentar mudanças
- [ ] Manter versões anteriores

### **Após Modificações**
- [ ] Teste completo do sistema
- [ ] Verificação de funcionalidades
- [ ] Validação de performance
- [ ] Documentação das mudanças

### **Em Caso de Falha**
- [ ] Identificar problema
- [ ] Executar rollback automático
- [ ] Verificar restauração
- [ ] Documentar incidente

## 🎯 Resumo do Plano de Rollback

### **✅ Estado Atual Documentado**
- Configurações completas das APIs
- Arquivos críticos identificados
- Procedimentos de backup/restore
- Ferramentas de diagnóstico

### **🔄 Procedimento de Rollback**
- Backup automático antes de modificações
- Restauração automática em caso de falha
- Verificação completa após restauração
- Validação de funcionalidades

### **🚨 Pontos de Atenção**
- Host personalizado do Pinecone (CRÍTICO)
- Configurações do LLM (CRÍTICO)
- Estrutura de arquivos (CRÍTICO)
- Dependências Python (CRÍTICO)

---

## 📝 Notas Finais

**ESTE DOCUMENTO É READ-ONLY**  
**NÃO MODIFIQUE ESTE PLANO DE ROLLBACK**  
**É A REFERÊNCIA OFICIAL PARA RESTAURAÇÃO**  

**Última Atualização**: 13 de Agosto de 2025  
**Status**: Sistema totalmente operacional  
**Próximo Passo**: Modificações no agente (com backup)  

**⚠️ IMPORTANTE**: Sempre execute backup antes de modificações!
