# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

```{py:currentmodule} py_tree_sitter_epics
```

## [Unreleased]

### Added

- A new {py:class}`epicsdb.Database` class, that represents a database file.

  This contains a list of records,
  and a documentation for the file,
  which you can write like
  by using `#|` comments:

  ```
  #| This is
  #| a database
  #| toplevel documentation.

  # ...
  ```

  This special comment has to be before any declaration.

- New simplified functions for parsing DBs:
  - {py:func}`epicsdb.parse_file`
  - {py:func}`epicsdb.parse_str`
  - {py:func}`epicsdb.parse_bytes`

### Deprecated

- The `epicsdb.DbParser` class was deprecated,
  use one of the {py:func}`epicsdb.parse_file`,
  {py:func}`epicsdb.parse_str`,
  or {py:func}`epicsdb.parse_bytes` functions instead

- The `epicsdb.Link.create_link` method was renamed to {py:meth}`epicsdb.Link.parse`

- Several {py:class}`epicsdb.Record` fields were renamed:

  - `epicsdb.Record.description` into {py:attr}`epicsdb.Record.documentation`
  - `epicsdb.Record.record_name` into {py:attr}`epicsdb.Record.name`
  - `epicsdb.Record.record_type` into {py:attr}`epicsdb.Record.type`

### Removed

- The record's `print_to_text` function was removed

  [Unreleased]: https://github.com/epics-extensions/py-tree-sitter-epics/compare/v0.2.2...main

## [0.2.2] --- 2025-10-23

First official release!

### Added

Support for parsing DB files:

- Getting input and output links from records
- Getting documentation from records

  [0.2.2]: https://github.com/epics-extensions/py-tree-sitter-epics/releases/tag/v0.2.2
