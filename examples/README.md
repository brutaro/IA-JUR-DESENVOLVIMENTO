# Exemplo de Uso - IA-JUR

## Configuração Rápida

1. Copie o arquivo de configuração:
```bash
cp examples/.env.example .env
```

2. Configure suas chaves de API no arquivo `.env`

3. Instale as dependências:
```bash
pip install -r requirements.txt
pip install -r web/requirements.txt
```

4. Execute o servidor:
```bash
cd web && python main.py
```

5. Acesse: http://localhost:8001

## Testando a Memória Contextual

1. Faça uma pergunta: "O servidor tem direito a pagamento de diárias para realizar perícia médica?"
2. Faça um follow-up: "Pode me explicar mais a fundo sobre isso?"
3. Observe como o sistema detecta automaticamente o follow-up e enriquece a resposta com contexto!
