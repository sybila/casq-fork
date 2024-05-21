import os
import re
from casq.aeonExport import write_aeon
from casq.celldesigner2qual import write_qual
from casq.readCD import read_celldesigner
from casq.simplify import simplify_model

"""
# generate models
for filename in os.listdir(os.getcwd() + "/../cd_maps/"):
    with open(os.path.join(os.getcwd() + "/../cd_maps/", filename), 'r', encoding="utf-8") as f:
        info, width, height = read_celldesigner(f)
        simplify_model(info, [], [])
        # print(info)
        # print("Done")
        # write_bma("out_bma.json", info)
        file_suf = filename.rsplit('.', 1)  # Split at only one dot, from the right
        file = file_suf[0]
        write_aeon("./../aeon_models/model_{fn}.aeon".format(fn=file), info)
        write_qual("./../aeon_models/model_{fn}.sbml".format(fn=file), info, "1000", "1000")
"""


"""
with open('./test/format_aeon.xml','r',encoding="utf-8") as f:
    info, width, height = read_celldesigner(f)
    simplify_model(info, [], [])
    write_aeon("out_aeon.aeon", info)
"""


variable = "cat_Btk_phosphorylated_Cytosol_42(1), cat_Btk_phosphorylated_Cytosol_43(1), cat_Ca2__ion_34(1), cat_Ca2__ion_35(1), cat_Ca2_space_channel_36(1), cat_Calmodulin_Calcineurin_complex_19(2), cat_Cbp_PAG_phosphorylated_palmytoylated_69(1), cat_DAG_simple_molecule_65(2), cat_Elk1_phosphorylated_53(3), cat_Erk_MAPK1_3__phosphorylated_49(2), cat_Fc_gamma_RIIB_phosphorylated_66(1), cat_FceRI_Syk_complex_Cytosol_1_24(1), cat_FceRI_Syk_complex_Cytosol_1_25(1), cat_FceRI_phosphorylated_phosphorylated_46(1), cat_Fos_phosphorylated_68(1), cat_Fyn_phosphorylated_phosphorylated_palmytoylated_62(1), cat_Gab2_phosphorylated_51(1), cat_IKK_Beta_phosphorylated_39(1), cat_IP3_simple_molecule_57(2), cat_I_kappa_Beta___F_kappa_B_complex_32(1), cat_JNK_phosphorylated_70(2), cat_LAT1_phosphorylated_phosphorylated_phosphorylated_phosphorylated_palmytoylated_54(1), cat_LAT2_phosphorylated_palmytoylated_47(2), cat_MEK1_MAP2K1__phosphorylated_50(1), cat_MEK2_MAP2K2__phosphorylated_41(1), cat_MEK4_MAP2K4__phosphorylated_61(1), cat_MEKK1_MAP3K1__phosphorylated_74(1), cat_MKK7_MAP2K7__phosphorylated_67(1), cat_NFAT_Cytosol_73(1), cat_PIP3_Akt_complex_8(1), cat_PIP3_simple_molecule_55(1), cat_PLCG1_phosphorylated_64(1), cat_SHIP_1_phosphorylated_52(1), cat_SLP_76_phosphorylated_40(1), cat_SOS_Grb2_complex_5(1), cat_Shc_phosphorylated_56(2), cat_c_JUN_phosphorylated_nucleus_1_59(1)"


def count_parameters(var):
    nums = re.findall(r'\(\d+\)', var)
    dic = {}
    for num in nums:
        dic[num] = dic.get(num, 0) + 1

    print("occurrence: ")
    print(dict(sorted(dic.items())))


count_parameters(variable)
