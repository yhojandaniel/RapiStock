from httpx import AsyncClient

# 1. Create Seller
async def test_create_seller(client: AsyncClient):
    payload = {
        "fullname": "John Doe",
        "dni": "12345678",
        "email": "john@example.com",
        "phone": "+123456789"
    }
    response = await client.post("/sellers/seller", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["fullname"] == "John Doe"
    assert "seller_id" in data

# 2. Get Sellers
async def test_get_sellers(client: AsyncClient):
    # Setup
    await client.post("/sellers/seller", json={
        "fullname": "Jane Doe",
        "dni": "87654321", 
        "email": "jane@example.com",
        "phone": "+987654321"
    })
    
    response = await client.get("/sellers/sellers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

# 3. Update Seller
async def test_update_seller(client: AsyncClient):
    # Setup
    create_res = await client.post("/sellers/seller", json={
        "fullname": "Update Me",
        "dni": "11223344",
        "email": "update@example.com"
    })
    sid = create_res.json()["seller_id"]
    
    # Update
    payload = {"fullname": "Updated Name", "phone": "+555555555"}
    response = await client.patch(f"/sellers/seller/{sid}", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["fullname"] == "Updated Name"
    assert data["phone"] == "+555555555"
    assert data["dni"] == "11223344"

# 4. Delete Seller
async def test_delete_seller(client: AsyncClient):
    # Setup
    create_res = await client.post("/sellers/seller", json={
        "fullname": "Delete Me",
        "dni": "99887766",
        "email": "delete@example.com"
    })
    sid = create_res.json()["seller_id"]
    
    # Delete
    response = await client.delete(f"/sellers/seller/{sid}")
    assert response.status_code == 202
    
    # Verify (GET by ID is not exposed as direct route in your router code shown, but list search is)
    # Checking list
    list_res = await client.get("/sellers/sellers")
    assert not any(s["seller_id"] == sid for s in list_res.json())
