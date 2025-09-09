# 🚀 Guia de Uso Rápido - Sistema Simplificado

## 📋 Visão Geral

Este guia fornece instruções rápidas para usar o Sistema de Agentes Jurídicos na versão simplificada.

## 🚀 Início Rápido

### **1. Executar o Sistema**
```bash
python simple_main.py
```

### **2. Menu Principal**
```
🤖 SISTEMA DE AGENTES JURÍDICOS - VERSÃO SIMPLIFICADA
======================================================================

Escolha uma opção:

1. 🔍 Fazer uma pergunta jurídica (Pesquisa)
2. 📊 Ver métricas do sistema
3. ❌ Sair
```

### **3. Fazer uma Consulta**
- **Escolha opção 1**
- **Digite sua pergunta jurídica**
- **Pressione Enter duas vezes para confirmar**
- **Aguarde o processamento (12-15 segundos)**

## 🔍 Exemplos de Consultas

### **Consultas Simples**
```
O DNIT pode pagar ARTs a arquitetos?
```

### **Consultas Detalhadas**
```
O DNIT pode ou deve pagar ARTs a arquitetos? Em quais casos?
```

### **Consultas com Siglas**
```
Qual o entendimento da AGU sobre custeio de ART?
```

## 📊 Entendendo os Resultados

### **Resumo da Pesquisa**
- **Resposta direta** à sua pergunta
- **Informações práticas** e organizadas
- **Citações específicas** de documentos

### **Fontes Consultadas**
- **Número de fontes** encontradas
- **Principais fontes** com relevância
- **Scores de similaridade** (0.75+ = alta relevância)

### **Metadados**
- **Tempo de processamento**
- **ID único** da consulta
- **Timestamps** de início e fim

## 💾 Arquivos Gerados

### **Localização**
```
respostas/respostas_txt/
```

### **Formato do Nome**
```
(Palavras_chave_YYYYMMDD_HHMMSS).txt
```

### **Exemplo**
```
(O_DNIT_pode_pagar_AR_20250811_125523).txt
```

## 🔧 Configuração Necessária

### **Variáveis de Ambiente**
```bash
# Crie um arquivo .env
GEMINI_API_KEY=sua_chave_aqui
PINECONE_API_KEY=sua_chave_aqui
PINECONE_INDEX=seu_indice_aqui
```

### **Dependências**
```bash
pip install google-generativeai pinecone-client python-dotenv
```

## 📈 Métricas do Sistema

### **Acessar Métricas**
- **Escolha opção 2** no menu principal
- **Visualize estatísticas** de uso
- **Monitore performance** do sistema

### **Informações Disponíveis**
- Total de consultas processadas
- Consultas de pesquisa realizadas
- Histórico de uso

## 🎯 Dicas de Uso

### **Para Melhores Resultados**
1. **Seja específico** na sua pergunta
2. **Use termos técnicos** quando apropriado
3. **Inclua contexto** relevante
4. **Uma pergunta por vez** para melhor foco

### **Exemplos de Boas Práticas**
```
✅ BOM: "O DNIT pode pagar ARTs a arquitetos em obras de infraestrutura?"
❌ EVITAR: "Pode pagar?"
```

## 🚨 Solução de Problemas

### **Erro de API Key**
```
❌ Erro: API key do Gemini não encontrada
✅ Solução: Configure GEMINI_API_KEY no arquivo .env
```

### **Erro de Conexão Pinecone**
```
❌ Erro: Falha na conexão com Pinecone
✅ Solução: Verifique PINECONE_API_KEY e PINECONE_INDEX
```

### **Sistema Lento**
```
⏳ Processamento demorado
✅ Solução: Normal (12-15 segundos é o tempo esperado)
```

## 📚 Recursos Adicionais

### **Documentação Técnica**
- **`ARQUITETURA_SISTEMA_SIMPLIFICADO.md`**: Arquitetura detalhada
- **`ESTADO_ATUAL_SISTEMA.md`**: Status e capacidades
- **`SIMPLIFICACAO_SISTEMA.md`**: Detalhes da simplificação

### **Glossário Técnico**
- **24 termos** expandidos automaticamente
- **Siglas jurídicas** resolvidas
- **Contexto técnico** adicionado

## 🔄 Fluxo de Trabalho Típico

### **1. Preparação**
```bash
# Configure variáveis de ambiente
# Instale dependências
# Execute o sistema
```

### **2. Uso Diário**
```bash
# Execute sistema
# Escolha opção 1
# Digite consulta
# Aguarde resultado
# Salve arquivo TXT
```

### **3. Monitoramento**
```bash
# Verifique métricas (opção 2)
# Monitore performance
# Acompanhe uso
```

## 📞 Suporte

### **Problemas Técnicos**
- Verifique arquivo `.env`
- Confirme dependências instaladas
- Teste conexões de API

### **Melhorias**
- Sugira novas funcionalidades
- Reporte bugs encontrados
- Contribua com o projeto

---

**Versão**: 2.0-simplificada
**Última Atualização**: Agosto 2025
**Status**: ✅ Sistema operacional e funcional
