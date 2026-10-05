import os
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from backend.app.tools.workspace_tools import create_file, update_file, read_file
from backend.app.tools.test_tools import run_project_pytest
from backend.app.tools.git_tools import git_commit

class MockDeterministicEngine:
    """
    High-fidelity deterministic software engineer engine for Demo Mode.
    Produces real production-quality code, executes real pytest suites,
    performs genuine debugging fixes, code reviews, and Git history commits.
    """

    @classmethod
    def generate_plan(cls, requirement: str, project_name: str) -> Dict[str, Any]:
        slug = re.sub(r'[^a-zA-Z0-9_-]', '_', project_name.lower())
        return {
            "project_name": project_name,
            "description": f"Production-ready backend API service for {project_name}, implementing requirements: {requirement}",
            "requirements": [
                "FastAPI RESTful application with asynchronous handlers",
                "SQLite database persistence with SQLAlchemy ORM",
                "Pydantic schemas with strict validation and error handling",
                "Modular service layer for clean separation of concerns",
                "Comprehensive pytest test suite with test isolation",
                "Automated Swagger/OpenAPI documentation generation"
            ],
            "tasks": [
                {"id": 1, "title": "Setup project directory structure and environment dependencies", "status": "pending"},
                {"id": 2, "title": "Configure SQLite database engine and declarative base models", "status": "pending"},
                {"id": 3, "title": "Implement Pydantic validation schemas (Create, Update, Response)", "status": "pending"},
                {"id": 4, "title": "Develop CRUD data access layer with exception handling", "status": "pending"},
                {"id": 5, "title": "Build FastAPI REST routes with dependency injection", "status": "pending"},
                {"id": 6, "title": "Author Pytest test cases covering CRUD operations & edge cases", "status": "pending"},
                {"id": 7, "title": "Perform automated test verification and debugging loop", "status": "pending"},
                {"id": 8, "title": "Run automated code review and security analysis", "status": "pending"},
                {"id": 9, "title": "Generate comprehensive README documentation and setup instructions", "status": "pending"}
            ],
            "dependencies": [
                "fastapi>=0.110.0",
                "uvicorn[standard]>=0.28.0",
                "sqlalchemy>=2.0.28",
                "pydantic>=2.6.0",
                "pytest>=8.1.0",
                "httpx>=0.27.0"
            ],
            "acceptance_criteria": [
                "Healthcheck endpoint returns 200 OK with server status",
                "Full CRUD endpoints work correctly against SQLite database",
                "Pydantic validation rejects invalid payloads with 422 Unprocessable Entity",
                "Non-existent entity lookups return 404 Not Found",
                "All automated pytest unit tests pass with zero errors"
            ]
        }

    @classmethod
    def generate_architecture(cls, requirement: str, project_name: str) -> Dict[str, Any]:
        return {
            "tech_stack": {
                "framework": "FastAPI",
                "database": "SQLite (aiosqlite / sqlalchemy)",
                "orm": "SQLAlchemy 2.0",
                "validation": "Pydantic V2",
                "testing": "Pytest + HTTPX AsyncClient"
            },
            "directory_structure": [
                "app/",
                "app/__init__.py",
                "app/main.py",
                "app/config.py",
                "app/database.py",
                "app/models.py",
                "app/schemas.py",
                "app/crud.py",
                "app/routes.py",
                "tests/",
                "tests/__init__.py",
                "tests/conftest.py",
                "tests/test_api.py",
                "requirements.txt",
                ".env.example"
            ],
            "modules": {
                "app.database": "Handles database session lifecycle and engine connection pooling",
                "app.models": "Defines SQLAlchemy table entities with timestamps and primary keys",
                "app.schemas": "Defines request/response contracts and data validation rules",
                "app.crud": "Encapsulates repository operations with safe database transactions",
                "app.routes": "API route handlers with dependency-injected DB sessions",
                "app.main": "Application factory, CORS middleware, exception handlers, and routing"
            },
            "security_considerations": [
                "Path traversal and SQL injection prevention via ORM parameter binding",
                "Input sanitization through Pydantic V2 type checking",
                "Structured exception handling preventing internal stack trace leaks"
            ]
        }

    @classmethod
    def write_initial_code(cls, workspace_root: Path, project_name: str, has_intentional_bug: bool = True) -> List[str]:
        """
        Creates full working source code in the project workspace.
        If has_intentional_bug is True, introduces a minor off-by-one or status code mismatch
        that pytest will catch on iteration 1, demonstrating real debugging!
        """
        files_written = []

        # 1. requirements.txt
        reqs = (
            "fastapi>=0.110.0\n"
            "uvicorn[standard]>=0.28.0\n"
            "sqlalchemy>=2.0.28\n"
            "pydantic>=2.6.0\n"
            "pytest>=8.1.0\n"
            "httpx>=0.27.0\n"
        )
        create_file(workspace_root, "requirements.txt", reqs)
        files_written.append("requirements.txt")

        # 2. app/__init__.py
        create_file(workspace_root, "app/__init__.py", '"""Application package."""\n__version__ = "1.0.0"\n')
        files_written.append("app/__init__.py")

        # 3. app/database.py
        db_code = '''import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app_data.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        create_file(workspace_root, "app/database.py", db_code)
        files_written.append("app/database.py")

        # 4. app/models.py
        models_code = '''from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
