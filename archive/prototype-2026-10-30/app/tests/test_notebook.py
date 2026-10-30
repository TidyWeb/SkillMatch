import importlib.util

import pytest

pytest.importorskip("nbformat", reason="notebook group not installed (uv sync --group notebook)")


def load_builder():
    spec = importlib.util.spec_from_file_location("build_notebook", "scripts/build_notebook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_notebook_has_required_sections():
    nb = load_builder().build()
    text = "\n".join(c.source for c in nb.cells)
    for needle in [
        "Hypothesis 1",
        "fisher_exact",
        "chi2_contingency",
        "Hypothesis 2",
        "transferable competencies",
        "## Limitations",
        "AI-assisted interpretation: what we checked, kept and rejected",
        "MODE",
    ]:
        assert needle in text, needle
