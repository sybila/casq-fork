import itertools

from casq.bmaExport import write_bma
from casq.aeonExportJSON import write_aeon as write_aeon_1
from casq.aeonExportAEON import write_aeon as write_aeon_2
from casq.readCD import read_celldesigner
from casq.simplify import simplify_model

for i in range(5):
    with open("test/cd_maps/map{i}.xml".format(i=i+1), "r", encoding="utf-8") as f:
        info, width, height = read_celldesigner(f)
        simplify_model(info, [], [])
        print(info)
        print("Done")
        # write_bma("out_bma.json", info)
        # write_aeon_1("out_aeon.json", info)
        write_aeon_2("./output/out_{i}".format(i=i+1), info)
