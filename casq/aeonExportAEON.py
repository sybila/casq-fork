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


class booleanFormulaBuilder():
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

    def addActivator(self, vid):
        """Update transition to add an activator.

        A reaction may only take place if all reactants/activators are present.
        """
        if self.reactant == "_":
            self.reactant = cleanName(vid)
        else:
            self.reactant = "({current} & {vid})".format(
                vid=cleanName(vid), current=self.reactant
            )

    def addInhibitor(self, vid):
        """If any inhibitor is active, the reaction is stopped."""
        if self.reactant == "_":
            self.reactant = "!" + cleanName(vid)
        else:
            self.reactant = "(!{vid} & {current})".format(
                vid=cleanName(vid), current=self.reactant
            )

    def addTransition(self):
        """AddTransition."""
        self.reactant = "_"

    def addCatalysis(self, vidList):
        """All non-reactants, non-inhibitors in casq are treated as catalysts.

        If at least one catalyst is active, the reaction can proceed.
        This is achieved in BMA with a min function
        """
        if len(vidList) == 0:
            raise RuntimeError("Empty list of catalyzers.")

        base = "_"
        for vid in vidList:
            if base == "_":
                base = cleanName(vid)
            else:
                base = "({vid} | {base})".format(vid=cleanName(vid), base=base)
        if self.modifier == "_":
            self.modifier = base
        else:
            self.modifier = "({base} & {current})".format(
                base=base, current=self.modifier
        )

    def addAnd(self, vidList):
        """All listed elements are required for firing."""
        if len(vidList) == 0:
            raise RuntimeError("Empty list of required elements.")

        base = "_"
        for vid in vidList:
            if base == "_":
                base = cleanName(vid)
            else:
                base = "({vid} & {base})".format(vid=cleanName(vid), base=base)
        if self.modifier == "_":
            self.modifier = base
        else:
            self.modifier = "({base} & {current})".format(
                base=base, current=self.modifier
            )

    def finishTransition(self):
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


class multiStateFormulaBuilder:
    """Builds a multistate formula.

    This is more simple as BMA defaults to avg(pos)-avg(neg).
    """

    def __init__(self):
        """Init."""
        self.value = ""

    def function(self):
        """Return self.value."""
        return self.value

    def addActivator(self, vid):
        """Do nothing."""
        pass

    def addInhibitor(self, vid):
        """Do nothing."""
        pass

    def addAnd(self, vid):
        """Do nothing."""
        pass

    def addCatalysis(self, vidList):
        """Do nothing."""
        pass

    def addTransition(self):
        """Do nothing."""
        pass

    def finishTransition(self):
        """Do nothing."""
        pass


# hardcoded colour codes so elements still follow BMA colourscheme
# Default pink #ff66cc
COLOURMAP = {0: "#ff66cc", 1: "#33cc00", 2: "#ff9900", 3: "#9966ff", 4: "#00cccc"}


def aeon_relationship(source, target, idMap, count, which="Activator"):
    """Return BMA relationship dict."""
    result = {
        "ToVariable": target,
        "Type": which,
        "FromVariable": source,
        "Id": next(count),
    }
    return result


def get_relationships(info, idMap, count, granularity, ignoreSelfLoops):
    """Return all BMA relationships."""
    relationships = []
    allFormulae = {}
    out = {}
    for item in info.keys():
        """logger.debug(
            item + ", varid = " + str(idMap[item]) + ", name = " + info[item]["name"]
        )"""
        # skip if there are no transitions
        if len(info[item]["transitions"]) == 0:
            logger.debug(item + "-No transitions")
            continue
        product = item
        """
        if granularity == 1:
            formula = booleanFormulaBuilder()
        else:
            formula = multiStateFormulaBuilder()
        """
        formula = booleanFormulaBuilder()

        # variables may be missing from the "simplified" model.
        # Test for variable in the ID map before appending
        for transition in info[item]["transitions"]:
            formula.addTransition()
            logger.debug(item + "\tReactants:\t" + str(transition[1]))
            # reactant
            for reactant in transition[1]:
                if ignoreSelfLoops and reactant == product:
                    continue
                if reactant in idMap:
                    if transition.type in (
                        "INHIBITION",
                        "NEGATIVE_INFLUENCE",
                        "UNKNOWN_INHIBITION",
                    ):
                        relationships.append(
                            aeon_relationship(
                                reactant, product, idMap, count, "Inhibitor"
                            )
                        )

                        inhibitor_name = info[reactant]["name"]
                        formula.addInhibitor(inhibitor_name)
                    else:
                        relationships.append(
                            aeon_relationship(reactant, product, idMap, count)
                        )

                        activator_name = info[reactant]["name"]
                        formula.addActivator(activator_name)
                else:
                    pass
            # now modifiers
            if len(transition[2]) == 0:
                formula.finishTransition()
                continue
            modifiers = transition[2]
            # catalysts are a special case
            catalysts = []
            catalysts_names = []
            inhibitors = []
            inhibitors_names = []
            # List of variables that should be omitted from formulae due to other function
            ignoreList = []
            ignoreList_names = []
            # everything else
            logger.debug(str(modifiers))
            for impact, m in modifiers:
                if ignoreSelfLoops and m == product:
                    continue
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

                if m in idMap:
                    if impact == "UNKNOWN_INHIBITION" or impact == "INHIBITION":
                        relationships.append(
                            aeon_relationship(m, product, idMap, count, "Inhibitor")
                        )
                        inhibitor_name = info[m]["name"]
                        formula.addInhibitor(inhibitor_name)
                        inhibitors.append(idMap[m])
                    else:
                        # treat all other modifiers as catalysts (casq approach)
                        logger.debug(item + "\tFound impact:" + impact)
                        catalysts.append(idMap[m])
                        catalysts_names.append(info[m]["name"])
                        relationships.append(aeon_relationship(m, product, idMap, count))
                else:
                    pass
            """
            logger.debug(item + "\tCatalysts\t" + str(catalysts))
            logger.debug(item + "\tInhibitors\t" + str(inhibitors))
            logger.debug(item + "\tIgnoreList\t" + str(ignoreList))
            """
            # filter catalysts for items to be ignored
            finalCat = [item for item in catalysts if item not in ignoreList]

            finalCat_names = [name for name in catalysts_names if name not in ignoreList_names]
            if len(finalCat) > 0:
                formula.addCatalysis(finalCat_names)
            formula.finishTransition()
        formula_prev = formula.function()

        out[item] = {'Formula': formula_prev, 'Relationships': relationships}
        relationships = []

    return out


