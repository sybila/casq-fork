"""Convert CellDesigner models to .aeon format.

Copyright (C) 2024 xfrak@fi.muni.cz

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
import re
from loguru import logger


class BooleanFormulaBuilder:
    """Builds a logic formula for a variable of Boolean network encoded in .aeon format."""

    def __init__(self):
        """Init.

        reactant reflects the species that are required for formation
        modifier reflects the state of the modifiers
        previous is a function for other transitions
        """

        self.modifier = ""
        self.reactant = ""
        self.previous = ""

    def function(self):
        """Return self.previous."""

        return self.previous

    def add_activator(self, variable_id):
        """Update transition to add an activator.

        A reaction may only take place if all reactants/activators are present.
        """

        if self.reactant == "":
            self.reactant = variable_id
        else:
            self.reactant = "({current} & {vid})".format(
                vid=variable_id, current=self.reactant
            )

    def add_inhibitor(self, vid):
        """If any inhibitor is active, the reaction is stopped."""

        if self.reactant == "":
            self.reactant = "!" + vid
        else:
            self.reactant = "(!{vid} & {current})".format(
                vid=vid, current=self.reactant
            )

    def add_transition(self):
        """AddTransition."""
        self.reactant = ""

    def add_catalysis(self, catalyst_list):
        """All non-reactants, non-inhibitors in casq are treated as catalysts.

        not used now (maybe for future use)
        """

        if len(catalyst_list) == 0:
            raise RuntimeError("Empty list of catalyzers.")

        base = ""
        for vid in catalyst_list:
            if base == "":
                base = vid
            else:
                base = "({vid} | {base})".format(vid=vid, base=base)

        if self.modifier == "":
            self.modifier = base
        else:
            self.modifier = "({base} & {current})".format(
                base=base, current=self.modifier)

    def add_unknown_function(self, catalyst_list, target, transition_id):
        """All non-reactants, non-inhibitors in casq are treated as catalysts.

        create unknown function of catalysts and add it to logic formula
        """

        if len(catalyst_list) == 0:
            raise RuntimeError("Empty list of catalyzers.")

        cat_list_str = ""
        for cat in catalyst_list:
            if cat_list_str == "":
                cat_list_str = cat
            else:
                cat_list_str = "{cat_list_str}, {cat}".format(cat=cat, cat_list_str=cat_list_str)

        function_name = "cat_{target}_{tran_id}".format(target=target, tran_id=transition_id)
        unknown_fun_str = "{fun_name}({cat_list_str})".format(fun_name=function_name, cat_list_str=cat_list_str)

        if self.modifier == "":
            self.modifier = unknown_fun_str
        else:
            self.modifier = "({current} & {unknown_fun_str})".format(
                current=self.modifier, unknown_fun_str=unknown_fun_str
            )

    def add_and(self, catalyst_list):
        """All listed elements are required for firing.

        (maybe for future for AND_GATE)
        """

        if len(catalyst_list) == 0:
            raise RuntimeError("Empty list of required elements.")

        base = ""
        for vid in catalyst_list:
            if base == "":
                base = vid
            else:
                base = "({vid} & {base})".format(vid=vid, base=base)
        if self.modifier == "":
            self.modifier = base
        else:
            self.modifier = "({base} & {current})".format(
                base=base, current=self.modifier
            )

    def finish_transition(self):
        """Add a single transition formula to the current state.

        The final formula is logic alternative for all reactions for variable.
        """

        if self.modifier == "":
            function = self.reactant
        elif self.reactant == "":
            function = self.modifier
        else:
            function = "({transition} & {current})".format(
                transition=self.reactant, current=self.modifier
        )

        if self.previous == "":
            self.previous = function
        else:
            self.previous = "({f} | {old})".format(f=function, old=self.previous)
        self.reactant = ""
        self.modifier = ""


def aeon_relationship(source, target, relationship_type_str):
    """Return new AEON relationship."""

    #  default parameters are activation, known=False
    relationship = {
        "from_variable": source,
        "to_variable": target,
        "type": "activation",
        "unknown": False,
        "type_str": relationship_type_str,
    }

    if relationship_type_str.find('UNKNOWN_', 0) != -1:
        relationship['unknown'] = True

        if relationship_type_str in ["UNKNOWN_INHIBITION", "UNKNOWN_NEGATIVE_INFLUENCE"]:
            relationship['type'] = "inhibition"

    if relationship_type_str in ["INHIBITION", "NEGATIVE_INFLUENCE"]:
        relationship['type'] = "inhibition"

    return relationship


def add_relationship(relationships, relationship):
    """Add unique relationship, fuse relationships with identity in pairs "from" and "to" variables.

    returns updated dictionary with relationships
    solve non-essential reactions and monotonicity"""

    rel_dic = relationships

    for item in rel_dic:
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

            return rel_dic

    rel_dic.append(relationship)
    return rel_dic


def get_relationships(info, id_map, count, ignore_self_loops):
    """Return all AEON relationships.

    for every variable in model gives formula and relationships"""

    transition_id = itertools.count()
    variables = {}

    for item_vid in info.keys():
        # skip if there are no transitions
        if len(info[item_vid]["transitions"]) == 0:
            logger.debug(item_vid + "-No transitions")
            continue

        product_name = info[item_vid]['clean_name']
        relationships = []
        formula = BooleanFormulaBuilder()

        # variables may be missing from the "simplified" model.
        # Test for variable in the ID map before appending
        for transition in info[item_vid]["transitions"]:
            tran_id = next(transition_id)

            formula.add_transition()
            logger.debug(item_vid + "\tReactants:\t" + str(transition[1]))

            # reactants
            for reactant_vid in transition[1]:
                if ignore_self_loops and reactant_vid == item_vid:
                    continue
                if reactant_vid in id_map:
                    reactant_name = info[reactant_vid]["clean_name"]

                    if transition.type in (
                        "INHIBITION",
                        "NEGATIVE_INFLUENCE",
                        "UNKNOWN_INHIBITION",
                    ):
                        formula.add_inhibitor(reactant_name)
                    else:
                        formula.add_activator(reactant_name)

                    relationship = aeon_relationship(reactant_name, product_name, transition.type)
                    relationships = add_relationship(relationships, relationship)

            # modifiers
            if len(transition[2]) == 0:
                formula.finish_transition()
                continue
            modifiers = transition[2]

            catalysts = []
            catalysts_names = []

            for impact, modifier_vid in modifiers:
                if ignore_self_loops and modifier_vid == item_vid:
                    continue

                if modifier_vid in id_map:
                    modifier_name = info[modifier_vid]["clean_name"]

                    if impact == "UNKNOWN_INHIBITION" or impact == "INHIBITION":
                        formula.add_inhibitor(modifier_name)

                    else:
                        # treat all other modifiers as catalysts (casq approach)
                        logger.debug(item_vid + "\tFound impact:" + impact)
                        catalysts.append(id_map[modifier_vid])
                        catalysts_names.append(modifier_name)

                    relationship = aeon_relationship(modifier_name, product_name, impact)
                    relationships = add_relationship(relationships, relationship)

            logger.debug(item_vid + "\tCatalysts\t" + str(catalysts))

            if len(catalysts) > 0:
                formula.add_unknown_function(catalysts_names, product_name, tran_id)

            formula.finish_transition()

        formula_prev = formula.function()

        variables[item_vid] = {'Formula': formula_prev, 'Relationships': relationships}

    return variables


def translate_greek(name):
    """Translate Greek to Latin alphabet."""

    greek_alphabet = "ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω"
    latin_alphabet = "AaBbGgDdEeZzHhJjIiKkLlMmNnXxOoPpRrSssTtUuFfQqYyWw"
    greek2latin = str.maketrans(greek_alphabet, latin_alphabet)
    return name.translate(greek2latin)


def clean_name(name):
    """Remove unsupported aeon symbols from variables names."""

    result = translate_greek(name)
    # non-alphanumeric characters (and "\_")
    result = re.sub('[^0-9a-zA-Z_]', '_', result)
    return result


def aeon_model_variable(var, var_dic, info):
    """Return AEON model variable as a string position, logic formula and relationships to variable."""

    position_line = "#position:{name}:{position_x},{position_y}\n".format(name=(info[var]['clean_name']),
                                                                          position_x=float(info[var]["x"]),
                                                                          position_y=float(info[var]["y"]))
    
    # If there are no transitions or the function is empty, this variable is an "input"
    # and has an empty update function.
    formula = var_dic['Formula']
    if formula != "":
        formula_line = "${name}:{formula}\n".format(name=info[var]['clean_name'], formula=formula)
    else:
        formula_line = ""

    relationships_lines = ""

    for relationship in var_dic['Relationships']:
        reaction_type = "-"
        if relationship['type'] == "activation":
            reaction_type += ">"
        elif relationship['type'] == "inhibition":
            reaction_type += "|"
        else:  # "non-monotonic"
            reaction_type += "?"

        if relationship['unknown']:
            reaction_type += "?"

        relationship_str = "{from_v} {type} {to_v}\n".format(
            type_str=relationship['type_str'],
            from_v=relationship['from_variable'],
            type=reaction_type,
            to_v=relationship['to_variable'])

        relationships_lines += relationship_str

    return position_line + formula_line + relationships_lines


def clean_names(info):
    """Clean all names of variables in info.

    all aeon unsupported symbols are replaced by \"_\""""

    clean_names_dic = {}

    for vid in info.keys():
        name = info[vid]['name']
        c_name = clean_name(name)

        if c_name not in clean_names_dic.keys():
            clean_names_dic[c_name] = {name: c_name}
            info[vid]['clean_name'] = c_name

        else:  # c_name in
            if name in clean_names_dic[c_name]:
                info[vid]['clean_name'] = clean_names_dic[c_name][name]
            else:
                clean_names_dic[c_name][name] = c_name + "_v" + str(len(clean_names_dic[c_name]) + 1)
                info[vid]['clean_name'] = clean_names_dic[c_name][name]


def write_aeon(
    file_name: str,
    info,
    ignore_self_loops=False,
):
    """Write the .aeon file for our model."""

    id_generator = itertools.count(1)
    id_map = {k: next(id_generator) for k in info.keys()}

    # add clean names of variables into info
    clean_names(info)

    relationships_dic = get_relationships(
        info, id_map, id_generator, ignore_self_loops
    )

    model_variables_str = [
        aeon_model_variable(variable, relationships_dic[variable], info)
        for variable in relationships_dic.keys()
    ]

    name = "#name:\n"
    description = "#description:\n"

    with open(file_name, "w", encoding='utf-8') as outfile:
        # outfile.write(name)
        # outfile.write(description)
        for var in model_variables_str:
            outfile.write(var)
