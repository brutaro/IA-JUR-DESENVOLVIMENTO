# 🌐 IA-JUR - Frontend Web

Sistema de Pesquisa Jurídica Inteligente com interface web moderna e responsiva.

## 🚀 **Funcionalidades**

### **Interface Web**
- ✅ **Design moderno** com gradientes e animações
- ✅ **Responsivo** para desktop e mobile
- ✅ **Navegação intuitiva** entre seções
- ✅ **Tema IA-JUR** personalizado

### **Pesquisa Jurídica**
- ✅ **Formulário de consulta** intuitivo
- ✅ **Processamento em tempo real** com loading
- ✅ **Resultados estruturados** (resumo + resposta completa)
- ✅ **Metadados** (tempo, fontes, workflow ID)

### **Histórico e Métricas**
- ✅ **Histórico de consultas** persistente (localStorage)
- ✅ **Métricas em tempo real** (consultas, tempo médio, fontes)
- ✅ **Botão de atualização** para métricas
- ✅ **Ações** (repetir consulta, copiar pergunta)

### **Download e Exportação**
- ✅ **Download TXT** das respostas
- ✅ **Formatação estruturada** com metadados
- ✅ **Nome de arquivo** com timestamp

## 🏗️ **Arquitetura**

### **Frontend**
```
web/
├── static/
│   ├── css/style.css          # Estilos IA-JUR
│   └── js/app.js             # JavaScript principal
├── templates/
│   └── index.html            # Template HTML
├── main.py                   # Backend FastAPI
├── requirements.txt          # Dependências web
├── start_ia_jur.py          # Script de inicialização
└── README.md                # Este arquivo
```

### **Integração**
- **Backend FastAPI** integrado com agente existente
- **API REST** para consultas e métricas
- **Templates Jinja2** para renderização
- **Arquivos estáticos** servidos pelo FastAPI

## 🛠️ **Instalação e Uso**

### **1. Instalar Dependências Web**
```bash
pip install -r web/requirements.txt
```

### **2. Iniciar Sistema Web**
```bash
# Opção 1: Script de inicialização (recomendado)
python web/start_ia_jur.py

# Opção 2: Direto do diretório web
cd web
python main.py

# Opção 3: Uvicorn direto
cd web
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **3. Acessar Interface**
- **Interface Web:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔌 **APIs Disponíveis**

### **POST /api/consulta**
Processa consulta jurídica
```json
{
  "pergunta": "O DNIT pode ou deve pagar ARTs a arquitetos?"
}
```

### **GET /api/metricas**
Retorna métricas do sistema
```json
{
  "total_consultas": 10,
  "consultas_pesquisa": 10,
  "tempo_medio": 2.5,
  "fontes_totais": 45,
  "uptime": "2h 30m"
}
```

### **GET /api/health**
Verificação de saúde do sistema

### **GET /api/info**
Informações do sistema

## 🎨 **Personalização**

### **Cores e Tema**
- **Primária:** #667eea (azul)
- **Secundária:** #764ba2 (roxo)
- **Gradiente:** Linear 135° azul → roxo
- **Cards:** Branco com transparência e sombras

### **Responsividade**
- **Desktop:** Layout em grid com múltiplas colunas
- **Mobile:** Layout em coluna única com navegação vertical
- **Breakpoint:** 768px

## 🔒 **Segurança**

- **Validação de entrada** com Pydantic
- **Tratamento de erros** estruturado
- **Logging** de todas as requisições
- **Middleware** para monitoramento

## 📱 **Compatibilidade**

### **Navegadores**
- ✅ Chrome/Chromium (recomendado)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

### **Dispositivos**
- ✅ Desktop (Windows, macOS, Linux)
- ✅ Mobile (iOS, Android)
- ✅ Tablet

## 🚨 **Troubleshooting**

### **Erro: "Dependência não encontrada"**
```bash
pip install -r web/requirements.txt
```

### **Erro: "Sistema principal não funcionando"**
Verifique se o CLI está funcionando:
```bash
python simple_main.py
```

### **Erro: "Porta 8000 em uso"**
Mude a porta no arquivo `main.py` ou mate o processo:
```bash
lsof -ti:8000 | xargs kill -9
```

### **Erro: "Template não encontrado"**
Verifique se está executando do diretório raiz:
```bash
python web/start_ia_jur.py
```

## 🔄 **Desenvolvimento**

### **Modo Debug**
```bash
cd web
uvicorn main:app --reload --log-level debug
```

### **Estrutura de Desenvolvimento**
- **CSS:** Modificar `static/css/style.css`
- **JavaScript:** Modificar `static/js/app.js`
- **HTML:** Modificar `templates/index.html`
- **Backend:** Modificar `main.py`

### **Hot Reload**
- **Frontend:** Atualização automática com `--reload`
- **CSS/JS:** Recarregar página manualmente
- **Templates:** Reiniciar servidor

## 📊 **Monitoramento**

### **Logs em Tempo Real**
```bash
tail -f logs/ia_jur.log  # Se configurado
```

### **Métricas de Performance**
- Tempo de resposta por consulta
- Total de consultas processadas
- Fontes consultadas
- Uptime do sistema

## 🌟 **Recursos Avançados**

### **Histórico Local**
- Persistência em localStorage
- Limite de 50 consultas
- Ações de repetir e copiar

### **Notificações**
- Sucesso, erro e informação
- Posicionamento fixo
- Auto-remoção após 3s

### **Navegação por Teclado**
- **Ctrl+Enter:** Processar consulta
- **Tab:** Navegação entre elementos
- **Enter:** Ativar botões

---

## 📞 **Suporte**

Para suporte técnico ou dúvidas sobre o IA-JUR:
- **Documentação:** Ver arquivos na pasta `docs/`
- **Issues:** Reportar problemas no repositório
- **Desenvolvimento:** Ver código fonte e comentários

---

**IA-JUR v1.0.0** - Sistema de Pesquisa Jurídica Inteligente 🚀
