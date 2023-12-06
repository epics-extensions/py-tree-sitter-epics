"""Functions and classes for parsing from template/db files using tree-sitter-epics.

This module provides:
- PVParserError: exception raised by PVParser class.
- PV : python class to get PV information in a python object.
- PVParser : Python class to use easily py-tree-sitter en tree-sitter-epics
"""
import logging
import os

import tree_sitter


class SNLParserError(Exception):
    """SNLParserError class exception.

    Raised by SNL Parser class
    """

    def __init__(self: "SNLParserError", message: "str") -> None:
        super().__init__(message)


class program:
    """to represent a PV in python object."""

    def __init__(self: "program") -> None:
        """Initialize a city with a name and population."""
        logging.debug("program")

class SNLParser:
    """To handle tree-sitter parsing."""

    def __init__(self: "SNLParser") -> None:
        """Py Tree sitter configuration."""
        current_directory = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(current_directory, "tree-sitter-epics/snl")

        tree_sitter.Language.build_library(
            # Store the library in the `build` directory
            "build/my-languages.so",
            # Include one or more languages
            [relative_path],
        )
        snl_language = tree_sitter.Language("build/my-languages.so", "snl")

        parser_tree = tree_sitter.Parser()
        parser_tree.set_language(snl_language)
        self.parserTree = parser_tree
        self.tree = None
        self.root_node = None

    def parse(self: "PVParser", text: "str") -> None:
        """Parse the text in argument to build the tree of the object."""
        self.tree = self.parserTree.parse(bytes(text, "utf-8"))

    def build_pvs_list(self: "PVParser") -> list:  # noqa: C901, PLR0912
        """From a tree-sitter node built a list of object PV class."""
        logging.info("Building PVs from node")
        if self.tree is None:
            message = (
                "Parser tree is empty. You need to parse a text before building PVs."
            )
            raise PVParserError(message)
        root_node = self.tree.root_node
        if root_node.has_error:
            message = "Syntax error: check syntax or if it is real EPICS databases."
            raise PVParserError(message)

        logging.info("Syntax analysing correct")
        pv_list = []
        last_comment = ""
        for child in root_node.children:
            if child.type == "comment":
                last_comment += child.text.decode("utf-8")
            elif child.type == "record_instance":
                fields = []
                comment = last_comment
                last_comment = ""
                for record_child in child.children:
                    if record_child.type == "record_type":
                        record_type = record_child.text.decode("utf-8")
                    elif record_child.type == "record_name":
                        record_name = record_child.text.decode("utf-8")
                    elif record_child.type == "field":
                        field_name = ""
                        field_value = ""
                        for field_child in record_child.children:
                            if field_child.type == "field_name":
                                field_name = field_child.text.decode("utf-8")
                            if field_child.type == "string":
                                field_value = field_child.text.decode("utf-8")
                        if field_name == "DESC" and comment == "":
                            comment = field_value.replace('"', "")
                        fields.append((field_name, field_value))
                pv_obj = PV(record_type, record_name, fields, comment)
                pv_list.append(pv_obj)
        logging.debug("List of PVs found ")
        for pv in pv_list:
            logging.debug(pv.print_to_text())
        return pv_list
