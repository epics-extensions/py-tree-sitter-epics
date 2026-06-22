# py-tree-sitter-epics documentation

Based on [tree-sitter](https://github.com/tree-sitter/tree-sitter) EPICS grammars
and [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter),
this module enables you to serialize [EPICS](https://epics-controls.org/) DB files
into semantic Python objects.

```{code-block} bash
:caption: Example use

from py_tree_sitter_epics import epicsdb

db = epicsdb.parse_file("/tmp/myExample.db")
for record in db.records:
    print(f"'{record.name}': {record.documentation}")
```

```{toctree}
:titlesonly:
:hidden:

changelog
```

```{toctree}
:caption: API reference
:titlesonly:
:hidden:

epicsdb
```
