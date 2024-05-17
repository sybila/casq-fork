import os
import re
from casq.aeonExport import write_aeon as write_aeon_2
from casq.celldesigner2qual import write_qual
from casq.readCD import read_celldesigner
from casq.simplify import simplify_model


# generate models
for filename in os.listdir(os.getcwd() + "/../cd_maps/"):
    with open(os.path.join(os.getcwd() + "/../cd_maps/", filename), 'r', encoding="utf-8") as f:
        info, width, height = read_celldesigner(f)
        simplify_model(info, [], [])
        # print(info)
        # print("Done")
        # write_bma("out_bma.json", info)
        # write_aeon_1("out_aeon.json", info)
        file_suf = filename.rsplit('.', 1)  # Split at only one dot, from the right
        file = file_suf[0]
        write_aeon_2("./../aeon_models/model_{fn}.aeon".format(fn=file), info)
        write_qual("./../aeon_models/model_{fn}.sbml".format(fn=file), info, "1000", "1000")



"""
with open('./test/format_aeon.xml','r',encoding="utf-8") as f:
    info, width, height = read_celldesigner(f)
    simplify_model(info, [], [])
    write_aeon_2("out_aeon.aeon", info)
"""


#  variable = ""


def count_parameters(var):
    nums = re.findall(r'\(\d+\)', var)
    dic = {}
    for num in nums:
        dic[num] = dic.get(num, 0) + 1

    print("occurrence: ")
    print(dic)


#  count_parameters(variable)