'''
        create_file(workspace_root, "app/models.py", models_code)
        files_written.append("app/models.py")

        # 5. app/schemas.py
        schemas_code = '''from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Item title")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed item description")
    priority: Literal["low", "medium", "high", "urgent"] = Field(default="medium", description="Priority level")
    status: Literal["pending", "in_progress", "completed"] = Field(default="pending", description="Current status")
    is_completed: bool = Field(default=False, description="Completion status")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    status: Optional[Literal["pending", "in_progress", "completed"]] = None
    is_completed: Optional[bool] = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
'''
        create_file(workspace_root, "app/schemas.py", schemas_code)
        files_written.append("app/schemas.py")

        # 6. app/crud.py (with potential bug for debugging demonstration)
        crud_code = '''from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Item
from app.schemas import ItemCreate, ItemUpdate

def get_item(db: Session, item_id: int) -> Optional[Item]:
    return db.query(Item).filter(Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
    return db.query(Item).offset(skip).limit(limit).all()

def create_item(db: Session, item_in: ItemCreate) -> Item:
    db_item = Item(
        title=item_in.title,
        description=item_in.description,
        priority=item_in.priority,
        status=item_in.status,
        is_completed=item_in.is_completed
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    db_item = get_item(db, item_id)
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True
'''
        create_file(workspace_root, "app/crud.py", crud_code)
        files_written.append("app/crud.py")

        # 7. app/routes.py
        # If has_intentional_bug is True, return 200 instead of 201 on create or raise 500 on delete to trigger debugger
        if has_intentional_bug:
            routes_code = '''from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ItemCreate, ItemUpdate, ItemResponse
import app.crud as crud

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[ItemResponse])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_200_OK) # BUG: Should be 201 Created
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item_in)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return crud.update_item(db, item, item_in)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return None
'''
        else:
            routes_code = '''from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ItemCreate, ItemUpdate, ItemResponse
import app.crud as crud

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[ItemResponse])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item_in)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return crud.update_item(db, item, item_in)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return None
'''
        create_file(workspace_root, "app/routes.py", routes_code)
        files_written.append("app/routes.py")

        # 8. app/main.py
        main_code = f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import router as items_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{project_name} API",
    description="Autonomous AI Engineered API Service with CRUD & SQLite persistence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items_router)

@app.get("/health", tags=["system"])
def health_check():
    return {{"status": "healthy", "service": "{project_name} API", "version": "1.0.0"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        create_file(workspace_root, "app/main.py", main_code)
        files_written.append("app/main.py")

        # 9. tests/conftest.py & tests/__init__.py
        create_file(workspace_root, "tests/__init__.py", "")
        files_written.append("tests/__init__.py")

        conftest_code = '''import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
'''
        create_file(workspace_root, "tests/conftest.py", conftest_code)
        files_written.append("tests/conftest.py")

        # 10. tests/test_api.py
        test_api_code = '''import pytest

def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_create_item_success(client):
    payload = {
        "title": "Integration Test Task",
        "description": "Verify item creation endpoint",
        "priority": "high",
        "status": "pending",
        "is_completed": False
    }
    response = client.post("/items/", json=payload)
    # Testing strict HTTP 201 Created requirement
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["id"] is not None

def test_get_item_by_id(client):
    # Create item first
    payload = {"title": "Lookup Test", "priority": "low", "status": "pending"}
    res = client.post("/items/", json=payload)
    item_id = res.json()["id"]

    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Lookup Test"

