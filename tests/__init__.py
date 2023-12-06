from pathlib import Path
from py_tree_sitter_epics.PV import PVParser, PVParserError

try:
    with Path.open("misc/example.template") as file:
        code = file.read()
    PVParser = PVParser()
    PVParser.parse(code)
    pv_list = PVParser.build_pvs_list()
  
    print("number of pvs : ",len(pv_list))
    for pv_obj in pv_list:
        output_str = pv_obj.print_to_text() 
        print(output_str)


except OSError as e:
    print(f"An error occurred: {e}")
except PVParserError:
    print("pv parser error")