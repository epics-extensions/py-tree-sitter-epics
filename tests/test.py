from pathlib import Path

from py_tree_sitter_epics.epicsdb import DbParser, DbParserError

try:
    with Path.open("misc/example.template") as file:
        code = file.read()
    db_parser = DbParser()
    db_parser.parse(code)
    record_list = db_parser.build_records_list()

    print("number of records : ", len(record_list))
    for record_obj in record_list:
        output_str = record_obj.print_to_text()
        print(output_str)


except OSError as e:
    print(f"An error occurred: {e}")
except DbParserError:
    print("pv parser error")
