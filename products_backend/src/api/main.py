from __future__ import annotations

from typing import Dict, List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Shared product fields."""

    name: str = Field(..., min_length=1, description="Non-empty product name.")
    price: float = Field(..., ge=0, description="Non-negative product price.")


class ProductCreate(ProductBase):
    """Payload for creating a product."""


class ProductUpdate(ProductBase):
    """Payload for updating a product."""


class Product(ProductBase):
    """Product model returned by the API."""

    id: UUID = Field(..., description="Unique product identifier (UUID).")


# In-memory storage: UUID -> Product
_PRODUCTS: Dict[UUID, Product] = {}


def _seed_products() -> None:
    """Seed a couple of demo products if storage is empty."""
    if _PRODUCTS:
        return

    demo_items = [
        Product(id=uuid4(), name="Demo Widget", price=9.99),
        Product(id=uuid4(), name="Demo Gadget", price=19.5),
    ]
    for item in demo_items:
        _PRODUCTS[item.id] = item


app = FastAPI(
    title="Products API",
    description="A simple REST API to perform CRUD operations on products.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Readiness/liveness endpoints."},
        {"name": "Products", "description": "CRUD operations for products."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified for demo usage.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _on_startup() -> None:
    """Seed demo products on startup for quick testing."""
    _seed_products()


# PUBLIC_INTERFACE
@app.get(
    "/health",
    tags=["Health"],
    summary="Readiness check",
    description="Simple readiness endpoint for container/platform health checks.",
)
def health() -> dict:
    """Return service readiness status."""
    return {"status": "ok"}


# PUBLIC_INTERFACE
@app.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create a product",
    description="Create a new product with a generated UUID id.",
)
def create_product(payload: ProductCreate) -> Product:
    """Create a product and store it in memory."""
    product = Product(id=uuid4(), **payload.model_dump())
    _PRODUCTS[product.id] = product
    return product


# PUBLIC_INTERFACE
@app.get(
    "/products",
    response_model=List[Product],
    tags=["Products"],
    summary="List products",
    description="Return all products currently stored in memory.",
)
def list_products() -> List[Product]:
    """List all products."""
    return list(_PRODUCTS.values())


# PUBLIC_INTERFACE
@app.get(
    "/products/{id}",
    response_model=Product,
    tags=["Products"],
    summary="Get product by id",
    description="Fetch a product by its UUID id.",
)
def get_product(
    id: UUID = Path(..., description="Product id (UUID)."),
) -> Product:
    """Return a single product by id."""
    product = _PRODUCTS.get(id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# PUBLIC_INTERFACE
@app.put(
    "/products/{id}",
    response_model=Product,
    tags=["Products"],
    summary="Update product",
    description="Replace product fields (name, price) for the given id.",
)
def update_product(
    payload: ProductUpdate,
    id: UUID = Path(..., description="Product id (UUID)."),
) -> Product:
    """Update an existing product."""
    if id not in _PRODUCTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    updated = Product(id=id, **payload.model_dump())
    _PRODUCTS[id] = updated
    return updated


# PUBLIC_INTERFACE
@app.delete(
    "/products/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    tags=["Products"],
    summary="Delete product",
    description="Delete the product with the given id.",
)
def delete_product(
    id: UUID = Path(..., description="Product id (UUID)."),
) -> None:
    """Delete a product.

    Notes:
        This endpoint intentionally returns *no content* (HTTP 204). We set
        `response_model=None` to prevent FastAPI from inferring a response model
        from the return annotation under postponed evaluation of annotations
        (`from __future__ import annotations`), which would otherwise cause an
        assertion error at startup for 204 responses.
    """
    if id not in _PRODUCTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    del _PRODUCTS[id]
    return None


# PUBLIC_INTERFACE
def run() -> None:
    """Run the development server on 0.0.0.0:3001 (useful outside ASGI deployments)."""
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=3001, reload=False)


if __name__ == "__main__":
    run()
