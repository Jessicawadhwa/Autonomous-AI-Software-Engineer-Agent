import pytest

@pytest.mark.asyncio
async def test_create_and_get_project(async_client):
    payload = {
        "name": "EmployeeService",
        "description": "FastAPI employee management backend",
        "requirement": "Build a FastAPI REST API for employee management with CRUD and SQLite",
        "options": {"generate_tests": True}
    }
    response = await async_client.post("/api/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "EmployeeService"
    project_id = data["id"]

    # Get project
    get_res = await async_client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200
    p_data = get_res.json()
    assert p_data["project"]["name"] == "EmployeeService"

    # List projects
    list_res = await async_client.get("/api/projects")
    assert list_res.status_code == 200
    assert any(p["id"] == project_id for p in list_res.json())

    # Download zip
    dl_res = await async_client.get(f"/api/projects/{project_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/zip"

    # Delete project
    del_res = await async_client.delete(f"/api/projects/{project_id}")
    assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_settings_endpoints(async_client):
    res = await async_client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data

    update_payload = {
        "provider": "demo",
        "temperature": 0.3,
        "max_debug_iterations": 5
    }
    up_res = await async_client.post("/api/settings", json=update_payload)
    assert up_res.status_code == 200
    assert up_res.json()["temperature"] == 0.3

@pytest.mark.asyncio
async def test_mcp_endpoints(async_client):
    tools_res = await async_client.get("/api/mcp/tools")
    assert tools_res.status_code == 200
    assert "tools" in tools_res.json()
    assert len(tools_res.json()["tools"]) >= 4
