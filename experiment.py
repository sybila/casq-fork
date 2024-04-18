import itertools

from CaSQ.bmaExport import write_bma
from CaSQ.aeonExportJSON import write_aeon
from CaSQ.aeonExportAEON import write_aeon_2
from CaSQ.readCD import read_celldesigner
from CaSQ.simplify import simplify_model

with open("test/map_mastcell.xml", "r", encoding="utf-8") as f:
    info, width, height = read_celldesigner(f)
    simplify_model(info, [], [])
    print(info)
    print("Done")
    write_bma("mapkX.json", info)
    write_aeon("mapkXaeon.json", info)
    write_aeon_2("mapk.aeon", info)

    count = 0
    a = itertools.count()
    for i in range(0,4):
        count = next(a)
    print(count)