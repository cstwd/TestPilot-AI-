from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend import database, projects, workbench


@pytest.fixture
def request_stub(tmp_path):
    path = tmp_path / "db"
    database.initialize(path)
    workbench.initialize(path)
    return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(db_path=path)))


def test_project_versions(request_stub):
    r = request_stub
    a, b = [projects.create_project(projects.ProjectInput(name=n), r)["id"] for n in ("Alpha", "Beta")]
    def add(src):
        return projects.import_file(a, projects.FileInput(filename="maths.py", source=src), r)
    with ThreadPoolExecutor(2) as pool:
        first, repeat = pool.map(add, ["x=1", "x=1"])
    assert first == repeat
    second = add("x=2")
    assert second["revision"] == 2 and second["sha256"] != first["sha256"]
    assert projects.read_file(first["id"], r)["source"] == "x=1"
    assert projects.list_files(b, r) == []
    workbench.initialize(r.app.state.db_path)
    assert len(projects.list_files(a, r)) == len(projects.list_projects(r)) == 2


@pytest.mark.parametrize("name", ["../bad.py", "C:bad.py", "CON.py", "file.txt"])
def test_bad_import(request_stub, name):
    with pytest.raises(HTTPException) as error:
        projects.import_file(1, projects.FileInput(filename=name, source="x"), request_stub)
    assert error.value.status_code == 422
