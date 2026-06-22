"""Functions and classes for parsing from template/db files using tree-sitter-epics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import tree_sitter
import tree_sitter_epics_db
from tree_sitter import Node

if TYPE_CHECKING:
    import os
    from collections.abc import Generator


class DbParserError(Exception):
    """DbParser class exception.

    Raised when parsing a ``.db`` file that ``tree-sitter-epics-db`` couldn't parse.
    """

    def __init__(self: DbParserError, message: str) -> None:
        """Initialize DbParserError Class with a message."""
        super().__init__(message)


@dataclass(frozen=True, slots=True, kw_only=True)
class Link:
    """Represents a Record Link."""

    record_name: str
    """The name of the linked record.

    .. versionadded:: 0.3.0
    """

    type_link: str
    """The type of link.

    .. versionadded:: 0.3.0
    """

    @staticmethod
    def parse(field: str) -> Link | None:
        """Create a Link from the value of a "link" field.

        :returns: The Link, or :py:obj:`None` on parse error.

        .. versionadded:: 0.3.0
        """
        splits = field.split()
        name = splits[0].replace('"', "")
        type_link = ""
        if len(splits) > 1:
            type_link = splits[1].replace('"', "")
        if not name.startswith("@"):
            return Link(
                record_name=name,
                type_link=type_link,
            )
        return None

    @staticmethod
    def create_link(field: str) -> Link:
        """Create a Link Class from a link field.

        :returns: The Link, or :py:obj:`None` on parse error.

        .. deprecated:: 0.3.0
           Use :py:meth:`parse` instead.
        """
        return Link.parse(field)


class DbParser:
    """To handle tree-sitter parsing.

    .. deprecated:: 0.3.0
       Use :py:func:`parse_str` instead
    """

    def __init__(self: DbParser) -> None:
        """Py Tree sitter configuration.

        .. deprecated:: 0.3.0
           Use :py:func:`parse_str` instead
        """
        pass

    def parse(self: DbParser, text: str) -> None:
        """Parse the text in argument to build the tree of the object.

        .. deprecated:: 0.3.0
           Use :py:func:`parse_str` instead
        """
        self.database = parse_str(text)

    def build_records_list(self: DbParser) -> list:
        """From a tree-sitter node built a list of object 'db' class.

        .. deprecated:: 0.3.0
           Use :py:func:`parse_str` and the :py:attr:`Record.fields` instead.
        """
        return self.database.records


_DATABASE_DOC_QUERY = tree_sitter.Query(
    tree_sitter.Language(tree_sitter_epics_db.language()),
    """
(source_file . (comment)+ @database_documentation)
""",
)

_RECORD_QUERY = tree_sitter.Query(
    tree_sitter.Language(tree_sitter_epics_db.language()),
    """
(
  (comment)* @record_documentation
  .
  (record_instance
    type: (record_type) @record_type
    name: (record_name) @record_name) @record
)
""",
)

_RECORD_CONTENT_QUERY = tree_sitter.Query(
    tree_sitter.Language(tree_sitter_epics_db.language()),
    """
(field
  name: (_) @field_name
  value: (_) @field_value)

(info
  name: (_) @info_name
  value: (_) @info_value)
