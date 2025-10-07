# Projeto: API de Gestão de Estoques com FastAPI

Esta API foi desenvolvida para consolidar regras de negócio de estoque, permitindo o registro de entradas e saídas, cálculo de saldo, controle de estoque mínimo e operações compostas como vendas e devoluções.

## Como Executar a Aplicação

1.  **Pré-requisitos**:
    *   Python 3.8+
    *   `pip` (gerenciador de pacotes do Python)

2.  **Clone o repositório**:
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-do-repositorio>
    ```

3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o servidor**:
    A partir do diretório raiz do projeto (`projeto-estoque`), execute o comando:
    ```bash
    uvicorn app.main:app --reload
    ```
    O servidor estará disponível em `http://127.0.0.1:8000`.

5.  **Acesse a documentação interativa**:
    Para ver todas as rotas e testá-las, acesse um dos seguintes links no seu navegador:
    *   **Swagger UI**: `http://127.0.0.1:8000/docs`
    *   **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Decisão sobre Saldo Negativo

**A API, por padrão, está configurada para BLOQUEAR saldo negativo.**

Essa decisão foi tomada para garantir a integridade dos dados de estoque e evitar cenários onde uma venda é registrada para um produto que não está fisicamente disponível.

A verificação é feita em todas as operações de `SAIDA`. Se uma movimentação de saída resultar em um saldo menor que zero, a API retornará um erro `400 Bad Request` com a mensagem "Saldo insuficiente".

*   **Onde configurar?** A permissão pode ser alterada diretamente no código, na variável `ALLOW_NEGATIVE_STOCK` no arquivo `app/api/v1/rotas_estoque.py`.

---

## Exemplos de Chamadas (usando `curl`)

**Nota:** Antes de testar, crie um produto. Substitua `{produto_id}` pelo ID do produto criado.

**1. Criar um Produto**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/produtos/' \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "Caderno 10 Matérias",
    "descricao": "Caderno espiral com 200 folhas",
    "preco": 2500,
    "estoque_minimo": 10
  }'
```

**2. Registrar uma Entrada (Ajuste)**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/estoque/ajuste' \
  -H 'Content-Type: application/json' \
  -d '{
    "produto_id": 1,
    "tipo": "ENTRADA",
    "quantidade": 50,
    "motivo": "Compra de fornecedor"
  }'
```

**3. Registrar uma Venda**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/estoque/venda' \
  -H 'Content-Type: application/json' \
  -d '{
    "produto_id": 1,
    "quantidade": 5
  }'
```

**4. Registrar uma Devolução**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/estoque/devolucao' \
  -H 'Content-Type: application/json' \
  -d '{
    "produto_id": 1,
    "quantidade": 1
  }'
```

**5. Consultar o Extrato de um Produto**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/estoque/extrato/1'
```

**6. Consultar o Resumo do Estoque**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/estoque/resumo'
```