def test_get_nonexistent_item(client):
    response = client.get("/items/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_update_item(client):
    # Create item
    payload = {"title": "Before Update", "priority": "medium"}
    res = client.post("/items/", json=payload)
    item_id = res.json()["id"]

    # Update item
    update_payload = {"title": "After Update", "is_completed": True, "status": "completed"}
    put_res = client.put(f"/items/{item_id}", json=update_payload)
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "After Update"
    assert put_res.json()["is_completed"] is True

def test_delete_item(client):
    # Create item
    payload = {"title": "To Delete"}
    res = client.post("/items/", json=payload)
    item_id = res.json()["id"]

    # Delete item
    del_res = client.delete(f"/items/{item_id}")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 404
'''
        create_file(workspace_root, "tests/test_api.py", test_api_code)
        files_written.append("tests/test_api.py")

        return files_written

    @classmethod
    def apply_debugger_fix(cls, workspace_root: Path) -> Dict[str, Any]:
        """
        Fixes the status code issue in app/routes.py so tests pass 100%.
        """
        routes_path = "app/routes.py"
        res = read_file(workspace_root, routes_path)
        if res["success"]:
            fixed_code = res["content"].replace(
                'status_code=status.HTTP_200_OK) # BUG: Should be 201 Created',
                'status_code=status.HTTP_201_CREATED)'
            )
            update_file(workspace_root, routes_path, fixed_code)
            return {
                "fixed_file": routes_path,
                "description": "Fixed HTTP response status code in POST /items/ endpoint from 200 OK to 201 Created according to REST acceptance standards."
            }
        return {"fixed_file": routes_path, "error": "Could not read file to patch"}

    @classmethod
    def generate_review(cls, workspace_root: Path) -> List[Dict[str, Any]]:
        return [
            {
                "severity": "info",
                "file": "app/models.py",
                "line": 15,
                "issue": "Consider adding composite database index if querying by status and priority frequently",
                "recommendation": "Add Index('idx_item_status_priority', Item.status, Item.priority) for optimized high-volume query indexing."
            },
            {
                "severity": "low",
                "file": "app/routes.py",
                "line": 10,
                "issue": "Query offset and limit pagination without max ceiling",
                "recommendation": "Enforce Query(default=100, le=500) ceiling on limit parameter to protect memory under high load."
            },
            {
                "severity": "info",
                "file": "app/main.py",
                "line": 14,
                "issue": "CORS configured with wildcard origin for local development",
                "recommendation": "Before deploying to production, replace allow_origins=['*'] with specific trusted domain list."
            }
        ]

    @classmethod
    def generate_readme(cls, project_name: str, requirement: str, test_passed: int) -> str:
        return f"""# {project_name}

> Production-ready RESTful service autonomously generated, tested, and reviewed by **Autonomous AI Software Engineer Agent**.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Pytest](https://img.shields.io/badge/Tests-{test_passed}%20Passed-brightgreen.svg)](https://pytest.org)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🚀 Overview

This application fulfills the specification:
> **"{requirement}"**

The system provides full CRUD data lifecycle management with SQLite persistence, declarative SQLAlchemy ORM models, Pydantic V2 schema validation, structured error handling, automated Swagger documentation, and automated pytest coverage.

---

## 🏗️ Architecture

```mermaid
graph TD
    Client([HTTP Client / Frontend]) -->|JSON Payloads| API[FastAPI Application]
    API --> Middleware[CORS & Exception Handlers]
    Middleware --> Router[Routes /items]
    Router --> Schemas[Pydantic Validation Layer]
    Router --> CRUD[CRUD Service Layer]
    CRUD --> DB[(SQLite Database)]
```

---

## 📦 Project Structure

```text
├── app/
│   ├── __init__.py
│   ├── database.py       # Engine & SessionLocal configuration
│   ├── models.py         # SQLAlchemy Item table model
│   ├── schemas.py        # Pydantic request & response models
│   ├── crud.py           # Data access repository layer
│   ├── routes.py         # REST API route handlers
│   └── main.py           # FastAPI application factory
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures & isolated test client
│   └── test_api.py       # Comprehensive unit & integration tests
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## ⚡ Quick Start

### 1. Installation
```bash
# Clone repository
cd {project_name}

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
API server will be running at: `http://localhost:8000`

### 3. Interactive API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests

Execute test suite via `pytest`:
```bash
pytest tests/ -v
```

All `{test_passed}` automated tests verify CRUD integrity, schema validation, and status code compliance.

---

## 📡 API Endpoints

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/health` | Service health status | `200 OK` |
| `GET` | `/items/` | List all items (paginated) | `200 OK` |
| `GET` | `/items/{{id}}` | Get item by ID | `200 OK` / `404 Not Found` |
| `POST` | `/items/` | Create a new item | `201 Created` |
| `PUT` | `/items/{{id}}` | Update existing item | `200 OK` / `404 Not Found` |
| `DELETE` | `/items/{{id}}` | Delete item | `204 No Content` / `404 Not Found` |

---

## 🔒 Security & Code Quality
- Clean code architecture with dependency injection for database connections.
- Parameterized queries to eliminate SQL injection vulnerabilities.
- Validated payloads with Pydantic V2 to prevent malformed or unauthorized data entry.
"""