""",
)


@dataclass(slots=True, kw_only=True)
class Database:
    """Represents an EPICS database file.

    .. versionadded:: 0.3.0
    """

    documentation: str | None
    """Toplevel documentation of the datbase file.

    The documentation is the first comment block prefixed by ``#|``,
    for example::

        #| This is
        #| a database
        #| toplevel documentation.

        # ...

    .. versionadded:: 0.3.0
    """

    records: list[Record]
    """Records present in this database file.

    .. versionadded:: 0.3.0
    """


@dataclass(frozen=True, slots=True, kw_only=True)
class Record:
    """Represents an EPICS record."""

    type: str
    """The type of the record, for example ``ai``.

    .. versionadded:: 0.3.0
    """

    name: str
    """The name of the record.

    .. versionadded:: 0.3.0
    """

    documentation: str | None
    """The documentation of the record.

    The documentation is obtained from adjacent comments before the record,
    or the ``DESC`` field, if none defined.
    For example::

        # This is
        # the record documentation
        record(ai, "...") {
            # ...
        }

    Or::

        record(ai, "...") {
            field(DESC, "This is the record documentation")
        }

    .. versionadded:: 0.3.0
    """

    fields: dict[str, str]
    """The fields declared in this record."""

    infos: dict[str, str]
    """The info items declared in this record."""

    @property
    def record_name(self) -> str:
        """The name of the record.

        .. deprecated:: 0.3.0
           Use :py:attr:`name` instead
        """
        return self.name

    @property
    def record_type(self) -> str:
        """The type of the record.

        .. deprecated:: 0.3.0
           Use :py:attr:`type` instead
        """
        return self.type

    @property
    def description(self) -> str | None:
        """The documentation or description of the record.

        .. deprecated:: 0.3.0
           Use :py:attr:`documentation` instead
        """
        return self.documentation

    @property
    def unit(self) -> str | None:
        """The unit of the record.

        This is equivalent to fetching the ``EGU`` field.
        """
        return self.fields.get("EGU")

    @property
    def links_in(self) -> list[Link]:
        """List the incoming links specified in this record."""
        selected = []
        for name, value in self.fields.items():
            if name.startswith("INP") or name == "DOL":
                selected.append(Link.create_link(value))
        return selected

    @property
    def links_out(self) -> list[Link]:
        """List the outgoing links specified in this record."""
        selected = []
        for name, value in self.fields.items():
            if name.startswith("OUT") or name == "FLNK":
                selected.append(Link.create_link(value))
        return selected


def _to_str(value: tree_sitter.Node) -> str:
    """Convert a node to a string, stripping quotes if necessary."""
    return (value.text or b"").decode().strip('"')


def _is_next_to(first: Node, second: Node) -> bool:
    """Return whether `first` finishes in the line before `second`."""
    return first.end_point.row == second.start_point.row + 1


def _select_adjacent_comments(comments: list[Node]) -> Generator[Node]:
    """Select the first streak of comments that are adjacent to each other."""
    if not comments:
        return None

    first_comment = comments[0]
    last_comment = first_comment

    yield first_comment

    for comment in comments[1:]:
        if not _is_next_to(comment, last_comment):
            break

        yield comment
        last_comment = comment


def _select_doc_comments(comments: list[Node], record: Node) -> list[Node] | None:
    """Select all comments that are directly adjacent to the given record."""
    last_comment = comments[-1]

    # If the last comment is not next to the record, ignore everything
    if last_comment.end_point.row + 1 != record.range.start_point.row:
        return None

    selected = [last_comment]
    last_row = last_comment.end_point.row

    for comment in reversed(comments[:-1]):
        row = comment.end_point.row
        if row + 1 != last_row:
            break
        selected.insert(0, comment)
        last_row = row

    return selected


def _comments_to_str(comments: list[Node], prefix: str = "#") -> str:
    comments_txt = [(comment.text or b"").decode() for comment in comments]
    return "\n".join(comment.removeprefix(prefix).removeprefix(" ") for comment in comments_txt)


def _process_comments(comments: list[Node], record: Node) -> str | None:
    doc_comments = _select_doc_comments(comments, record)
    if not doc_comments:
        return None
    return _comments_to_str(doc_comments)


def _record_from_match(match: dict[str, list[Node]]) -> Record:
    typ = _to_str(match["record_type"][0])
    record_name = _to_str(match["record_name"][0])
    documentation = (
        _process_comments(match["record_documentation"], match["record"][0])
        if "record_documentation" in match
        else None
    )
    fields = {}
    infos = {}

    cursor = tree_sitter.QueryCursor(_RECORD_CONTENT_QUERY)

    for _idx, content_match in cursor.matches(match["record"][0]):
        if not content_match:
            continue
        if "field_name" in content_match:
            name = _to_str(content_match["field_name"][0])
            value = _to_str(content_match["field_value"][0])
            fields[name] = value
        elif "info_name" in content_match:
            name = _to_str(content_match["info_name"][0])
            value = _to_str(content_match["info_value"][0])
            infos[name] = value

    if not documentation:
        documentation = fields.get("DESC")

    return Record(
        type=typ,
        name=record_name,
        documentation=documentation,
        fields=fields,
        infos=infos,
    )


def _database_doc(root_node: Node) -> str | None:
    db_doc_cursor = tree_sitter.QueryCursor(_DATABASE_DOC_QUERY)
    db_doc_matches = db_doc_cursor.matches(root_node)

    if not db_doc_matches:
        return None

    db_doc_comments = list(
        _select_adjacent_comments(
            [
                comment
                for comment in db_doc_matches[0][1].get("database_documentation", [])
                if (comment.text or b"").startswith(b"#|")
            ],
        ),
    )

    if not db_doc_comments:
        return None

    return _comments_to_str(db_doc_comments, prefix="#|")


def parse_bytes(b: bytes) -> Database:
    """Parse the given bytes in EPICS Database format.

    .. versionadded:: 0.3.0
    """
    parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_epics_db.language()))
    tree = parser.parse(b)
    if tree.root_node.has_error:
        message = "Syntax error: check syntax or if it is real EPICS databases."
        raise DbParserError(message)

    record_cursor = tree_sitter.QueryCursor(_RECORD_QUERY)
    record_matches = record_cursor.matches(tree.root_node)

    return Database(
        documentation=_database_doc(tree.root_node),
        records=[
            _record_from_match(match)
            for (_idx, match) in record_matches
            if "record" in match
        ],
    )


def parse_str(s: str) -> Database:
    """Parse the given string in EPICS Database format.

    .. versionadded:: 0.3.0
    """
    return parse_bytes(s.encode())


def parse_file(file: str | os.PathLike) -> Database:
    """Parse the given ``.db`` file.

    .. versionadded:: 0.3.0
    """
    return parse_bytes(Path(file).read_bytes())
