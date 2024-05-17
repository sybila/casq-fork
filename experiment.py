import itertools
import os
import re
from casq.bmaExport import write_bma
from casq.aeonExportAEON import write_aeon as write_aeon_2
from casq.celldesigner2qual import write_qual
from casq.readCD import read_celldesigner
from casq.simplify import simplify_model


for filename in os.listdir(os.getcwd() + "/cd_maps/"):
    with open(os.path.join(os.getcwd() + "/cd_maps/", filename), 'r', encoding="utf-8") as f:
        info, width, height = read_celldesigner(f)
        simplify_model(info, [], [])
        # print(info)
        # print("Done")
        # write_bma("out_bma.json", info)
        # write_aeon_1("out_aeon.json", info)
        file_suf = filename.rsplit('.', 1)  # Split at only one dot, from the right
        file = file_suf[0]
        write_aeon_2("./aeon_models/model_{fn}.aeon".format(fn=file), info)
        write_qual("./aeon_models/model_{fn}.sbml".format(fn=file), info, "1000", "1000")


"""
with open('./test/format_aeon.xml','r',encoding="utf-8") as f:
    info, width, height = read_celldesigner(f)
    simplify_model(info, [], [])
    write_aeon_2("out_aeon.aeon", info)
"""
"""
with open('./zjednodusenie/step_three.xml','r',encoding="utf-8") as f:
    info, width, height = read_celldesigner(f)
    simplify_model(info, [], [])
    write_aeon_2("./zjednodusenie/step_three_aeon", info)
"""

