# Guia de Contribuição

## Como Contribuir

### 1. Configuração do Ambiente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/agente-pesquisa-juridica-v2.0.git
cd agente-pesquisa-juridica-v2.0

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
pip install -r web/requirements.txt

# Configure as variáveis de ambiente
cp config_example.env .env
# Edite o arquivo .env com suas chaves de API
```

### 2. Estrutura do Projeto

```
agente-pesquisa-juridica-v2.0/
├── src/                    # Código fonte principal
│   ├── agents/            # Agentes de IA
│   ├── memory/            # Sistema de memória contextual
│   ├── tools/             # Ferramentas de pesquisa
│   └── ...
├── web/                   # Interface web
│   ├── templates/         # Templates HTML
│   ├── static/           # CSS, JS, imagens
│   └── main.py           # Servidor FastAPI
├── docs/                  # Documentação
├── tests/                 # Testes
└── deploy_github/         # Configurações de deploy
```

### 3. Padrões de Código

- **Python**: Siga PEP 8
- **Type Hints**: Use type hints em todas as funções públicas
- **Docstrings**: Documente classes e funções
- **Logging**: Use logging estruturado
- **Error Handling**: Trate exceções adequadamente

### 4. Processo de Desenvolvimento

1. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. **Faça suas alterações** seguindo os padrões

3. **Teste localmente**:
   ```bash
   # Teste o sistema CLI
   python simple_main.py

   # Teste o servidor web
   cd web && python main.py
   ```

4. **Commit com mensagem clara**:
   ```bash
   git commit -m "feat: adiciona nova funcionalidade X"
   ```

5. **Push e crie Pull Request**

### 5. Tipos de Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Tarefas de manutenção

### 6. Testes

```bash
# Execute os testes
python -m pytest tests/

# Teste específico
python test_followup.py
```

### 7. Deploy

- **Desenvolvimento**: Use o servidor local
- **Produção**: Configure Railway ou similar
- **Documentação**: Atualize README.md e docs/

## Regras de Contribuição

1. **Não quebre** funcionalidades existentes
2. **Mantenha** compatibilidade com a API
3. **Documente** mudanças significativas
4. **Teste** suas alterações
5. **Siga** os padrões de código estabelecidos

## Suporte

Para dúvidas ou problemas:
- Abra uma **Issue** no GitHub
- Consulte a **documentação** em `docs/`
- Verifique os **exemplos** em `examples/`
