from pathlib import Path
from types import SimpleNamespace

import pytest

from backend import database, generation, projects, workbench

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_workspace(tmp_path):
    path = tmp_path / "workflow.sqlite3"
    database.initialize(path)
    workbench.initialize(path)
    state = SimpleNamespace(db_path=path, generators={"template": generation.TemplateAdapter()})
    request = SimpleNamespace(app=SimpleNamespace(state=state))
    project = projects.create_project(projects.ProjectInput(name="Regression"), request)
    files = []
    for tag in ("buggy", "fixed"):
        source = (ROOT / "eval" / "phase02" / tag / "magnitude.py").read_text(encoding="utf-8")
        files.append(projects.import_file(project["id"], projects.FileInput(filename="magnitude.py", source=source), request))
    suite = generation.generate(files[0]["id"], generation.GenerateInput(target="magnitude"), request)
    return request, project, files, suite
