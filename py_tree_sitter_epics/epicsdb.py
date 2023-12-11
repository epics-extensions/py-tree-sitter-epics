"""Functions and classes for parsing from template/db files using tree-sitter-epics.

This module provides:
- dbParserError: exception raised by dbParser class.
- Record : python class to get Record information in a python object.
- DbParser : Python class to use easily py-tree-sitter en tree-sitter-epics
"""
from __future__ import annotations

import logging
from pathlib import Path

import tree_sitter


class DbParserError(Exception):
    """DbParser class exception.

    Raised by Db Parser class
    """

    def __init__(self: DbParserError, message: str) -> None:
        """Initialize DbParserError Class with a message."""
        super().__init__(message)


class Link:
    """to represent a Record Link in python object."""

    def __init__(
        self: Link,
    ) -> None:
        """Initialize Link Class with a the name of the record and the Link."""
        self.record_name = ""
        self.type_link = ""

    def set_record_name(self: Link, record_name: str) -> None:
        """Set the record name."""
        self.record_name = record_name.replace('"', "")

    def set_type_link(self: Link, type_link: str) -> None:
        """Set the type link."""
        self.type_link = type_link.replace('"', "")

    def create_link(field: str) -> Link:  # noqa: N805
        """Create a Link Class from a link field."""
        splits = field.split()
        name = splits[0].replace('"', "")
        type_link = ""
        if len(splits) > 1:
            type_link = splits[1].replace('"', "")
        if not name.startswith("@"):
            link = Link()
            link.record_name = name
            link.type_link = type_link

            return link
        return None


class Record:
    """to represent a Record in python object."""

    def __init__(
        self: Record,
    ) -> None:
        """Initialize a city with a name and population."""
        self.record_name = ""
        self.record_type = ""
        self.description = ""
        self.fields = []
        self.infos = []
        self.unit = ""

    def set_record_type(self: Record, record_type: str) -> None:
        """Set the record type."""
        self.record_type = record_type

    def set_record_name(self: Record, record_name: str) -> None:
        """Set the record name."""
        self.record_name = record_name

    def set_description(self: Record, description: str) -> None:
        """Set the record description."""
        self.description = description.replace("#", "")

    def set_fields(self: Record, fields: tuple[str, str]) -> None:
        """Set the fields."""
        self.fields = fields
        for name, value in fields:
            logging.debug("Field : %s = %s", name, value)
            match name:
                case "EGU":
                    self.unit = value
                case "DESC":
                    if self.description == "":
                        self.description = value

    def set_infos(self: Record, infos: tuple[str, str]) -> None:
        """Set the fields."""
        self.infos = infos

    def set_links_in(self: Record, link_in: list[Link]) -> None:
        """Set the list of EPICS INLINK."""
        self.links_in = link_in

    def set_links_out(self: Record, link_out: list[Link]) -> None:
        """Set the list of EPICS OUTLINK."""
        self.links_out = link_out

    def add_link_out(self: Record, link_out: Link) -> None:
        """Add EPICS OUTLINK to the Record."""
        self.links_out.append(link_out)

    def add_link_in(self: Record, link_in: Link) -> None:
        """Add EPICS INLINK to the Record."""
        self.links_in.append(link_in)

    def print_to_text(self: Record) -> str:
        """Print the records and its fields."""
        output = "record : " + self.record_name + " (" + self.record_type + ")\n"
        output += "Description : " + self.description + "\n"
        for name, value in self.fields:
            output += "Field : " + name + " = " + value + "\n"
        for linkin in self.links_in:
            if linkin is not None:
                output += (
                    "Link In: " + linkin.record_name + " " + linkin.type_link + "\n"
                )
        for linkout in self.links_out:
            if linkout is not None:
                output += (
                    "Link Out: " + linkout.record_name + " " + linkout.type_link + "\n"
                )
        for info in self.infos:
            output += "Info : " + info[0] + " , " + info[1]
        return output


