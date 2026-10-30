import subprocess
import sys

BLOCK = """
import importlib.abc, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name.split(".")[0] in {"pandas", "requests", "bs4", "dotenv", "numpy"}:
            raise ModuleNotFoundError(name)
sys.meta_path.insert(0, Block())
from skillmatch.web import create_app
app = create_app({"TESTING": True})
for path in ["/", "/results", "/insights", "/sources", "/about"]:
    assert app.test_client().get(path).status_code == 200, path
print("ok")
"""


def test_web_app_runs_without_etl_dependencies():
    """The container installs only the web dependencies; the app must not import ETL ones."""
    out = subprocess.run([sys.executable, "-c", BLOCK], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-2000:]
