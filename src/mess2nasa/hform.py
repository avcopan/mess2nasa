"""Determine CBH basis for calculating heat of formation."""

from typing import Any

from automol import graph


def isogyric_basis(gra: Any) -> list[tuple[Any, float]]:
    """Determine the isogyric (CBH-0) basis for determining heat of formation.

    :param gra: AutoMol graph
    :return: A list of AutoMol graphs of basis species, along with their
    stoichiometric coefficients
    """
    # 1. Make hydrogens implicit
    gra = graph.implicit(gra)
    # 2. Break bonds
    gra = graph.remove_bonds(gra, graph.bonds(gra))
    # 3. Saturate with hydrogens and determine product components
    unp_dct = graph.atom_unpaired_electrons(gra)
    gra = graph.change_implicit_hydrogens(gra, unp_dct)
    gras = graph.connected_components(gra)
    basis = graph.unique_with_counts(gras)
    # 4. Determine the number of H2 molecules for saturation
    h2_count = sum(unp_dct.values()) / 2
    h2_gra = graph.from_data({0: "H", 1: "H"}, [(0, 1)])
    basis.append((h2_gra, -h2_count))
    return basis
