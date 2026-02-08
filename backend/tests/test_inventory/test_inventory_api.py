from httpx import AsyncClient

# 1. Create Product
async def test_create_product(client: AsyncClient):
    payload = {
        "sku": "MOUSE-001",
        "name": "Wireless Mouse",
        "stock": 50,
        "price": 25.99,
        "is_active": True
    }
    response = await client.post("/products/product", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "MOUSE-001"
    assert data["name"] == "Wireless Mouse"
    assert float(data["price"]) == 25.99
    assert "product_id" in data

# 2. Get Products (List)
async def test_get_products(client: AsyncClient):
    # Setup: Create extra product to ensure data exists
    await client.post("/products/product", json={
        "sku": "KEYBOARD-001", 
        "name": "Mech Keyboard", 
        "stock": 10, 
        "price": 100.00
    })
    
    response = await client.get("/products/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

# 3. Update Product
async def test_update_product(client: AsyncClient):
    # Setup
    create_res = await client.post("/products/product", json={
        "sku": "SCREEN-001", "name": "Screen 24", "stock": 5, "price": 150.00
    })
    pid = create_res.json()["product_id"]
    
    # Update
    payload = {"price": 140.00, "stock": 8}
    response = await client.patch(f"/products/product/{pid}", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["price"]) == 140.00
    assert data["stock"] == 8
    assert data["name"] == "Screen 24" # Should not change

# 4. Delete Product
async def test_delete_product(client: AsyncClient):
    # Setup
    create_res = await client.post("/products/product", json={
        "sku": "CABLE-001", "name": "HDMI Cable", "stock": 100, "price": 5.00
    })
    pid = create_res.json()["product_id"]
    
    # Delete
    response = await client.delete(f"/products/product/{pid}")
    assert response.status_code == 200
    
    # Verify deletion
    list_res = await client.get("/products/products")
    assert not any(p["product_id"] == pid for p in list_res.json())
