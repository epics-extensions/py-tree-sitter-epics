from pathlib import Path

from py_tree_sitter_epics.epicsdb import (
    Database,
    Link,
    Record,
    parse_bytes,
    parse_file,
    parse_str,
)

# ruff: noqa: D103, S101


def test_parse_file(tmp_path: Path) -> None:
    db_text = """
record(calc, "${P}TEST:CALC") {}
"""
    db_file = tmp_path / "test.db"
    db_file.write_text(db_text)
    db = parse_file(db_file)
    assert db == Database(
        documentation=None,
        records=[
            Record(
                type="calc",
                name="${P}TEST:CALC",
                documentation=None,
                fields={},
                infos={},
            ),
        ],
    )


def test_parse_bytes() -> None:
    db_text = b"""
record(calc, "${P}TEST:CALC") {}
"""
    db = parse_bytes(db_text)
    assert db == Database(
        documentation=None,
        records=[
            Record(
                type="calc",
                name="${P}TEST:CALC",
                documentation=None,
                fields={},
                infos={},
            ),
        ],
    )


def test_parse() -> None:
    db = parse_str("""
#| Doc comment
#| line continuation

#| Unused comment
#| Unused comment

# Example database
record(ai, "TEST:VAL") {
    field(DESC, "My Description")
    field(EGU, "V")
    field(INP,  "SRC:INP PP")
    info("INFO1", "value1 input")
}

record(ao, "TEST:VAL_out") {
    info("INFO0", "value0 out")
    field(DESC, "My Description")
    field(EGU, "V")
    field(OUT,  "SRC:INP PP")
    info("INFO1", "value1 out")
}

record(calc, "${P}TEST:CALC") {}
""")
    assert db == Database(
        documentation="""Doc comment
line continuation""",
        records=[
            Record(
                type="ai",
                name="TEST:VAL",
                documentation="Example database",
                fields={
                    "DESC": "My Description",
                    "EGU": "V",
                    "INP": "SRC:INP PP",
                },
                infos={"INFO1": "value1 input"},
            ),
            Record(
                type="ao",
                name="TEST:VAL_out",
                documentation="My Description",
                fields={
                    "DESC": "My Description",
                    "EGU": "V",
                    "OUT": "SRC:INP PP",
                },
                infos={"INFO0": "value0 out", "INFO1": "value1 out"},
            ),
            Record(
                type="calc",
                name="${P}TEST:CALC",
                documentation=None,
                fields={},
                infos={},
            ),
        ],
    )


def test_links() -> None:
    db = parse_str("""
record(ai, "TEST:VAL") {
    field(DESC, "My Description")
    field(EGU, "V")
    field(INP,  "SRC:INP PP")
    info("INFO1", "value1 input")
}

record(ao, "TEST:VAL_out") {
    field(DESC, "My Description")
    field(EGU, "V")
    field(OUT,  "SRC:INP PP")
    info("INFO1", "value1 out")
}

record(calc, "TEST:CALC") {}
""")
    assert set(db.records[0].links_in) == {Link(record_name="SRC:INP", type_link="PP")}
    assert db.records[0].links_out == []
    assert db.records[1].links_in == []
    assert set(db.records[1].links_out) == {Link(record_name="SRC:INP", type_link="PP")}
    assert db.records[2].links_in == []
    assert db.records[2].links_out == []


def test_db_doc() -> None:
    db = parse_str("")
    assert db.documentation is None

    db = parse_str("# Hello")
    assert db.documentation is None

    db = parse_str("#| Hello")
    assert db.documentation == "Hello"

    db = parse_str("""
#| Hello
#| World
""")
    assert db.documentation == "Hello\nWorld"

    db = parse_str("""
# Hello
#| World
""")
    assert db.documentation == "World"

    db = parse_str("""
#| Hello
# World
""")
    assert db.documentation == "Hello"

    db = parse_str("""
# Hello
#| Hello
#| World
# World
""")
    assert db.documentation == "Hello\nWorld"
