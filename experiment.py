from casq.bmaExport import write_bma
from casq.aeonExportJSON import write_aeon
from casq.aeonExportAEON import write_aeon_2
from casq.readCD import read_celldesigner
from casq.simplify import simplify_model

with open("test/map_mastcell.xml", "r", encoding="utf-8") as f:
    info, width, height = read_celldesigner(f)
    simplify_model(info, [], [])
    print(info)
    print("Done")
    write_bma("mapkX.json", info)
    write_aeon("mapkXaeon.json", info)
    write_aeon_2("mapk.aeon", info)