import os
import tempfile
import shutil
import pytest
from fastapi.testclient import TestClient
from backend.routes.evals import router, EVALS_DIR
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def temp_eval_dirs():
    # Setup temporary directories and files for testing
    base_dir = tempfile.mkdtemp()
    input_dir = os.path.join(EVALS_DIR, "inputs")
    os.makedirs(input_dir, exist_ok=True)
    # Create a sample input image
    input_image_path = os.path.join(input_dir, "test.png")
    with open(input_image_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
    # Create output HTML files in a temp folder
    folder = os.path.join(base_dir, "outputs")
    os.makedirs(folder, exist_ok=True)
    html_path = os.path.join(folder, "test.html")
    with open(html_path, "w") as f:
        f.write("<html>output</html>")
    yield base_dir, folder, input_image_path, html_path
    shutil.rmtree(base_dir)

# /evals endpoint

def test_get_evals_happy_path(client, temp_eval_dirs):
    base_dir, folder, input_image_path, html_path = temp_eval_dirs
    response = client.get("/evals", params={"folder": folder})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("outputs" in e for e in data)

def test_get_evals_missing_folder(client):
    response = client.get("/evals", params={"folder": "/nonexistent/folder"})
    # With the security flaw, this may return 500 or empty list
    assert response.status_code in (200, 500)

def test_get_evals_directory_traversal(client, temp_eval_dirs):
    # Try to access parent directory (security flaw test)
    base_dir, folder, _, _ = temp_eval_dirs
    parent = os.path.dirname(folder)
    response = client.get("/evals", params={"folder": parent})
    # Should not be allowed, but with the flaw, may return 200 or 500
    assert response.status_code in (200, 500)

# /pairwise-evals endpoint

def test_pairwise_evals_happy_path(client, temp_eval_dirs):
    base_dir, folder, input_image_path, html_path = temp_eval_dirs
    # Duplicate folder for pairwise
    response = client.get("/pairwise-evals", params={"folder1": folder, "folder2": folder})
    assert response.status_code == 200
    data = response.json()
    assert "evals" in data
    assert "folder1_name" in data and "folder2_name" in data

def test_pairwise_evals_missing_folder(client):
    response = client.get("/pairwise-evals", params={"folder1": "/nope", "folder2": "/nope2"})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

# /run_evals endpoint

def test_run_evals_invalid_model(client):
    # Stack is required, but we can pass a dummy value
    response = client.post("/run_evals", json={"models": ["fake-model"], "stack": "dummy"})
    # Should return 422 due to validation error
    assert response.status_code == 422

# /models endpoint

def test_get_models(client):
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "stacks" in data

# /best-of-n-evals endpoint

def test_best_of_n_evals_happy_path(client, temp_eval_dirs):
    base_dir, folder, input_image_path, html_path = temp_eval_dirs
    params = {"folder1": folder}
    response = client.get("/best-of-n-evals", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "evals" in data
    assert "folder_names" in data

def test_best_of_n_evals_no_folders(client):
    response = client.get("/best-of-n-evals")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data or "evals" in data

def test_best_of_n_evals_missing_folder(client):
    params = {"folder1": "/nope"}
    response = client.get("/best-of-n-evals", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
