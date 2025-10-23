import pytest
import logging
from pathlib import Path
from py_tree_sitter_epics.epicsdb import Record, DbParser, DbParserError


# Active le logging pendant les tests pour debug
logging.basicConfig(level=logging.DEBUG)


# ------------------------------------------------------
# Fichier EPICS de test
# ------------------------------------------------------

@pytest.fixture
def sample_db_file(tmp_path):
    """Crée un petit fichier EPICS .db de test temporaire."""
    db_text = """
# Example database
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

record(calc, "TEST:CALC") {
    field(DESC, "Calculation")
    field(INPA, "TEST:VAL")
    field(FLNK, "TEST:NEXT")
}
"""
    db_file = tmp_path / "test.db"
    db_file.write_text(db_text)
    return db_file


def test_parse_epics_db(sample_db_file):
    """Teste le parsing complet d’un fichier EPICS avec tree-sitter-epics."""
    record_parser = DbParser()
    with open(sample_db_file, "r", encoding="utf-8") as input_file:
        record_parser.parse(input_file.read())

    records = record_parser.build_records_list()

    # Vérifications de base
    assert isinstance(records, list)
    assert len(records) == 3

    record1 = records[0]
    record2 = records[1]
    record3 = records[2]

    # Record 1 : TEST:VAL
    assert record1.record_type == "ai"
    assert record1.record_name == "TEST:VAL"
    assert record1.unit == "V"
    assert any("DESC" in f for f in record1.fields)
    assert any("EGU" in f for f in record1.fields)
    assert len(record1.links_in) > 0


    # Record 2 : TEST:VAL_out
    assert record2.record_type == "ao"
    assert record2.record_name == "TEST:VAL_out"
    assert record2.unit == "V"
    assert any("DESC" in f for f in record2.fields)
    assert any("EGU" in f for f in record2.fields)
    assert len(record2.links_out) > 0

    # Record 2 : TEST:CALC
    assert record3.record_type == "calc"
    assert record3.record_name == "TEST:CALC"
    assert len(record3.links_in) >= 1


def test_parser_syntax_error(tmp_path):
    """Teste qu’une erreur de syntaxe déclenche bien une exception."""
    invalid_text = """
record(ai, "BROKEN:REC") {
    field(DESC, "No closing brace"
"""
    invalid_file = tmp_path / "invalid.db"
    invalid_file.write_text(invalid_text)

    parser = DbParser()
    parser.parse(invalid_file.read_text())

    # Comme la syntaxe est invalide, build_records_list doit lever une erreur
    with pytest.raises(DbParserError):
        parser.build_records_list()

