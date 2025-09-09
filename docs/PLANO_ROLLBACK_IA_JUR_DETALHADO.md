# 🔄 PLANO DE ROLLBACK DETALHADO - IA-JUR

## 📋 **RESUMO EXECUTIVO**

Este documento detalha o plano completo de rollback para o sistema IA-JUR, permitindo reverter qualquer implementação futura que possa falhar e retornar ao estado atual funcional.

## 🎯 **OBJETIVO DO ROLLBACK**

Restaurar o sistema ao estado **IA-JUR v1.0.0** funcional, caso implementações futuras causem problemas ou falhas no sistema.

## 📊 **ESTADO ATUAL (PONTO DE ROLLBACK)**

### **Versão:** IA-JUR v1.0.0
### **Data:** 13 de Agosto de 2025
### **Status:** ✅ Totalmente funcional
### **Funcionalidades:** 100% operacionais

## 🗂️ **ARQUIVOS CRÍTICOS PARA ROLLBACK**

### **1. Sistema Web IA-JUR**
```
web/
├── main.py                        # Backend FastAPI funcional
├── start_ia_jur.py               # Script de inicialização
├── requirements.txt               # Dependências web
├── static/css/style.css          # Estilos funcionais
├── static/js/app.js              # JavaScript funcional
├── templates/index.html          # Template HTML funcional
└── README.md                     # Documentação web
```

### **2. Sistema Principal (CLI)**
```
src/                              # Código fonte original
├── agents/
│   ├── base_agent.py
│   ├── research_agent.py
│   └── simple_orchestrator.py
├── tools/
│   └── pinecone_search_tool.py  # Versão customizada funcional
└── [outros módulos]

simple_main.py                    # CLI original funcional
.env                              # Configurações funcionais
requirements.txt                  # Dependências originais
```

### **3. Documentação Atualizada**
```
docs/
├── IMPLEMENTACAO_IA_JUR_COMPLETA.md    # Este documento
├── PLANO_ROLLBACK_IA_JUR_DETALHADO.md  # Este arquivo
├── ESTADO_ATUAL_SISTEMA.md             # Status atual
├── CONFIGURACAO_ATUAL_AGENTE.md        # Configurações atuais
└── [outros documentos]
```

## 🔄 **PROCESSO DE ROLLBACK AUTOMATIZADO**

### **1. Script de Rollback Automático**
```bash
#!/bin/bash
# rollback_ia_jur.sh

echo "🔄 INICIANDO ROLLBACK DO IA-JUR"
echo "=================================="

# Verifica se o backup existe
if [ ! -d "$1" ]; then
    echo "❌ Diretório de backup não encontrado: $1"
    echo "💡 Uso: ./rollback_ia_jur.sh backup_estado_atual_YYYYMMDD_HHMMSS"
    exit 1
fi

BACKUP_DIR="$1"
echo "📁 Restaurando de: $BACKUP_DIR"

# Cria backup do estado atual antes do rollback
CURRENT_BACKUP="backup_antes_rollback_$(date +%Y%m%d_%H%M%S)"
echo "📦 Criando backup do estado atual: $CURRENT_BACKUP"
mkdir -p "$CURRENT_BACKUP"

# Backup dos arquivos críticos atuais
echo "  📦 Copiando sistema web atual..."
cp -r web/ "$CURRENT_BACKUP/"

echo "  📦 Copiando código fonte atual..."
cp -r src/ "$CURRENT_BACKUP/"

echo "  📦 Copiando arquivos principais..."
cp simple_main.py "$CURRENT_BACKUP/"
cp .env "$CURRENT_BACKUP/"
cp requirements.txt "$CURRENT_BACKUP/"

echo "  📦 Copiando documentação atual..."
cp -r docs/ "$CURRENT_BACKUP/"

# Restaura arquivos do backup
echo "🔄 Restaurando arquivos do backup..."

echo "  📥 Restaurando sistema web..."
rm -rf web/
cp -r "$BACKUP_DIR/web/" ./

echo "  📥 Restaurando código fonte..."
rm -rf src/
cp -r "$BACKUP_DIR/src/" ./

echo "  📥 Restaurando arquivos principais..."
cp "$BACKUP_DIR/simple_main.py" ./
cp "$BACKUP_DIR/.env" ./
cp "$BACKUP_DIR/requirements.txt" ./

echo "  📥 Restaurando documentação..."
rm -rf docs/
cp -r "$BACKUP_DIR/docs/" ./

# Verifica integridade
echo "🔍 Verificando integridade da restauração..."

if [ -f "web/main.py" ] && [ -f "simple_main.py" ] && [ -f ".env" ]; then
    echo "✅ Restauração concluída com sucesso!"
    echo "📁 Backup do estado anterior: $CURRENT_BACKUP"
    echo "📁 Estado restaurado de: $BACKUP_DIR"
else
    echo "❌ Erro na restauração!"
    echo "🔄 Restaurando estado anterior..."
    cp -r "$CURRENT_BACKUP/"* ./
    echo "✅ Estado anterior restaurado"
    exit 1
fi

echo ""
echo "🔄 ROLLBACK CONCLUÍDO!"
echo "📋 Próximos passos:"
echo "   1. Testar CLI: python simple_main.py"
echo "   2. Testar Web: python web/start_ia_jur.py"
echo "   3. Verificar funcionalidades"
```

