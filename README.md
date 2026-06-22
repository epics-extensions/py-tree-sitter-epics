# PY-TREE-SITTER-EPICS

[![ReadTheDocs - documentation](https://img.shields.io/badge/ReadTheDocs-documentation-blue?logo=readthedocs)](https://py-tree-sitter-epics.readthedocs.io/en/stable/)
[![PyPI - Version](https://img.shields.io/pypi/v/py-tree-sitter-epics)](https://pypi.org/project/py-tree-sitter-epics/)

Based on [tree-sitter](https://github.com/tree-sitter/tree-sitter) EPICS grammars
and [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter),
this module enables you to serialize [EPICS](https://epics-controls.org/) DB files
into semantic Python objects.

## Installation

The module is available on PyPI as [py-tree-sitter-epics](https://pypi.org/project/py-tree-sitter-epics/).

Add `py-tree-sitter-epics` to your `pyproject.toml`,
or if you use Python virtual environments:

```bash
# In your virtual environment
pip install py-tree-sitter-epics
```

## Example usage

``` python
from py_tree_sitter_epics import epicsdb

db = epicsdb.parse_file("/tmp/myExample.db")
for record in db.records:
    print(f"'{record.name}': {record.documentation}")
```
