from __future__ import print_function

import doctest
import os

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DOCS_DIRS = [PROJECT_ROOT, os.path.join(PROJECT_ROOT, 'doc')]

@pytest.mark.parametrize("path", [
    os.path.join(path, filename)
    for path in DOCS_DIRS
    for filename in os.listdir(path)
    if filename.endswith((".rst", ".md"))])
def test_doctests(path):
    assert os.path.exists(path)

    context_filename = path + ".ctx.py"
    context = {}
    if os.path.exists(context_filename):
        with open(context_filename) as f:
            exec(f.read(), context)

    result = doctest.testfile(path, module_relative=False, globs=context)
    assert result.failed == 0