### **2. Script de Verificação Pós-Rollback**
```bash
#!/bin/bash
# verificar_rollback.sh

echo "🔍 VERIFICANDO INTEGRIDADE PÓS-ROLLBACK"
echo "========================================="

# Verifica arquivos críticos
echo "📁 Verificando arquivos críticos..."

CRITICAL_FILES=(
    "web/main.py"
    "web/start_ia_jur.py"
    "web/static/css/style.css"
    "web/static/js/app.js"
    "web/templates/index.html"
    "src/agents/simple_orchestrator.py"
    "src/agents/research_agent.py"
    "src/tools/pinecone_search_tool.py"
    "simple_main.py"
    ".env"
    "requirements.txt"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - FALTANDO!"
        exit 1
    fi
done

# Verifica dependências
echo ""
echo "🔧 Verificando dependências..."
if command -v python &> /dev/null; then
    echo "  ✅ Python disponível"
else
    echo "  ❌ Python não encontrado"
    exit 1
fi

# Testa CLI
echo ""
echo "🧪 Testando CLI..."
if python -c "import src.agents.simple_orchestrator" 2>/dev/null; then
    echo "  ✅ Importação do orquestrador funcionando"
else
    echo "  ❌ Erro na importação do orquestrador"
    exit 1
fi

# Testa Web
echo ""
echo "🌐 Testando sistema web..."
if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "  ✅ Dependências web instaladas"
else
    echo "  ❌ Dependências web não encontradas"
    echo "  💡 Execute: pip install -r web/requirements.txt"
    exit 1
fi

echo ""
echo "✅ VERIFICAÇÃO CONCLUÍDA - SISTEMA FUNCIONAL!"
```

## 🚨 **CENÁRIOS DE ROLLBACK**

### **Cenário 1: Falha na Implementação Web**
**Sintomas:**
- Erro 500 na API
- Interface não carrega
- JavaScript não funciona

**Ações:**
1. Parar servidor web
2. Executar rollback automático
3. Verificar integridade
4. Reiniciar sistema

### **Cenário 2: Falha na Integração com Agente**
**Sintomas:**
- Erro "Orquestrador não inicializado"
- Consultas falhando
- Sistema web funcionando, mas sem processamento

**Ações:**
1. Verificar logs do orquestrador
2. Restaurar arquivos do agente
3. Verificar configurações LLM
4. Testar CLI primeiro

### **Cenário 3: Falha nas Dependências**
**Sintomas:**
- Erro de importação
- Módulos não encontrados
- Versões incompatíveis

**Ações:**
1. Restaurar requirements.txt original
2. Reinstalar dependências
3. Verificar versões Python
4. Testar ambiente virtual

### **Cenário 4: Falha na Configuração**
**Sintomas:**
- Erro de conexão Pinecone
- API keys inválidas
- Variáveis de ambiente corrompidas

**Ações:**
1. Restaurar .env original
2. Verificar conectividade
3. Testar chaves API
4. Validar configurações

## 📋 **CHECKLIST DE ROLLBACK**

### **✅ Pré-Rollback**
- [ ] Sistema parado (web + CLI)
- [ ] Backup do estado atual criado
- [ ] Usuários notificados
- [ ] Logs salvos

### **✅ Durante Rollback**
- [ ] Arquivos web restaurados
- [ ] Código fonte restaurado
- [ ] Configurações restauradas
- [ ] Documentação restaurada

