# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - 2025-09-09

### Adicionado
- Sistema de memória contextual avançado com ContextManager
- Detecção automática de follow-ups com score de relevância
- Enriquecimento automático de consultas com contexto histórico
- API endpoints para gerenciamento de contexto (`/api/context`)
- Frontend web completo com interface moderna
- Persistência de memória em arquivo JSON
- Sistema de logging estruturado
- Configuração de CORS para desenvolvimento
- Validação de entrada com Pydantic
- Lifespan handlers para inicialização/shutdown

### Melhorado
- Arquitetura do servidor FastAPI com padrões modernos
- Sistema de pesquisa jurídica com IA Gemini 2.5 Flash
- Integração com Pinecone para busca semântica
- Processamento de consultas com contexto histórico
- Interface web responsiva e intuitiva

### Corrigido
- Erros de importação (SimpleOrchestrator -> SimpleLegalOrchestrator)
- Problemas de travamento do servidor
- Configuração de paths para módulos Python
- Inicialização sequencial de componentes

### Técnico
- Implementação de thread-safe operations
- Sistema de janela deslizante para memória (10 interações)
- Padrões de follow-up com regex patterns
- Configuração de ambiente com variáveis de ambiente
- Estrutura de projeto organizada com separação de responsabilidades

## [1.0.0] - 2025-08-13

### Adicionado
- Sistema básico de pesquisa jurídica
- Integração com Pinecone e Gemini
- Interface CLI simples
- Processamento de documentos jurídicos
