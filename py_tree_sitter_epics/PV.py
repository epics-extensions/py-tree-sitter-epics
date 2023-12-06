"""Functions and classes for parsing from template/db files using tree-sitter-epics.

This module provides:
- PVParserError: exception raised by PVParser class.
- PV : python class to get PV information in a python object.
- PVParser : Python class to use easily py-tree-sitter en tree-sitter-epics
"""
import logging
import os

import tree_sitter


class PVParserError(Exception):
    """PVParser class exception.

    Raised by PV Parser class
    """

    def __init__(self: "PVParserError", message: "str") -> None:
        """test."""
        super().__init__(message)


class PV:
    """to represent a PV in python object."""

    def __init__(
        self: "PV",
        record_type: "str",
        record_name: "str",
        fields: "tuple",
        description: "str",
    ) -> None:
        """Initialize a city with a name and population."""
        self.record_type = record_type
        self.record_name = record_name
        self.fields = fields
        self.description = description.replace("#", "")

        logging.debug("PV : %s (%s)", record_name, record_type)
        logging.debug("Description : %s", description)
        has_unit = False
        for name, value in fields:
            logging.debug("Field : %s = %s", name, value)
            if name == "EGU":
                self.unit = value
                has_unit = True
        if not has_unit:
            self.unit = ""

    def print_to_text(self: "PV") -> str:
        """Print the PVs and its fields."""
        output = "PV : " + self.record_name + " (" + self.record_type + ")\n"
        output += "Description : " + self.description + "\n"
        for name, value in self.fields:
            output += "Field : " + name + " = " + value + "\n"
        return output


class PVParser:
    """To handle tree-sitter parsing."""

    def __init__(self: "PVParser") -> None:
        """Py Tree sitter configuration."""
        current_directory = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(current_directory, "tree-sitter-epics/epics-db")

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

    def parse(self: "PVParser", text: "str") -> None:
        """Parse the text in argument to build the tree of the object."""
        self.tree = self.parserTree.parse(bytes(text, "utf-8"))

    def build_fields(self: "PVParser",node)-> list:
        logging.info("Building Fields from node")
        """From a tree-sitter node built a list of tuple."""
        field_name = ""
        field_value = ""
        for field_child in node:
            match field_child.type:
                case "field_name":
                    field_name = field_child.text.decode("utf-8")
                case "string":
                    field_value = field_child.text.decode("utf-8")
        return field_name, field_value

    def build_pvs_list(self: "PVParser") -> list:
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
            logging.debug("child.type : %s",child.type)
            match child.type:
                case "comment":
                    last_comment += child.text.decode("utf-8")
                    logging.debug("comment : %s",last_comment)
                case "record_instance":

                    logging.debug("record_instance")
                    fields = []
                    comment = last_comment
                    last_comment = ""
                    for record_child in child.children:
                        match record_child.type:
                            case "record_type":
                                record_type = record_child.text.decode("utf-8")
                            case "record_name":
                                record_name = record_child.text.decode("utf-8")
                            case "field":
                                f_name, f_value = self.build_fields(
                                    record_child.children,
                                )
                                if f_name == "DESC" and comment == "":
                                    comment = f_value.replace('"', "")
                                fields.append((f_name, f_value))
                    pv_obj = PV(record_type, record_name, fields, comment)
                    pv_list.append(pv_obj)
        logging.debug("Found %i PVS : ",len(pv_list))
        for pv in pv_list:
            logging.debug(pv.print_to_text())
        return pv_list
