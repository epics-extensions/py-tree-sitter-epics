# PY-TREE-SITTER-EPICS

Based on [Tree sitter ](https://github.com/tree-sitter/tree-sitter), [tree-sitter-epics](https://github.com/epics-extensions/tree-sitter-epics) and [Py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter), this module is used to serialize any [EPICS](https://epics-controls.org/) files into a Python object usable in a script.

*⚠️ For now it is only developped for EPICS CA database but it will support more files in the future.*

## Installation

The module is available on [Pypi](https://github.com/tree-sitter/tree-sitter). This package currently only works with Python \>3.10. The library dependencis is tree-sitter-epics

``` console
pip3 install py-tree-sitter-epics
```

You may need to use this line

``` console
pip3 install py-tree-sitter-epics --break-system-packages
```

## Using

This example show how to use the module. It is parsing a file building a python object containing all the fields, infos and links to finally displaying all those infos.

``` python
from py_tree_sitter_epics import epicsdb

with Path.open("/tmp/myExample.db") as file:
        code = file.read()
#build the parser
db_parser = epicsdb.DbParser()
#parse the code
db_parser.parse(code)
#build record list from the parser
record_list = db_parser.build_records_list()
for record in reccord_list:
    #print a complete result
    record.print_to_text()
```

``` mermaid
classDiagram
    Record--o Link : 0..1
    class Link {
        set_record_name()
        set_type_link()
        create_link()
        string record_name
        string type_link
    }
    class Record {
        set_record_type()
        set_record_name()
        set_description()
        set_fields()
        set_infos()
        set_links_in()
        set_links_out()
        add_link_out()
        add_link_in()
        print_to_text()
        string record_type 
        string record_name 
        string description 
        tuple[string,string] fields 
        string unit
        string description
        string infos
        List<Link> links_in
        List<Link> links_out
    }
    class DbParser {
        +parse()
        +build_fields()
        +build_comment()
        +build_infos()
        +build_records_list()
        parserTree
        tree
        root_node
        tree
    }

   
```