class DbParser:
    """To handle tree-sitter parsing."""

    def __init__(self: DbParser) -> None:
        """Py Tree sitter configuration."""
        current_directory = Path(Path(__file__).resolve()).parent
        relative_path = Path(current_directory) / "tree-sitter-epics/epics-db"

        tree_sitter.Language.build_library(
            # Store the library in the `build` directory
            "build/my-languages.so",
            # Include one or more languages
            [relative_path],
        )
        db_language = tree_sitter.Language("build/my-languages.so", "epics_db")

        parser_tree = tree_sitter.Parser()
        parser_tree.set_language(db_language)
        self.parserTree = parser_tree
        self.tree = None
        self.root_node = None

    def parse(self: DbParser, text: str) -> None:
        """Parse the text in argument to build the tree of the object."""
        self.tree = self.parserTree.parse(bytes(text, "utf-8"))

    def build_fields(self: DbParser, node: any) -> list:
        """From a tree-sitter node built a list of tuple."""
        logging.info("Building Fields from node %s", node)
        field_name = ""
        field_value = ""
        link_in = None
        link_out = None
        for field_child in node:
            match field_child.type:
                case "field_name":
                    field_name = (field_child.text.decode("utf-8")).replace('"', "")
                case "string":
                    field_value = (field_child.text.decode("utf-8")).replace('"', "")

        if (
            field_name.startswith("INP") or field_name == "DOL"
        ) and not field_value.isdigit():
            link_in = Link()
            link_in = Link.create_link(field_value)
        if (
            field_name.startswith("OUT") or field_name == "FLNK"
        ) and not field_value.isdigit():
            link_out = Link()
            link_out = Link.create_link(field_value)
        return field_name, field_value, link_in, link_out

    def build_infos(self: DbParser, node: any) -> list:
        """From a tree-sitter node built a list of tuple."""
        logging.info("Building Infos from node ")
        info_name = node[2].text.decode("utf-8")
        info_value = node[4].text.decode("utf-8")
        return info_name, info_value

    def build_records_list(self: DbParser) -> list:
        """From a tree-sitter node built a list of object 'db' class."""
        logging.info("Building records from node")
        if self.tree is None:
            message = """
            Parser tree is empty. You need to parse a text before building records.
            """
            raise DbParserError(message)
        root_node = self.tree.root_node
        if root_node.has_error:
            message = "Syntax error: check syntax or if it is real EPICS databases."
            raise DbParserError(message)

        logging.info("Syntax analysing correct")
        record_list = []
        last_comment = ""
        for child in root_node.children:
            logging.debug("child.type : %s", child.type)
            match child.type:
                case "comment":
                    last_comment += child.text.decode("utf-8")
                    logging.debug("comment : %s", last_comment)
                case "record_instance":
                    logging.debug("record_instance")
                    fields = []
                    link_in = []
                    link_out = []
                    comment = last_comment
                    last_comment = ""
                    record_obj = Record()
                    for record_child in child.children:
                        match record_child.type:
                            case "record_type":
                                record_type = record_child.text.decode("utf-8")
                                record_obj.set_record_type(record_type)
                            case "record_name":
                                record_name = record_child.text.decode("utf-8")
                                record_obj.set_record_name(record_name)
                            case "field":
                                (
                                    f_name,
                                    f_value,
                                    f_link_in,
                                    f_link_out,
                                ) = self.build_fields(
                                    record_child.children,
                                )
                                fields.append((f_name, f_value))
                                if f_link_in is not None:
                                    link_in.append(f_link_in)
                                if f_link_out is not None:
                                    link_out.append(f_link_out)
                            case "info":
                                (
                                    f_name,
                                    f_value,
                                ) = self.build_infos(
                                    record_child.children,
                                )
                                record_obj.infos.append((f_name, f_value))
                    record_obj.set_description(comment)
                    record_obj.set_fields(fields)
                    record_obj.set_links_out(link_out)
                    record_obj.set_links_in(link_in)

                    record_list.append(record_obj)
        logging.debug("Found %i records : ", len(record_list))
        for record in record_list:
            logging.debug(record.print_to_text())
        return record_list
