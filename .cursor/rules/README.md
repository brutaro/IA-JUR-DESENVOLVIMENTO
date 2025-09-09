# Cursor Rules Structure

Esta é a estrutura organizada das Cursor Rules do projeto agente-pesquisa-juridica-v2.0.

## Estrutura de Diretórios

```
.cursor/rules/
├── core/                    # Core foundational rules
│   ├── base-agentic.mdc    # Agentic workflow patterns
│   └── base-devops.mdc     # AI-driven DevOps standards
│
├── framework/              # Framework-specific rules
│   ├── python-standards.mdc      # Python coding standards
│   └── fastapi-patterns.mdc      # FastAPI implementation patterns
│
├── domain/                 # Domain-specific rules
│   ├── rag-processing.mdc           # RAG document processing standards
│   └── pinecone-config.mdc          # Pinecone configuration standards
│
├── security/              # Security rules
│   ├── security.mdc       # Universal security standards
│   └── secure-mcp-usage.mdc  # MCP security guidelines
│
└── patterns/              # Advanced patterns
    └── (vazio - para futuras patterns avançadas)
```

## Descrição das Rules

### Core Rules
- **base-agentic.mdc**: Comportamento fundamental do agente, regras de desenvolvimento e preservação do sistema
- **base-devops.mdc**: Stack tecnológico, configurações e padrões de DevOps

### Framework Rules
- **python-standards.mdc**: Padrões de código Python, formatação e boas práticas
- **fastapi-patterns.mdc**: Padrões específicos para desenvolvimento FastAPI

### Domain Rules
- **rag-processing.mdc**: Processamento de documentos RAG, chunking e metadados
- **pinecone-config.mdc**: Configurações específicas do Pinecone

### Security Rules
- **security.mdc**: Princípios universais de desenvolvimento seguro
- **secure-mcp-usage.mdc**: Diretrizes de segurança para uso do MCP

## Como Usar

As rules são carregadas automaticamente pelo Cursor IDE. Cada arquivo `.mdc` contém regras específicas para sua área de atuação, mantendo a organização e facilitando a manutenção.

## Manutenção

- **Máximo 50 linhas** por rule para manter concisão
- **Seja específico** ao invés de genérico
- **Organize por domínio** para facilitar localização
- **Mantenha consistência** na nomenclatura e estrutura
