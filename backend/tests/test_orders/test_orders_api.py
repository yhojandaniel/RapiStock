from httpx import AsyncClient

# Fixture-like helper to create dependencies
async def create_product(client: AsyncClient, sku="ORD-PROD-1"):
    res = await client.post("/products/product", json={
        "sku": sku, "name": f"Orderable Product {sku}", "stock": 100, "price": 50.00, "is_active": True
    })
    return res.json()

async def create_seller(client: AsyncClient, dni="11111111"):
    res = await client.post("/sellers/seller", json={
        "fullname": "Order Seller", "dni": dni, "email": f"{dni}@test.com"
    })
    return res.json()

# 1. Create Order
async def test_create_order(client: AsyncClient):
    # Dependencies
    prod = await create_product(client, "ORD-001")
    seller = await create_seller(client, "11111111")
    
    payload = {
        "seller_id": seller["seller_id"],
        "details": [
            {
                "product_id": prod["product_id"],
                "product_quantity": 2
            }
        ]
    }
    
    response = await client.post("/orders/order", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["seller_id"] == seller["seller_id"]
    assert len(data["details"]) == 1
    assert data["details"][0]["product_id"] == prod["product_id"]
    # assert data["total_amount"] == 100.00 # Removed as not in schema

# 2. Get Orders
async def test_get_orders(client: AsyncClient):
    # Ensure at least one order exists
    prod = await create_product(client, "ORD-002")
    seller = await create_seller(client, "22222222")
    await client.post("/orders/order", json={
        "seller_id": seller["seller_id"],
        "details": [{"product_id": prod["product_id"], "product_quantity": 1}]
    })
    
    response = await client.get("/orders/orders")
    assert response.status_code == 200
    assert len(response.json()) >= 1

# 3. Update Order Status
async def test_update_order(client: AsyncClient):
    # Setup
    prod = await create_product(client, "ORD-003")
    seller = await create_seller(client, "33333333")
    create_res = await client.post("/orders/order", json={
        "seller_id": seller["seller_id"],
        "details": [{"product_id": prod["product_id"], "product_quantity": 1}]
    })
    oid = create_res.json()["order_id"]
    
    # Update to CANCELLED (valid enum: paid, cancelled, refunded)
    response = await client.patch(f"/orders/order/{oid}?status_input=cancelled")
        
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