### **✅ Pós-Rollback**
- [ ] Verificação de integridade
- [ ] Teste do CLI
- [ ] Teste do sistema web
- [ ] Validação de funcionalidades
- [ ] Notificação de sucesso

## 🔧 **PROCEDIMENTOS MANUAIS DE ROLLBACK**

### **1. Rollback Parcial (Apenas Web)**
```bash
# Restaura apenas o sistema web
rm -rf web/
cp -r backup_estado_atual_20250813_094350/web/ ./

# Verifica
ls -la web/
```

### **2. Rollback Parcial (Apenas Agente)**
```bash
# Restaura apenas o código do agente
rm -rf src/
cp -r backup_estado_atual_20250813_094350/src/ ./

# Verifica
python -c "import src.agents.simple_orchestrator"
```

### **3. Rollback de Configurações**
```bash
# Restaura apenas configurações
cp backup_estado_atual_20250813_094350/.env ./
cp backup_estado_atual_20250813_094350/requirements.txt ./

# Verifica
cat .env | grep -E "(GEMINI|PINECONE)"
```

## 📊 **MONITORAMENTO PÓS-ROLLBACK**

### **1. Métricas de Saúde**
- **Uptime:** Tempo desde o rollback
- **Consultas:** Número de consultas processadas
- **Erros:** Taxa de erro pós-rollback
- **Performance:** Tempo médio de resposta

### **2. Logs de Sistema**
```bash
# Monitorar logs em tempo real
tail -f logs/ia_jur.log  # Se configurado

# Verificar métricas via API
curl http://localhost:8001/api/health
curl http://localhost:8001/api/metricas
```

### **3. Testes de Funcionalidade**
```bash
# Teste CLI
python simple_main.py

# Teste Web
python web/start_ia_jur.py

# Teste API
curl -X POST http://localhost:8001/api/consulta \
  -H "Content-Type: application/json" \
  -d '{"pergunta":"teste rollback"}'
```

## 🚀 **RECUPERAÇÃO E OTIMIZAÇÃO**

### **1. Análise Pós-Rollback**
- **Identificar causa raiz** da falha
- **Documentar lições aprendidas**
- **Atualizar procedimentos** de rollback
- **Melhorar monitoramento**

### **2. Otimizações de Segurança**
- **Backup automático** mais frequente
- **Validação pré-implementação**
- **Ambiente de staging** para testes
- **Rollback incremental** para mudanças grandes

### **3. Documentação Atualizada**
- **Procedimentos revisados** baseados na experiência
- **Checklists atualizados** com novos cenários
- **Scripts melhorados** com validações adicionais
- **Treinamento da equipe** nos novos procedimentos

## 📞 **CONTATOS DE EMERGÊNCIA**

### **Equipe Técnica**
- **Desenvolvedor Principal:** Responsável pelo sistema
- **DevOps:** Infraestrutura e deploy
- **QA:** Testes e validação

### **Escalação**
1. **Nível 1:** Desenvolvedor principal
2. **Nível 2:** Equipe técnica
3. **Nível 3:** Gerência de projeto

## 📋 **RESUMO EXECUTIVO DO ROLLBACK**

### **Objetivo**
Restaurar o sistema IA-JUR ao estado funcional v1.0.0 em caso de falhas futuras.

### **Estratégia**
- **Rollback automático** via scripts
- **Verificação de integridade** pós-restauração
- **Testes funcionais** para validação
- **Monitoramento contínuo** pós-recuperação

### **Resultado Esperado**
Sistema 100% funcional com:
- ✅ CLI operacional
- ✅ Interface web funcionando
- ✅ Agente de pesquisa operacional
- ✅ Integração Pinecone funcionando
- ✅ LLM Gemini respondendo consultas

---

## 🔄 **EXECUÇÃO DO ROLLBACK**

### **Comando de Rollback Automático:**
```bash
./rollback_ia_jur.sh backup_estado_atual_20250813_094350
```

### **Comando de Verificação:**
```bash
./verificar_rollback.sh
```

### **Backup de Segurança:**
```bash
./backup_sistema.sh
```

---

**IA-JUR v1.0.0** - Plano de Rollback Detalhado 🔄
**Data de Criação:** 13 de Agosto de 2025
**Status:** ✅ Sistema Funcional - Rollback Preparado
**Última Atualização:** 13 de Agosto de 2025
