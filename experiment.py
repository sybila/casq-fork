from casq.bmaExport import write_bma
from casq.readCD import read_celldesigner
from casq.simplify import simplify_model

with open("test/map_mastcell.xml", "r", encoding="utf-8") as f:
    info, width, height = read_celldesigner(f)
    simplify_model(info, [], [])
    print(info)
    write_bma("test/mapk.json", info)