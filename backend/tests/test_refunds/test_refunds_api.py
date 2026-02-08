from httpx import AsyncClient

async def create_full_order(client: AsyncClient, sku_suffix):
    # 1. Product
    prod_res = await client.post("/products/product", json={
        "sku": f"REF-PROD-{sku_suffix}", "name": f"Refundable {sku_suffix}", "stock": 100, "price": 10.00, "is_active": True
    })
    prod = prod_res.json()
    
    # 2. Seller
    seller_res = await client.post("/sellers/seller", json={
        "fullname": "Refund Seller", "dni": f"REF-{sku_suffix}", "email": f"ref{sku_suffix}@test.com"
    })
    seller = seller_res.json()
    
    # 3. Order
    order_res = await client.post("/orders/order", json={
        "seller_id": seller["seller_id"],
        "details": [{"product_id": prod["product_id"], "product_quantity": 5}]
    })
    return order_res.json()

# 1. Create Refund
async def test_create_refund(client: AsyncClient):
    order = await create_full_order(client, "001")
    order_id = order["order_id"]
    detail_id = order["details"][0]["order_detail_id"]
    
    payload = {
        "order_id": order_id,
        "details": [
            {
                "order_detail_id": detail_id,
                "product_quantity": 2, # Refunding 2 of 5
                "status": "opened" # Valid: 'same', 'opened'
            }
        ]
    }
    
    response = await client.post("/refunds/refund", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == order_id
    assert len(data["details"]) == 1
    # Check amount: 2 items * 10.00 = 20.00
    assert float(data["amount"]) == 20.00

# 2. Get Refunds
async def test_get_refunds(client: AsyncClient):
    # Setup
    order = await create_full_order(client, "002")
    payload = {
        "order_id": order["order_id"],
        "details": [{
            "order_detail_id": order["details"][0]["order_detail_id"],
            "product_quantity": 1, 
            "status": "same"
        }]
    }
    await client.post("/refunds/refund", json=payload)
    
    response = await client.get("/refunds/refunds")
    assert response.status_code == 200
    assert len(response.json()) >= 1