def translateGreek(name):
    """Translate Greek to Latin alphabet."""
    greek_alphabet = "ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω"
    latin_alphabet = "AaBbGgDdEeZzHhJjIiKkLlMmNnXxOoPpRrSssTtUuFfQqYyWw"
    greek2latin = str.maketrans(greek_alphabet, latin_alphabet)
    return name.translate(greek2latin)


def depunctuate(name):
    """Replace punctuation by underscores."""
    badChars = " ,-()+:/\\'[]><"
    alternatives = "______________"
    cleanup = str.maketrans(badChars, alternatives)
    return name.translate(cleanup)


def cleanName(name):
    """Remove punctuation and replace Greek letters."""
    noPunctuation = depunctuate(name)
    result = translateGreek(noPunctuation)
    # TODO: This can generate the same name for variables that only differ in
    # non-alphanumeric characters. We should probably fix that in the future.
    result = re.sub('[^0-9a-zA-Z_]', '_', result)
    return result


def aeon_model_variable(var, var_d, info):
    """Return BMA model variable as a dict."""

    position = "#position:{name}:{position_x},{position_y}\n".format(name = cleanName(info[var]['name']),
                                                                  position_x = float(info[var]["x"]),
                                                                  position_y = float(info[var]["y"]))
    formula = "${name}:{formula}\n".format(name = cleanName(info[var]['name']), formula = var_d['Formula'])

    #print(cleanName(var_d['Formula']))
    relationships = ""
    for relationship in var_d['Relationships']:
        type = "->" if relationship['Type'] == "Activator" else "-|"
        relationship_str = "{from_v} {type} {to_v}\n".format(
            from_v = cleanName(info[relationship['FromVariable']]['name']),
            type = type,
            to_v = cleanName(info[relationship['ToVariable']]['name']))
        relationships += relationship_str

    return position + formula + relationships


def bma_layout_variable(vid, infoVariable, fill=None, description=""):
    """Return BMA layout variable as a dict."""
    result = {
        "Id": vid,
        "Name": cleanName(infoVariable["name"]),
        "Type": "Constant",
        "ContainerId": 0,
        "PositionX": float(infoVariable["x"]),
        "PositionY": float(infoVariable["y"]),
        "CellY": 0,
        "CellX": 0,
        "Angle": 0,
        "Description": description,
    }
    if fill is not None:
        result["Fill"] = fill
    return result


def write_aeon_2(
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

    idGenerator = itertools.count(1)



    idMap = {k: next(idGenerator) for k in info.keys()}

    relationships_d = get_relationships(
        info, idMap, idGenerator, granularity, ignoreSelfLoops
    )

    """logger.debug(formula)"""

    variables_model_str = [
        aeon_model_variable(variable, relationships_d[variable], info)
        for variable in relationships_d.keys()
    ]
    vl = [
        bma_layout_variable(
            idMap[v],
            info[v],
            #compartmentColour[info[v]["compartment"]],
            info[v]["compartment"],
        )
        for v in info.keys()
    ]

    name = "#name:\n"
    description = "#description:\n"

    with open(filename, "w", encoding='utf-8') as outfile:
        outfile.write(name)
        outfile.write(description)
        for var in variables_model_str:
            outfile.write(var)



    """
   
    with open(filename, "w") as outfile:
        outfile.write("#name:" + name)
        outfile.write("#description:" + description)
        outfile.write("#position:" + position)
        outfile.write(formula)
        outfile.write(relationships)
    """
