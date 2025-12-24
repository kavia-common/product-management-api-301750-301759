# products_backend (FastAPI)

FastAPI backend exposing CRUD APIs for managing products with fields:

```json
{ "id": "uuid", "name": "string", "price": 0.0 }
```

- Runs on port **3001**
- In-memory storage (data resets on restart)
- CORS enabled for `*`
- OpenAPI available at `/docs` and `/openapi.json`

## Run locally

From `product-management-api-301750-301759/products_backend`:

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 3001
```

Then open:

- Swagger UI: `http://localhost:3001/docs`
- OpenAPI JSON: `http://localhost:3001/openapi.json`

On startup the service seeds two demo products.

## Endpoints

### Health
- `GET /health` → `{"status":"ok"}`

### Products
- `POST /products` (create)
- `GET /products` (list)
- `GET /products/{id}` (get)
- `PUT /products/{id}` (update)
- `DELETE /products/{id}` (delete)

## Example requests

### List products

```bash
curl -s http://localhost:3001/products | jq
```

Response:

```json
[
  { "id": "b0f6c6f3-3b2a-4d2f-a17a-3e4c0f3f0c0e", "name": "Demo Widget", "price": 9.99 }
]
```

### Create product

```bash
curl -s -X POST http://localhost:3001/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Coffee Mug","price":12.5}' | jq
```

Response:

```json
{ "id": "0c0b3b7e-6d2a-4b56-9b2c-9d2f0d7b7e1a", "name": "Coffee Mug", "price": 12.5 }
```

### Get product

```bash
ID="0c0b3b7e-6d2a-4b56-9b2c-9d2f0d7b7e1a"
curl -s http://localhost:3001/products/$ID | jq
```

### Update product

```bash
ID="0c0b3b7e-6d2a-4b56-9b2c-9d2f0d7b7e1a"
curl -s -X PUT http://localhost:3001/products/$ID \
  -H "Content-Type: application/json" \
  -d '{"name":"Large Coffee Mug","price":14.0}' | jq
```

### Delete product

```bash
ID="0c0b3b7e-6d2a-4b56-9b2c-9d2f0d7b7e1a"
curl -i -X DELETE http://localhost:3001/products/$ID
```

Expected: `204 No Content`

## Error behavior

- Missing product id → `404 {"detail":"Product not found"}`
- Invalid payload (e.g., empty name or negative price) → `422` via FastAPI/Pydantic validation
