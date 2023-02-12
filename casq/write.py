"""Write SBML-Qual models.

Copyright (C) 2019, Sylvain.Soliman@inria.fr

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

import csv
import xml.etree.ElementTree as etree
from itertools import chain, repeat
from typing import IO, List, Optional, Tuple  # noqa: F401

from loguru import logger  # type: ignore

import networkx as nx  # type: ignore

from . import version
from .readCD import NS, Transition, add_rdf


INHIBITION = ("INHIBITION", "UNKNOWN_INHIBITION")
NEGATIVE = ("INHIBITION", "NEGATIVE_INFLUENCE", "UNKNOWN_INHIBITION")


def write_qual(
    filename: str,
    info,
    width: str,
    height: str,
    remove: int = 0,
    sif: bool = False,
    fixed: IO = None,
):
    # pylint: disable=too-many-arguments, too-many-locals
    """Write the SBML qual with layout file for our model."""
    for name, space in NS.items():
        etree.register_namespace(name, space)
    root = etree.Element(
        "sbml",
        {
            "level": "3",
            "version": "1",
            "layout:required": "false",
            "xmlns": NS["sbml3"],
            "qual:required": "true",
            "xmlns:layout": NS["layout"],
            "xmlns:qual": NS["qual"],
        },
    )
    model = etree.SubElement(root, "model", id="model_id")
    notes = etree.SubElement(model, "notes")
    html = etree.SubElement(notes, "html", xmlns=NS["xhtml"])
    body = etree.SubElement(html, "body")
    p = etree.SubElement(body, "p")
    p.text = "Created by CaSQ " + version
    clist = etree.SubElement(model, "listOfCompartments")
    etree.SubElement(clist, "compartment", constant="true", id="comp1")
    llist = etree.SubElement(model, "layout:listOfLayouts")
    layout = etree.SubElement(llist, "layout:layout", id="layout1")
    etree.SubElement(layout, "layout:dimensions", width=width, height=height)
    qlist = etree.SubElement(model, "qual:listOfQualitativeSpecies")
    tlist = etree.SubElement(model, "qual:listOfTransitions")
    graph = nx.DiGraph()
    initial = {}
    if fixed:
        # dialect = csv.Sniffer().sniff(fixed.read(1024))
        # fixed.seek(0)
        for row in csv.reader(fixed):
            if row[0] in info:
                info[row[0]]["transitions"] = []
                initial[row[0]] = row[1]

    add_transitions(tlist, info, graph)
    remove_connected_components(tlist, info, graph, remove)
    if sif:
        write_sif(filename, info, graph)
    add_qual_species(layout, qlist, info, initial)
    etree.ElementTree(root).write(filename, encoding="utf-8", xml_declaration=True)


def remove_connected_components(
    tlist: etree.Element, info, graph: nx.DiGraph, remove: int
):
    """Remove connected components of size smaller than remove."""
    # because we did not properly NameSpace all transitions, we cannot use
    # find('./qual:transition[@qual:id=]')
    logger.debug("remove value {S}", S=remove)
    transitions = list(tlist)
    ccs = list(nx.connected_components(graph.to_undirected()))
    # add completely isolated nodes
    nodes = graph.nodes()
    ccs.extend({species} for (species, data) in info.items() if species not in nodes)
    logger.debug("CCs: {ccs}", ccs=ccs)
    if remove < 0:
        remove = len(max(ccs, key=len)) - 1
    logger.debug("remove value {S}", S=remove)
    for component in filter(lambda x: len(x) <= remove, ccs):
        logger.debug(
            "removing connected component {component}", component=list(component)
        )
        for species in component:
            logger.debug("removing species {sp}", sp=species)
            del info[species]
            trans_id = "tr_" + species
            trans = next((t for t in transitions if t.get("qual:id") == trans_id), None)
            if trans:
                logger.debug("removing transition {tr}", tr=trans)
                tlist.remove(trans)


def write_sif(sbml_filename: str, info, graph: nx.DiGraph):
    """Write a SIF file with influences.

    http://www.cbmc.it/fastcent/doc/SifFormat.htm
    """
    with open(sbml_filename[:-4] + "sif", "w", encoding="utf-8", newline="") as f:
        print(f"# Generated by CaSQ v{version}", file=f)
        with open(
            sbml_filename[:-5] + "_raw.sif", "w", encoding="utf-8", newline=""
        ) as fraw:
            print(f"# Generated by CaSQ v{version}", file=fraw)
            for source, target, sign in graph.edges.data("sign"):
                print(
                    source.replace(" ", "_"),
                    sign.upper(),
                    target.replace(" ", "_"),
                    file=fraw,
                )
                print(
                    info[source]["name"].replace(" ", "_"),
                    sign.upper(),
                    info[target]["name"].replace(" ", "_"),
                    file=f,
                )


def add_qual_species(layout: etree.Element, qlist: etree.Element, info, initial):
    """Create layout sub-elements and species."""
    llist = etree.SubElement(layout, "layout:listOfAdditionalGraphicalObjects")
    for species, data in info.items():
        glyph = etree.SubElement(
            llist,
            "layout:generalGlyph",
            {"layout:reference": species, "layout:id": species + "_glyph"},
        )
        box = etree.SubElement(glyph, "layout:boundingBox")
        etree.SubElement(
            box, "layout:position", {"layout:x": data["x"], "layout:y": data["y"]}
        )
        etree.SubElement(
            box,
            "layout:dimensions",
            {"layout:height": data["h"], "layout:width": data["w"]},
        )
        if data["transitions"]:
            constant = "false"
        else:
            constant = "true"
        attribs = {
            "qual:maxLevel": "1",
            "qual:compartment": "comp1",
            "qual:name": data["name"],
            "qual:constant": constant,
            "qual:id": species,
        }
        if species in initial:
            attribs["qual:initialLevel"] = initial[species]
        qspecies = etree.SubElement(
            qlist,
            "qual:qualitativeSpecies",
            attribs,
        )
        add_annotation(qspecies, data["annotations"])


def add_annotation(node: etree.Element, rdf: Optional[etree.Element]):
    """Add a single RDF element as an annotation node."""
    if rdf is not None:
        etree.SubElement(node, "annotation").append(rdf)


def add_transitions(tlist: etree.Element, info, graph: nx.DiGraph):
    """Create transition elements."""
    known = list(info.keys())
    for species, data in info.items():
        if data["transitions"]:
            trans = etree.SubElement(
                tlist, "qual:transition", {"qual:id": "tr_" + species}
            )
            ilist = etree.SubElement(trans, "qual:listOfInputs")
            add_inputs(ilist, data["transitions"], species, known, graph)
            # there might not be any input left after filtering known species
            if len(ilist) == 0:
                tlist.remove(trans)
                logger.debug(
                    "transition for {species} exists {trans} but has no inputs",
                    trans=data["transitions"],
                    species=species,
                )
                info[species]["transitions"] = []
                add_function_as_rdf(info, species, info[species]["function"])
            else:
                olist = etree.SubElement(trans, "qual:listOfOutputs")
                etree.SubElement(
                    olist,
                    "qual:output",
                    {
                        "qual:qualitativeSpecies": species,
                        "qual:transitionEffect": "assignmentLevel",
                        "qual:id": f"tr_{species}_out",
                    },
                )
                flist = etree.SubElement(trans, "qual:listOfFunctionTerms")
                etree.SubElement(flist, "qual:defaultTerm", {"qual:resultLevel": "0"})
                func = etree.SubElement(
                    flist, "qual:functionTerm", {"qual:resultLevel": "1"}
                )
                add_function(func, data["transitions"], known)
                sfunc = mathml_to_ginsim(func.find("./math/*", NS), info)
                info[species]["function"] = sfunc
                add_function_as_rdf(info, species, sfunc)
                add_notes(trans, data["transitions"])
                add_annotations(trans, data["transitions"])
        else:
            add_function_as_rdf(info, species, info[species]["function"])


def add_notes(trans: etree.Element, transitions: List[Transition]):
    """Add all the found notes."""
    notes = etree.SubElement(trans, "notes")
    html = etree.SubElement(notes, "html", xmlns=NS["xhtml"])
    head = etree.SubElement(html, "head")
    etree.SubElement(head, "title")
    body = etree.SubElement(html, "body")
    some_notes = False
    for reaction in transitions:
        if reaction.notes is not None:
            some_notes = True
            reaction.notes.tag = "p"
            for element in reaction.notes.iter():
                for prefix in ("xhtml", "sbml"):
                    prefix_len = len(NS[prefix]) + 2
                    if element.tag.startswith("{" + NS[prefix] + "}"):
                        element.tag = element.tag[prefix_len:]
            body.append(reaction.notes)
    if not some_notes:
        trans.remove(notes)


def add_annotations(trans: etree.Element, transitions: List[Transition]):
    """Add all the found annotations."""
    annotation = etree.SubElement(trans, "annotation")
    rdf = etree.SubElement(annotation, "rdf:RDF")
    for reaction in transitions:
        if reaction.annotations is not None:
            rdf.append(reaction.annotations[0])
    if len(rdf) == 0:
        trans.remove(annotation)


def add_function(func: etree.Element, transitions: List[Transition], known: List[str]):
    """Add the complete boolean activation function.

    this is an or over all reactions having the target as product.
    For each reaction it can activate if all reactants are present,
    no inhibitor is present, and one of the activators is present.
    """
    math = etree.SubElement(func, "math", xmlns=NS["mathml"])
    # create or node if necessary
    if len(transitions) > 1:
        apply = etree.SubElement(math, "apply")
        etree.SubElement(apply, "or")
    else:
        apply = math
    for reaction in transitions:
        # we assume that only "BOOLEAN_LOGIC_GATE_AND" has multiple modifiers
        # it is also the only modification that has an AND and therefore ends
        # with reactants
        reactants = [reac for reac in reaction.reactants if reac in known]
        reactants.extend(
            [
                mod
                for (modtype, modifier) in reaction.modifiers
                for mod in modifier.split(",")
                if modtype == "BOOLEAN_LOGIC_GATE_AND" and mod in known
            ]
        )
        activators = [
            modifier
            for (modtype, modifier) in reaction.modifiers
            if modtype
            not in ("INHIBITION", "UNKNOWN_INHIBITION", "BOOLEAN_LOGIC_GATE_AND")
            and modifier in known
            and modifier not in reactants
        ]
        inhibitors = [
            modifier
            for (modtype, modifier) in reaction.modifiers
            if modtype in INHIBITION and modifier in known
        ]
        # this should only appear when species is of type PHENOTYPE otherwise
        # non-SBGN compliant, and there should be a single reactant and no inhibitors
        # just swap reactants and inhibitors, there should not be any activator
        if reaction.type in NEGATIVE:
            reactants, inhibitors = inhibitors, reactants
            if activators or reactants:
                logger.error("non-SBGN direct inhibition encountered")
        # create and node if necessary
        if len(reactants) + len(inhibitors) > 1 or (
            activators and (reactants or inhibitors)
        ):
            lapply = etree.SubElement(apply, "apply")
            etree.SubElement(lapply, "and")
        else:
            lapply = apply
        if len(activators) < 2:
            reactants.extend(activators)
        else:
            # create or node if necessary
            inner_apply = etree.SubElement(lapply, "apply")
            etree.SubElement(inner_apply, "or")
            for modifier in activators:
                set_level(inner_apply, modifier, "1")
        for level, modifier in chain(
            zip(repeat("1"), reactants), zip(repeat("0"), inhibitors)
        ):
            set_level(lapply, modifier, level)


def set_level(elt: etree.Element, modifier: str, level: str):
    """Add mathml to element elt such that modifier is equal to level."""
    trigger = etree.SubElement(elt, "apply")
    etree.SubElement(trigger, "eq")
    math_ci = etree.SubElement(trigger, "ci")
    math_ci.text = modifier
    math_cn = etree.SubElement(trigger, "cn", type="integer")
    math_cn.text = level


def negate(sign: str):
    """Change a sign represented as a string."""
    if sign == "negative":
        return "positive"
    return "negative"


def add_inputs(
    ilist: etree.Element,
    transitions: List[Transition],
    species: str,
    known: List[str],
    graph: nx.DiGraph,
):
    """Add all known inputs."""
    index = 0
    modifiers = []  # type: List[Tuple[str, str]]
    graph.add_node(species)
    for reaction in transitions:
        # we use enumerate to get a dummy modtype for reactants
        for modtype, modifier in chain(
            enumerate(reaction.reactants), reaction.modifiers
        ):
            if modtype in INHIBITION:
                sign = "negative"
            else:
                sign = "positive"
            # this should only appear when species is of type PHENOTYPE
            # otherwise non-SBGN compliant
            if reaction.type in NEGATIVE:
                sign = negate(sign)
                logger.warning("non-SBGN direct negative reaction found")
            if (modifier, sign) not in modifiers and modifier in known:
                modifiers.append((modifier, sign))
                graph.add_edge(modifier, species, sign=sign)
                etree.SubElement(
                    ilist,
                    "qual:input",
                    {
                        "qual:qualitativeSpecies": modifier,
                        "qual:transitionEffect": "none",
                        "qual:sign": sign,
                        "qual:id": f"tr_{species}_in_{index}",
                    },
                )
                index += 1


def write_csv(sbml_filename: str, info):
    """Write a csv file with SBML IDs, CD IDs, Names, Formulae, etc."""
    # pylint: disable=invalid-name
    with open(sbml_filename[:-4] + "csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for species, data in sorted(info.items()):
            writer.writerow(
                [species, data["name"], data["ref_species"], data["function"]]
            )


def mathml_to_ginsim(math: Optional[etree.Element], info) -> str:
    """Convert a MATHML boolean formula into its GinSIM representation."""
    if math is None:
        raise ValueError("Empty math element")
    if math.tag != "apply":
        raise ValueError(etree.tostring(math))
    children = list(math)
    if children[0].tag == "and":
        return "&".join(mathml_to_ginsim(x, info) for x in children[1:])
    if children[0].tag == "or":
        return "(" + "|".join(mathml_to_ginsim(x, info) for x in children[1:]) + ")"
    if children[0].tag == "eq":
        species = children[1].text
        species = info[species]["name"]
        if species is None:
            species = ""
        if children[2].text == "0":
            return "!" + species
        return species
    raise ValueError(etree.tostring(math))


def add_function_as_rdf(info, species: str, func: str):
    """Add a new RDF element containing the logical function and name."""
    rdf = etree.Element(f"{{{NS['rdf']}}}RDF")
    descr = etree.SubElement(
        rdf,
        f"{{{NS['rdf']}}}Description",
        attrib={f"{{{NS['rdf']}}}about": "#" + info[species]["ref_species"]},
    )
    bqbiol = etree.SubElement(descr, f"{{{NS['bqbiol']}}}isDescribedBy")
    bag = etree.SubElement(bqbiol, f"{{{NS['rdf']}}}Bag")
    etree.SubElement(
        bag,
        f"{{{NS['rdf']}}}li",
        attrib={f"{{{NS['rdf']}}}resource": "urn:casq:function:" + func},
    )
    bqbiol = etree.SubElement(descr, f"{{{NS['bqbiol']}}}isDescribedBy")
    bag = etree.SubElement(bqbiol, f"{{{NS['rdf']}}}Bag")
    etree.SubElement(
        bag,
        f"{{{NS['rdf']}}}li",
        attrib={
            f"{{{NS['rdf']}}}resource": "urn:casq:cdid:" + info[species]["ref_species"]
        },
    )
    add_rdf(info, species, rdf)
