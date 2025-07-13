from pymatgen.core import Composition
from pymatgen.ext.matproj import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
from pymatgen.analysis.phase_diagram import PDEntry

# Your composition (can be normalized later)
comp = Composition({"N": 27,"B": 42,"Si": 18,"Y": 4,"Sc": 4,"La": 5})

# Use your Materials Project API key here
API_KEY = "6NxwYfunMJYCb40EaZ1B7Sktu9o1Q9qy"

# Connect to Materials Project
with MPRester(API_KEY) as mpr:
    # Get all entries involving these elements
    elements = [el.symbol for el in comp.elements]
    entries = mpr.get_entries_in_chemsys(elements)

    # Create the phase diagram from these entries
    phase_diagram = PhaseDiagram(entries)

    # We'll use a dummy energy; the e_above_hull result is valid regardless
    test_entry = PDEntry(composition=comp, energy=0)

    # Compute energy above hull
    _, e_above_hull = phase_diagram.get_decomp_and_e_above_hull(test_entry)

    # Check stability
    is_stable = e_above_hull < 1e-6

    print(f"Is the composition {comp} stable? {is_stable}")
    print(f"Energy above hull: {e_above_hull:.6f} eV/atom")