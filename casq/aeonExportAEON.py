"""Convert CellDesigner models to .aeon format. (now only changes formula format)

Copyright (C) 2021 b.hall@ucl.ac.uk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import itertools
import json
import re

from loguru import logger


class BooleanFormulaBuilder:
    """Builds a formula for a boolean network encoded in .aeon format.

    The formula is a max applied to a series of reactions (transitions),
    so that if at least one reaction is active the variable becomes active
    """

    def __init__(self):
        """Init.

        reactant reflects the species that are required for formation
        modifier reflects the state of the modifiers
        previous is a function for other transitions
        """
        self.modifier = "_"
        self.reactant = "_"
        self.previous = "_"

    def function(self):
        """Return self.previous."""
        return self.previous

    def add_activator(self, vid):
        """Update transition to add an activator.

        A reaction may only take place if all reactants/activators are present.
        """
        if self.reactant == "_":
            self.reactant = clean_name(vid)
        else:
            self.reactant = "({current} & {vid})".format(
                vid=clean_name(vid), current=self.reactant
            )

    def add_inhibitor(self, vid):
        """If any inhibitor is active, the reaction is stopped."""
        if self.reactant == "_":
            self.reactant = "!" + clean_name(vid)
        else:
            self.reactant = "(!{vid} & {current})".format(
                vid=clean_name(vid), current=self.reactant
            )

    def add_transition(self):
        """AddTransition."""
        self.reactant = "_"

    def add_catalysis(self, cat_list):
        """All non-reactants, non-inhibitors in casq are treated as catalysts.

        If at least one catalyst is active, the reaction can proceed.
        This is achieved in BMA with a min function
        """
        if len(cat_list) == 0:
            raise RuntimeError("Empty list of catalyzers.")

        base = "_"
        for vid in cat_list:
            if base == "_":
                base = clean_name(vid)
            else:
                base = "({vid} | {base})".format(vid=clean_name(vid), base=base)
        if self.modifier == "_":
            self.modifier = base
        else:
            self.modifier = "({base} & {current})".format(
                base=base, current=self.modifier
        )

    def add_unknown_function(self, cat_list, target, tran_id):
        """..."""
        if len(cat_list) == 0:
            raise RuntimeError("Empty list of catalyzers.")

        clean_cat_list = [clean_name(cat) for cat in cat_list]

        cat_list_str = "_"
        for cat in clean_cat_list:
            if cat_list_str == "_":
                cat_list_str = cat
            else:
                cat_list_str = "{cat_list_str}, {cat}".format(cat=cat, cat_list_str=cat_list_str)

        fun_name = "cat_{target}_{tran_id}".format(target=clean_name(target), tran_id=tran_id)
        unknown_fun_str = "{fun_name}({cat_list_str})".format(fun_name=fun_name, cat_list_str=cat_list_str)

        if self.modifier == "_":
            self.modifier = unknown_fun_str
        else:
            self.modifier = "({current} & {unknown_fun_str})".format(
                current=self.modifier, unknown_fun_str=unknown_fun_str
            )

    def add_and(self, cat_list):
        """All listed elements are required for firing."""
        if len(cat_list) == 0:
            raise RuntimeError("Empty list of required elements.")

        base = "_"
        for vid in cat_list:
            if base == "_":
                base = clean_name(vid)
            else:
                base = "({vid} & {base})".format(vid=clean_name(vid), base=base)
        if self.modifier == "_":
            self.modifier = base
        else:
            self.modifier = "({base} & {current})".format(
                base=base, current=self.modifier
            )

    def finish_transition(self):
        """Add a single transition formula to the current state.

        The final formula is the min of the transition and the catalyst-modifiers
        The catalyst-modifiers default to 1, the transition defaults to 1
        Resets the transition formula to 1.
        """
        if self.modifier == "_" and self.reactant == "_":
            # TODO: This should probably be a warning/error?
            function = "true"
        if self.modifier == "_":
            function = self.reactant
        elif self.reactant == "_":
            function = self.modifier
        else:
            function = "({transition} & {current})".format(
                transition=self.reactant, current=self.modifier
        )

        if self.previous == "_":
            self.previous = function
        else:
            self.previous = "({f} | {old})".format(f=function, old=self.previous)
        self.reactant = "_"
        self.modifier = "_"


class MultiStateFormulaBuilder:
    """Builds a multistate formula.

    This is more simple as BMA defaults to avg(pos)-avg(neg).
    """

    def __init__(self):
        """Init."""
        self.value = ""

    def function(self):
        """Return self.value."""
        return self.value

    def add_activator(self, vid):
        """Do nothing."""
        pass

    def add_inhibitor(self, vid):
        """Do nothing."""
        pass

    def add_and(self, vid):
        """Do nothing."""
        pass

    def add_catalysis(self, vid_list):
        """Do nothing."""
        pass

    def add_transition(self):
        """Do nothing."""
        pass

    def finish_transition(self):
        """Do nothing."""
        pass


# hardcoded colour codes so elements still follow BMA colourscheme
# Default pink #ff66cc
COLOURMAP = {0: "#ff66cc", 1: "#33cc00", 2: "#ff9900", 3: "#9966ff", 4: "#00cccc"}


def aeon_relationship(source, target, idMap, count, relationship_type):
    """Return AEON relationship dict."""

    #  default is activation, known
    relationship = {
        "from_variable": source,
        "to_variable": target,
        "type": "activation",
        "unknown": False,
        "type_str": relationship_type,
        # "Id": next(count),
    }

    if relationship_type.find('UNKNOWN_', 0) != -1:
        relationship['unknown'] = True

        if relationship_type in ["UNKNOWN_INHIBITION", "UNKNOWN_NEGATIVE_INFLUENCE"]:
            relationship['type'] = "inhibition"

    if relationship_type in ["INHIBITION", "NEGATIVE_INFLUENCE"]:
        relationship['type'] = "inhibition"

    print(relationship)
    return relationship


def add_relationship(relationships, relationship):
    """Add unique relationship, fuse relationships with identity in "from" and "to" variables."""

    new_dic = relationships

    for item in new_dic:
        if (item["from_variable"] == relationship["from_variable"] and
                item["to_variable"] == relationship["to_variable"]):

            if (item["type"] != relationship["type"] or
                    item["unknown"] != relationship["unknown"]):

                if item["unknown"] and relationship["unknown"]:
                    item["unknown"] = True
                else:
                    item["unknown"] = False

                #  monotonicity
                if (item["type"] != relationship["type"] or
                        relationship["type"] == "non_monotonic"):
                    item["type"] = "non_monotonic"

            return new_dic

    new_dic.append(relationship)
    return new_dic


def get_relationships(info, idMap, count, granularity, ignoreSelfLoops):
    """Return all AEON relationships."""

    transition_id = itertools.count()
    relationships = []
    allFormulae = {}
    variables = {}
    for item_vid in info.keys():

        """logger.debug(
            item + ", varid = " + str(idMap[item]) + ", name = " + info[item]["name"]
        )"""
        # skip if there are no transitions
        if len(info[item_vid]["transitions"]) == 0:
            logger.debug(item_vid + "-No transitions")
            continue
        product_name = info[item_vid]['clean_name']
        """
        if granularity == 1:
            formula = booleanFormulaBuilder()
        else:
            formula = multiStateFormulaBuilder()
        """
        formula = BooleanFormulaBuilder()

        # variables may be missing from the "simplified" model.
        # Test for variable in the ID map before appending
        for transition in info[item_vid]["transitions"]:
            tran_id = next(transition_id)

            formula.add_transition()
            logger.debug(item_vid + "\tReactants:\t" + str(transition[1]))
            # reactant
            for reactant_vid in transition[1]:
                if ignoreSelfLoops and reactant_vid == item_vid:
                    continue
                if reactant_vid in idMap:
                    reactant_name = info[reactant_vid]["clean_name"]

                    if transition.type in (
                        "INHIBITION",
                        "NEGATIVE_INFLUENCE",
                        "UNKNOWN_INHIBITION",
                    ):
                        formula.add_inhibitor(reactant_name)
                    else:
                        formula.add_activator(reactant_name)

                    relationship = aeon_relationship(reactant_name, product_name, idMap, count, transition.type)
                    relationships = add_relationship(relationships, relationship)
                else:
                    pass

            # now modifiers
            if len(transition[2]) == 0:
                formula.finish_transition()
                continue
            modifiers = transition[2]
            # catalysts are a special case
            catalysts = []
            catalysts_names = []
            inhibitors = []
            inhibitors_names = []
            # List of variables that should be omitted from formulae due to other function
            ignore_list = []
            ignore_list_names = []
            # everything else
            logger.debug(str(modifiers))

            for impact, modifier_vid in modifiers:
                if ignoreSelfLoops and modifier_vid == item_vid:
                    continue
                """
                if impact == "BOOLEAN_LOGIC_GATE_AND":
                    logger.debug("Found an AND gate")
                    # indicates that the listed vars will be anded
                    # BAH: should I remove them from the cat code? In this instance its harmless...
                    vidList = [idMap[jtem] for jtem in m.split(",") if jtem in idMap]
                    and_list_names = [info[jtem]["name"] for jtem in m.split(",") if jtem in idMap]
                    formula.addAnd(and_list_names)
                    for jtem in vidList:
                        ignoreList.append(jtem)
                        print(type(info))
                        if jtem in info:
                            ignoreList_names.append(info[jtem]["name"])
                """
                if modifier_vid in idMap:
                    modifier_name = info[modifier_vid]["clean_name"]

                    if impact == "UNKNOWN_INHIBITION" or impact == "INHIBITION":
                        formula.add_inhibitor(modifier_name)
                        inhibitors.append(idMap[modifier_vid])

                    else:
                        # treat all other modifiers as catalysts (casq approach)
                        logger.debug(item_vid + "\tFound impact:" + impact)
                        catalysts.append(idMap[modifier_vid])
                        catalysts_names.append(modifier_name)

                    relationship = aeon_relationship(modifier_name, product_name, idMap, count, impact)
                    relationships = add_relationship(relationships, relationship)
                else:
                    pass
            """
            logger.debug(item + "\tCatalysts\t" + str(catalysts))
            logger.debug(item + "\tInhibitors\t" + str(inhibitors))
            logger.debug(item + "\tIgnoreList\t" + str(ignoreList))
            """
            # filter catalysts for items to be ignored
            final_cat = [item for item in catalysts if item not in ignore_list]

            final_cat_names = [name for name in catalysts_names if name not in ignore_list_names]

            if len(final_cat) > 0:
                formula.add_unknown_function(final_cat_names, product_name, tran_id)

            formula.finish_transition()

        formula_prev = formula.function()

        variables[item_vid] = {'Formula': formula_prev, 'Relationships': relationships}
        relationships = []

    return variables


def translate_greek(name):
    """Translate Greek to Latin alphabet."""
    greek_alphabet = "ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω"
    latin_alphabet = "AaBbGgDdEeZzHhJjIiKkLlMmNnXxOoPpRrSssTtUuFfQqYyWw"
    greek2latin = str.maketrans(greek_alphabet, latin_alphabet)
    return name.translate(greek2latin)


def depunctuate(name):
    """Replace punctuation by underscores."""
    bad_chars = " ,-()+:/\\'[]><"
    alternatives = "______________"
    cleanup = str.maketrans(bad_chars, alternatives)
    return name.translate(cleanup)


def clean_name(name):
    """Remove punctuation and replace Greek letters."""
    no_punctuation = depunctuate(name)
    result = translate_greek(no_punctuation)
    # TODO: This can generate the same name for variables that only differ in
    # non-alphanumeric characters. We should probably fix that in the future.
    result = re.sub('[^0-9a-zA-Z_]', '_', result)
    return result


def aeon_model_variable(var, var_d, info):
    """Return AEON model variable as a string."""

    position = "#position:{name}:{position_x},{position_y}\n".format(name=(info[var]['clean_name']),
                                                                     position_x=float(info[var]["x"]),
                                                                     position_y=float(info[var]["y"]))
    
    # If there are no transitions or the function is empty, this variable is an "input"
    # and has an empty update function.
    formula = var_d['Formula']
    if formula != "_" and formula != "":
        formula = "${name}:{formula}\n".format(name=info[var]['clean_name'], formula=formula)
    else:
        formula = ""

    relationships = ""

    for relationship in var_d['Relationships']:
        rec_type = "-"
        if relationship['type'] == "activation":
            rec_type += ">"
        elif relationship['type'] == "inhibition":
            rec_type += "|"
        else:  # "non-monotonic"
            rec_type += "?"

        if relationship['unknown']:
            rec_type += "?"
        # relationship_str = "# Type: {type_str}\n{from_v} {type} {to_v}\n".format
        relationship_str = "{from_v} {type} {to_v}\n".format(
            type_str=relationship['type_str'],
            from_v=clean_name(relationship['from_variable']),
            type=rec_type,
            to_v=clean_name(relationship['to_variable']))

        relationships += relationship_str

    return position + formula + relationships


def bma_layout_variable(vid, info_variable, fill=None, description=""):
    """Return BMA layout variable as a dict."""
    result = {
        "Id": vid,
        "Name": clean_name(info_variable["name"]),
        "Type": "Constant",
        "ContainerId": 0,
        "PositionX": float(info_variable["x"]),
        "PositionY": float(info_variable["y"]),
        "CellY": 0,
        "CellX": 0,
        "Angle": 0,
        "Description": description,
    }
    if fill is not None:
        result["Fill"] = fill
    return result


def clean_names(info):
    clean_names_dic = {}

    for vid in info.keys():
        name = info[vid]['name']
        c_name = clean_name(name)

        if c_name not in clean_names_dic:
            clean_names_dic[c_name] = {name: c_name}
            info[vid]['clean_name'] = c_name

        else: # c_name in
            if name in clean_names_dic[c_name]:
                info[vid]['clean_name'] = clean_names_dic[c_name][name]
            else:
                clean_names_dic[c_name][name] = c_name + "_v" + str(len(clean_names_dic[c_name]) + 1)
                info[vid]['clean_name'] = clean_names_dic[c_name][name]


def write_aeon(
    filename: str,
    info,
    granularity=1,
    inputLevel=None,
    ignoreSelfLoops=False,
    colourByCompartment=True,
):
    """
    # pylint: disable=too-many-arguments, too-many-locals
    """"""Write the BMA json with layout file for our model.""""""
    # granularity must be a non-zero natural
    assert granularity > 0
    # calculate the compartments for colours;
    # four largest compartments are coloured BMA colours, all else default
    compartments = {}
    for k in info.keys():
        location = info[k]["compartment"]
        if location in compartments:
            compartments[location] += 1
        else:
            compartments[location] = 1
    compList = list(compartments.items())
    compList.sort(key=lambda i: -i[1])
    compartmentColour = {}
    for i in range(len(compartments)):
        if colourByCompartment:
            compartmentColour[compList[i][0]] = COLOURMAP.get(i)
        else:
            compartmentColour[compList[i][0]] = COLOURMAP.get(0)
    """

    id_generator = itertools.count(1)

    id_map = {k: next(id_generator) for k in info.keys()}

    # add clean variables' names into info object
    clean_names(info)

    relationships_dic = get_relationships(
        info, id_map, id_generator, granularity, ignoreSelfLoops
    )

    """logger.debug(formula)"""

    variables_model_str = [
        aeon_model_variable(variable, relationships_dic[variable], info)
        for variable in relationships_dic.keys()
    ]
    vl = [
        bma_layout_variable(
            id_map[v],
            info[v],
            #compartmentColour[info[v]["compartment"]],
            info[v]["compartment"],
        )
        for v in info.keys()
    ]

    name = "#name:\n"
    description = "#description:\n"

    with open(filename, "w", encoding='utf-8') as outfile:
        # outfile.write(name)
        # outfile.write(description)
        for var in variables_model_str:
            outfile.write(var)

    print(info)


    """
   
    with open(filename, "w") as outfile:
        outfile.write("#name:" + name)
        outfile.write("#description:" + description)
        outfile.write("#position:" + position)
        outfile.write(formula)
        outfile.write(relationships)
    """