"""
str="cat_16_17S_DHA_Epoxide_simple_molecule_970(1), cat_17S_HpDHA_simple_molecule_969(1), cat_1_3_BPG_simple_molecule_370(1), cat_1_Met_simple_molecule_598(1), cat_24_OH_Chol_simple_molecule_neuron_353(1), cat_3_mercaptopyruvate_simple_molecule_mitochondria_538(1), cat_3_mercaptopyruvate_simple_molecule_neuron_526(1), cat_50kDa_fragment_856(1), cat_5ADHP_simple_molecule_mitochondia_830(1), cat_5ADHP_simple_molecule_mitochondria_828(1), cat_5ADHP_simple_molecule_mitochondria_829(1), cat_5_GMP_simple_molecule_postsynaptic_density_495(1), cat_5_GMP_simple_molecule_presynaptic_terminal_484(1), cat_5_HT_simple_molecule_601(3), cat_5_MTHF_simple_molecule_597(1), cat_60S_587(1), cat_A2MLRP_complex_214(1), cat_AA_simple_molecule_312(1), cat_AA_simple_molecule_313(2), cat_ABCA1_354(1), cat_ACO1_583(2), cat_ACTA1_rna_518(2), cat_ACh_production_phenotype_878(1), cat_ADAM_default_compartment_236(1), cat_AICD_default_compartment_1009(1), cat_AICD_neuron_238(1), cat_AICD_neuron_239(1), cat_AICD_neuron_240(1), cat_AKT1_694(2), cat_AKT1_phosphorylated_phosphorylated_842(5), cat_ALB_477(1), cat_ALLOP_simple_molecule_astrocyte_838(1), cat_AMPAR_983(1), cat_AP1_microglia_907(3), cat_AP1_nucleus_736(2), cat_APAF1_328(1), cat_APC_AXIN_GSK3B_CTNNB1_complex_neuron_1_36(1), cat_APC_AXIN_GSK3B_CTNNB1_complex_neuron_34(5), cat_APC_GSK3B_AXIN_CTNNB1_complex_31(1), cat_APC_GSK3B_AXIN_CTNNB1_complex_32(1), cat_APC_GSK3B_AXIN_CTNNB1_complex_33(1), cat_APOE_LRP_complex_213(1), cat_APOE_cholesterol_complex_neuron_205(1), cat_APOE_rna_517(2), cat_APP_ACO1_Fe_complex_77(3), cat_APP_PCBP2_PCBP1_FMR1_60S_40S_complex_82(2), cat_APP_neuron_234(1), cat_ARL4C_759(1), cat_ATG13_phosphorylated_706(2), cat_ATG3_717(1), cat_ATP2_797(1), cat_ATP_396(1), cat_ATP_simple_molecule_default_compartment_798(2), cat_Abnormal_cell_function_phenotype_854(1), cat_Abnormal_ceramide_accumulation_phenotype_849(5), cat_Acetate_simple_molecule_365(2), cat_AmyloidB1_40_Lipid_raft_1008(1), cat_AmyloidB1_40_default_compartment_237(1), cat_AmyloidB1_42_default_compartment_1_504(4), cat_AmyloidB1_42_default_compartment_225(1), cat_AmyloidB1_42_microglia_508(1), cat_AmyloidB_Brain_605(1), cat_AmyloidB_aggregation_phenotype_1003(1), cat_AmyloidB_blood_brain_barrier__BBB__608(1), cat_AmyloidB_blood_brain_barrier__BBB__609(1), cat_AmyloidB_clearance_phenotype_neuron_1002(2), cat_AmyloidB_clearance_phenotype_nucleus_725(1), cat_AmyloidB_default_compartment_474(1), cat_AmyloidB_default_compartment_475(1), cat_AmyloidB_deposit_phenotype_933(1), cat_AmyloidB_fibril_formation_phenotype_327(1), cat_AmyloidB_microglia_912(5), cat_AmyloidB_neuron_267(1), cat_AmyloidB_production_increase_phenotype_1004(1), cat_Apoptosis_phenotype_894(11), cat_Axon_pruning__Neuronal_culling_phenotype_346(1), cat_BAD_223(1), cat_BAX_662(1), cat_BCL2_678(1), cat_BER_phenotype_358(2), cat_BID_226(1), cat_C1_467(1), cat_C2_465(1), cat_C31_855(1), cat_C3_rna_510(1), cat_C83_235(2), cat_C99_Lipid_raft_1006(1), cat_C99_default_compartment_820(4), cat_CACNA1_231(1), cat_CAMK2_neuron_1_981(2), cat_CAMK2_neuron_684(1), cat_CAPN_220(1), cat_CASK_815(1), cat_CASP12_292(2), cat_CASP1_microglia_939(1), cat_CASP1_neuron_653(1), cat_CASP3_293(5), cat_CASP6_360(1), cat_CASP7_361(1), cat_CBS_548(2), cat_CCND1_rna_688(1), cat_CCNE_300(1), cat_CDC42_GGPP_complex_138(1), cat_CDK5_DCTN5_complex_104(1), cat_CDK5_DCTN5_complex_105(2), cat_CDKN1A_303(2), cat_CN_982(1), cat_CO2_simple_molecule_383(1), cat_CO2_simple_molecule_384(1), cat_COX_827(2), cat_CREB_979(1), cat_CSNK1A1_629(1), cat_CTNNB1_neuron_408(1), cat_CTNNB1_neuron_409(1), cat_CTNNB1_ubiquitinated_phosphorylated_679(2), cat_CYC_neuron_296(2), cat_CYC_ubiquitinated_295(1), cat_C_terminal_of_p35_270(2), cat_Ca2__increase_phenotype_891(1), cat_Ca2__ion_astrocyte_869(1), cat_Ca2__ion_default_compartment_257(2), cat_Ca2__ion_endoplasmic_reticulum_ER__261(2), cat_Ca2__ion_neuron_254(3), cat_Ca2__ion_neuron_255(8), cat_Ca2__ion_neuron_256(3), cat_Ca2__ion_postsynaptic_density_559(1), cat_Caspase_cascade_phenotype_893(1), cat_Cell_Death_phenotype_259(13), cat_Choline_simple_molecule_366(2), cat_Cl__ion_558(1), cat_Cys_S_R_simple_molecule_529(1), cat_Cytokine_upregulation_phenotype_511(1), cat_DAB1_696(4), cat_DAG_IP3_complex_93(2), cat_DAG_simple_molecule_neuron_1_841(1), cat_DA_simple_molecule_600(3), cat_DHA_simple_molecule_968(1), cat_DMAPP_simple_molecule_751(1), cat_DNA_damage_phenotype_282(2), cat_DNA_fragmentation_phenotype_652(1), cat_DVL_phosphorylated_404(1), cat_EDN1_rna_624(1), cat_EGF_EGFR_complex_neuron_1_180(2), cat_EIF2AK3_phosphorylated_endoplasmic_reticulum_ER__288(1), cat_EIF2A_phosphorylated_764(1), cat_Eicosanoid_simple_molecule_890(2), cat_F2A_isoprostanes_simple_molecule_668(2), cat_FOXO_748(1), cat_FPRL1_microglia_928(3), cat_FPRL1_rna_931(2), cat_FTH_ACO1_IREB2_Fe_complex_75(2), cat_FTH_PCBP2_40S_60S_complex_78(2), cat_FYN_neuron_676(1), cat_FZD_WNT_LRP5_6_complex_51(1), cat_Farnesyl_PP_simple_molecule_454(1), cat_Fe_simple_molecule_default_compartment_791(1), cat_Fe_simple_molecule_neuron_574(1), cat_Fru6P_simple_molecule_992(1), cat_G0_phenotype_301(1), cat_G1_S_checkpoint_phenotype_888(1), cat_G1_phenotype_400(1), cat_G2_M_checkpoint_phenotype_887(1), cat_G2_phenotype_397(1), cat_GABARAPL2_715(2), cat_GABA_GABR_complex_52(1), cat_GDP_simple_molecule_772(1), cat_GGPP_simple_molecule_456(1), cat_GLUT_997(1), cat_GNAQ_243(1), cat_GPCR_homolog_neuron_1_253(1), cat_GPP_simple_molecule_754(1), cat_GRI_glutamate_complex_107(1), cat_GSH_simple_molecule_810(1), cat_GSK3B_phosphorylated_265(2), cat_GSSG_HS__simple_molecule_544(1), cat_GSSG_simple_molecule_809(1), cat_GTPase_GDI_complex_146(1), cat_GTPase_neuron_683(1), cat_GTPase_phosphorylated_833(1), cat_Generation_of_reactive_oxygen_species_phenotype_326(3), cat_Glc6P_simple_molecule_991(1), cat_GlcNAc1P_simple_molecule_995(1), cat_GlcNAc6P_simple_molecule_994(1), cat_GlcNH26P_simple_molecule_993(1), cat_Glyceraldehyde_P_simple_molecule_369(2), cat_H2O2_simple_molecule_default_compartment_247(2), cat_H2O2_simple_molecule_neuron_669(1), cat_H2O_simple_molecule_inner_membrane_395(1), cat_H2O_simple_molecule_neuron_808(2), cat_HIF_785(1), cat_HK_367(1), cat_HMGB1_neuron_885(1), cat_HMG_CoA_simple_molecule_446(1), cat_HPETE_simple_molecule_323(2), cat_HRK_rna_659(1), cat_HSP60_948(1), cat_HSPA5_rna_767(2), cat_HS__ion_mitochondria_553(1), cat_HS__ion_neuron_549(1), cat_HS__ion_neuron_550(1), cat_HS__ion_neuron_551(1), cat_HS__ion_neuron_552(1), cat_H__ion_inner_membrane_392(1), cat_H__ion_mitochondria_391(3), cat_ICAM1_rna_625(1), cat_IDE_default_compartment_248(1), cat_IGF1R_693(1), cat_IKBK_phosphorylated_670(6), cat_IK_unknown_796(1), cat_IL1B_rna_astrocyte_913(1), cat_IL1B_rna_microglia_903(2), cat_IL1B_rna_nucleus_965(1), cat_IL1_rna_neuron_512(1), cat_IL6_blood_brain_barrier__BBB__620(1), cat_IL6_microglia_720(2), cat_IL6_neuron_882(2), cat_IL6_rna_902(2), cat_IPP_simple_molecule_451(1), cat_IRF_936(1), cat_IRS1_987(1), cat_IRS_747(1), cat_ITAM_complex_neuron_144(1), cat_ITPR_IP3_complex_7(2), cat_Inflammation_phenotype_283(4), cat_Inflammatory_signaling_phenotype_977(4), cat_Inflammatory_stimulus_for_Normal_Neuron_phenotype_308(1), cat_Insulin_IR_complex_neuron_1_218(1), cat_Insulin_IR_complex_neuron_217(1), cat_JAK2_675(1), cat_JUN_phosphorylated_655(1), cat_KCN_794(1), cat_K__ion_default_compartment_555(1), cat_K__ion_default_compartment_556(1), cat_K__ion_neuron_795(1), cat_Kv3_4_rna_962(1), cat_LIN7_818(1), cat_LOO_simple_molecule_742(2), cat_LO_simple_molecule_813(2), cat_LTP_impairment_phenotype_967(1), cat_L_Cit_simple_molecule_488(1), cat_L_Cysteinesulfinate_simple_molecule_neuron_521(1), cat_L_Cystine_simple_molecule_525(1), cat_Lipid_peroxidation_phenotype_284(3), cat_Lipid_raft__increase_phenotype_1005(2), cat_Lipoprotein_remnant_simple_molecule_default_compartment_651(4), cat_MAC_961(1), cat_MAC__membrane_attack_complex_complex_12(1), cat_MAP2K1_701(1), cat_MAP2K3_phosphorylated_640(1), cat_MAP2K4_phosphorylated_656(1), cat_MAP2K6_phosphorylated_644(1), cat_MAP2K7_phosphorylated_660(1), cat_MAP2K_735(1), cat_MAP3K9_10_11_phosphorylated_657(2), cat_MAP3K_637(2), cat_MAPK11_phosphorylated_639(2), cat_MAPK12_phosphorylated_642(2), cat_MAPK13_phosphorylated_643(2), cat_MAPK14_phosphorylated_636(2), cat_MAPK1_3_phosphorylated_294(5), cat_MAPK8_phosphorylated_473(9), cat_MAPK_phenotype_677(3), cat_MAPK_signaling_pathway_phenotype_951(1), cat_MAPT__neuron_263(1), cat_MAPT_phosphorylated_neuron_1_271(1), cat_MAPT_phosphorylated_neuron_264(8), cat_MAPT_phosphorylated_neuron_2_634(1), cat_MIF_884(1), cat_MMP9_438(1), cat_MMP_rna_568(2), cat_MTOR_704(2), cat_MY_681(1), cat_M_phenotype_299(2), cat_Met_simple_molecule_468(3), cat_Mevalonate_5_phosphate_simple_molecule_449(1), cat_Mevalonate_PP_simple_molecule_450(1), cat_Mg2__ion_673(1), cat_Microglia_Activation_phenotype_306(9), cat_Mitochondrial_dysfunction_phenotype_inner_membrane_260(5), cat_Mitochondrial_dysfunction_phenotype_neuron_892(1), cat_Modulation_of_gene_expression__phenotype_258(2), cat_N1_466(1), cat_N2_464(1), cat_NADH_simple_molecule_default_compartment_857(1), cat_NADH_simple_molecule_mitochondia_444(1), cat_NADH_simple_molecule_mitochondria_442(1), cat_NADH_simple_molecule_mitochondria_443(1), cat_NADH_simple_molecule_neuron_382(1), cat_NADP__simple_molecule_441(1), cat_NAD__simple_molecule_inner_membrane_388(1), cat_NALP1_958(1), cat_NALP3_938(1), cat_NEDD8_411(1), cat_NFAT_neuron_761(1), cat_NFKB1_617(1), cat_NFKB1_RELA_complex_neuron_176(3), cat_NFKBI_671(1), cat_NFKBI_NFKB1_RELA_complex_neuron_1_106(2), cat_NFKB_microglia_908(3), cat_NFKB_microglia_909(2), cat_NFKB_neuron_879(1), cat_NFKB_responsive_genes_rna_434(2), cat_NFKB_responsive_genes_rna_435(3), cat_NFKB_responsive_genes_rna_436(1), cat_NF_KB_responsive_phenotype_692(1), cat_NGF_default_compartment_439(1), cat_NH3_simple_molecule_528(1), cat_NICD_neuron_430(1), cat_NMDAR_neuron_1_984(1), cat_NOS_487(1), cat_NOS_phosphorylated_274(5), cat_NOTCH_ectodomain_Delta_complex_166(1), cat_NO_simple_molecule_default_compartment_491(1), cat_NO_simple_molecule_default_compartment_492(1), cat_NO_simple_molecule_default_compartment_493(1), cat_NO_simple_molecule_neuron_275(2), cat_NO_simple_molecule_postsynaptic_density_489(1), cat_NPD1_simple_molecule_971(1), cat_NR1_NR2BR_985(3), cat_Na__ion_default_compartment_557(1), cat_Na__ion_neuron_800(1), cat_Na__ion_neuron_801(1), cat_Na__ion_postsynaptic_density_554(1), cat_Necrosis_phenotype_919(2), cat_Nerve_regeneration_phenotype_978(1), cat_Neuro_toxicity_phenotype_341(2), cat_Neurofibrillary_tangles_NFTs__phenotype_273(2), cat_Neuronal_injury_phenotype_232(3), cat_Notch_site2_cleavaged_protein_428(2), cat_Notch_site3_cleavaged_protien_429(1), cat_O_GlcNAcylated_MAPT_999(1), cat_Oligomeric_AmyloidB_neuron_252(1), cat_PCBP1_579(2), cat_PDH_376(1), cat_PDH_phosphorylated_378(1), cat_PDH_rna_379(1), cat_PDK1_phosphorylated_418(1), cat_PEBP1_phosphorylated_702(1), cat_PE_GABARAPL2_complex_132(1), cat_PE_simple_molecule_718(2), cat_PFK_368(1), cat_PGG2_simple_molecule_314(1), cat_PGK_371(1), cat_PIK3_417(11), cat_PIP3_simple_molecule_285(1), cat_PKC_998(2), cat_PKC_response_phenotype_700(1), cat_PK_728(1), cat_PLA2G1B_807(1), cat_PLCB_251(3), cat_PLCG_845(2), cat_PP1_980(2), cat_PPARG_ligand_926(1), cat_PPARG_rna_687(1), cat_PPP3_760(2), cat_PRIM1_PCLB_APEX1_POLD1_complex_25(1), cat_PRKAA2_781(1), cat_PRKC_phosphorylated_633(7), cat_PRKG1_neuron_792(1), cat_PSMD9_399(1), cat_PS_exposure_phenotype_853(1), cat_PTEN_749(1), cat_PTGS2_rna_309(1), cat_Phagocytosis_phenotype_509(2), cat_Plasmin_437(1), cat_Proinflammetion_phenotype_896(1), cat_Protein_Oxidation_phenotype_279(2), cat_Q_simple_molecule_393(1), cat_Q_simple_molecule_394(1), cat_RAC1_GGPP_complex_139(1), cat_RAF1_565(2), cat_RAF1_566(1), cat_RARE_target_genes_rna_844(1), cat_RAS_564(2), cat_RAS_Farnesyl_PP_complex_140(1), cat_RHOA_680(1), cat_RHOA_GGPP_complex_137(1), cat_RIPK2_942(2), cat_ROS_simple_molecule_blood_brain_barrier__BBB__616(1), cat_ROS_simple_molecule_default_compartment_900(1), cat_ROS_simple_molecule_default_compartment_901(1), cat_ROS_simple_molecule_microglia_875(2), cat_ROS_simple_molecule_microglia_876(1), cat_RPS6KA1_783(1), cat_RPS6KB_788(1), cat_RYR3_262(2), cat_R_S_simple_molecule_545(1), cat_SAMe_simple_molecule_599(2), cat_SFK_695(2), cat_SMPD_733(1), cat_SPHK1_729(1), cat_SRC_562(1), cat_ST8SIA1_rna_689(1), cat_STXBP1_814(1), cat_STX_816(1), cat_S_phenotype_398(2), cat_Senile_plaque_phenotype_246(2), cat_SolublePRNP_463(1), cat_Squalene_simple_molecule_455(1), cat_Synaptic_suppression_phenotype_347(1), cat_TCA_cycle_phenotype_380(3), cat_TF_Fe_complex_68(1), cat_TF_default_compartment_790(1), cat_TIMP1_330(2), cat_TIMP1_333(1), cat_TIMP1_334(1), cat_TIMP1_335(2), cat_TIMP1_337(2), cat_TIMP1_338(1), cat_TNFA_default_compartment_986(2), cat_TNFA_rna_astrocyte_915(1), cat_TNFA_rna_microglia_905(2), cat_TNFRSF1A_249(1), cat_TNF_blood_brain_barrier__BBB__822(1), cat_TNF_microglia_823(1), cat_TNF_neuron_886(1), cat_TP53_221(2), cat_TRNAU1_rna_don_t_care_752(1), cat_TSC_777(3), cat_TTR_478(1), cat_TUB_419(2), cat_TUB_phosphorylated_420(1), cat_TUB_phosphorylated_421(2), cat_UBE2M_ROC1_UBE2_NEDD8_CUL_SKP1_FBXO_complex_41(1), cat_UB_Unknown_complex_83(1), cat_UB_neuron_1_426(1), cat_UB_neuron_412(2), cat_UDP_GlcNAc_simple_molecule_996(1), cat_UDP_simple_molecule_1000(1), cat_UQCR_390(2), cat_Unknown_CASP_362(1), cat_Unknown_TF_843(1), cat_Unknown_Wnt_target_genes_rna_405(1), cat_Unknown_transportation_phenotype_850(5), cat_VCAM1_rna_626(1), cat_VEGFA_786(1), cat_WISP1_635(1), cat_WNT_default_compartment_401(1), cat_WNT_rna_685(1), cat_XBP1_766(2), cat_ZAP70_phosphorylated_860(1), cat_acetylcholine_simple_molecule_363(1), cat_acetylcholine_simple_molecule_364(1), cat_actin_organization_phenotype_682(1), cat_activate_astrocyte_phenotype_917(2), cat_activate_microglia_inflammatory_processes_phenotype_302(3), cat_activate_microglia_phenotype_910(3), cat_activation_of_membrane_proteins_phenotype_744(1), cat_aldehydes_phenotype_746(1), cat_apoptosis_phenotype_281(10), cat_autophagosome_formation_phenotype_714(2), cat_autophagy_induction_phenotype_708(1), cat_axonal_transport_phenotype_698(1), cat_biological_damage_phenotype_472(1), cat_cAMP_simple_molecule_486(1), cat_cGMP_simple_molecule_neuron_793(1), cat_cGMP_simple_molecule_postsynaptic_density_496(1), cat_cGMP_simple_molecule_presynaptic_terminal_483(1), cat_cell_surviving_response_phenotype_935(2), cat_ceramide_simple_molecule_731(3), cat_chemotaxis_simple_molecule_929(1), cat_cholesterol_simple_molecule_astrocyte_352(1), cat_cholesterol_simple_molecule_neuron_1_349(1), cat_cognitive_and_behavioral_abnormalities_phenotype_664(1), cat_complement_system_phenotype_960(2), cat_create_AB_channel_phenotype_953(1), cat_cytoaarchitectural_integrity_phenotype_697(1), cat_cytokines_932(1), cat_decreased_energy_production_phenotype_241(1), cat_dedifferentiation_phenotype_298(2), cat_depolarization_phenotype_804(1), cat_destruction_of_membranes_phenotype_745(1), cat_differentiation_phenotype_480(2), cat_dystrophic_neurites_phenotype_503(1), cat_estrogen_simple_molecule_default_compartment_415(1), cat_expression_phenotype_304(1), cat_geranyl_geraniol_simple_molecule_356(1), cat_glucose_simple_molecule_990(3), cat_glutamate_GRIN_complex_neuron_109(1), cat_glutamate_simple_molecule_neuron_1001(1), cat_hypotaurine_simple_molecule_522(1), cat_increase_NFKBIA_NFKBIB_phenotype_724(1), cat_inflammasome_941(2), cat_inflammation_phenotype_microglia_937(3), cat_inflammation_phenotype_neuron_966(3), cat_inflammatory_response_phenotype_862(1), cat_learning_and_memory_phenotype_848(1), cat_lipid_radical_cycles_phenotype_743(1), cat_memory_phenotype_499(1), cat_mevalonic_acid_simple_molecule_447(1), cat_microtubules_complex_46(1), cat_neurite_outgrouth_phenotype_950(1), cat_neuro_toxicity_phenotype_667(3), cat_neurodegeneration_phenotype_427(1), cat_neuronal_cell_death_phenotype_663(1), cat_neuronal_development_phenotype_627(1), cat_neurotoxic_effect_phenotype_952(1), cat_neurotoxin_phenotype_874(5), cat_oxidative_stress_phenotype_default_compartment_889(1), cat_oxidative_stress_phenotype_neuron_661(1), cat_oxyradical_simple_molecule_806(2), cat_p3_846(1), cat_paired_helical_filaments_PHFs__phenotype_272(1), cat_phagocytosis_phenotype_930(2), cat_posttranslational_modification_of_APP_and_tau_phenotype_305(1), cat_preautophagosomal_membrane_phenotype_713(1), cat_processing_phenotype_865(1), cat_proinflammation_phenotype_934(2), cat_proliferation_phenotype_727(1), cat_protein_phosphorylation_phenotype_500(1), cat_protein_synthesis_phenotype_497(1), cat_protein_trafficking_phenotype_819(1), cat_pyruvate_simple_molecule_default_compartment_372(1), cat_pyruvate_simple_molecule_mitochondria_541(1), cat_pyruvate_simple_molecule_mitochondria_542(1), cat_pyruvate_simple_molecule_neuron_374(1), cat_pyruvate_simple_molecule_neuron_375(1), cat_recruitment_of_microglia_phenotype_307(1), cat_release_free_radicals_phenotype_847(1), cat_sAPPA_758(2), cat_sAPPB_Lipid_raft_1007(1), cat_sAPPB_default_compartment_821(4), cat_sLRP_612(1), cat_selective_chaperone_translation_phenotype_765(1), cat_speck_like_protein_911(1), cat_sphingomyelin_hydroxylated_880(1), cat_sphingoshine1_P_simple_molecule_1011(1), cat_sphingosine_simple_molecule_730(1), cat_succinate_simple_molecule_385(1), cat_sulfate_simple_molecule_546(1), cat_sulfinyl_pyruvate_simple_molecule_547(1), cat_sulfite_simple_molecule_mitochondria_534(1), cat_sulfite_simple_molecule_mitochondria_535(1), cat_sulfite_simple_molecule_neuron_531(1), cat_survival_phenotype_482(4), cat_synaptic_dysfunction_phenotype_502(1), cat_synaptic_plasticity_phenotype_neuron_699(2), cat_synaptic_plasticity_phenotype_postsynaptic_density_498(2), cat_synaptic_vesicle_release_phenotype_817(1), cat_thiocysteine_simple_molecule_527(1), cat_thiosulfate_simple_molecule_mitochondria_540(1), cat_unknown_unknown_blood_brain_barrier__BBB__613(1), cat_unknown_unknown_endoplasmic_reticulum_ER__569(1), cat_unknown_unknown_neuron_315(1), cat_unknown_unknown_neuron_317(2), cat_unknown_unknown_neuron_321(1), cat_unknown_unknown_neuron_322(2), cat_viral_defence_phenotype_925(1)"


def count_parameter(data):
    # nums = re.findall(r'\(\d+\)', data)
    dic = {}
    for num in nums:
        dic[num] = dic.get(num, 0) + 1

    print("occurrence: ")
    print(dic)


count_parameter(str)
"""
