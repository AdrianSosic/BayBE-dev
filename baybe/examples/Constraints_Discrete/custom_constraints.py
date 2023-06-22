"""
This examples shows how a custom constraint can be created for a discrete searchspace.
It assumes that the reader is familiar with the basics of Baybe, and thus does not
explain the details of e.g. parameter creation. For additional explanation on these
aspects, we refer to the Basic examples.
"""
import numpy as np
import pandas as pd
from baybe.constraints import CustomConstraint

from baybe.core import BayBE
from baybe.parameters import Categorical, GenericSubstance, NumericDiscrete
from baybe.searchspace import SearchSpace
from baybe.targets import NumericalTarget, Objective
from baybe.utils import add_fake_results


# We begin by setting up some parameters for our experiments.
dict_solvent = {
    "water": "O",
    "C1": "C",
    "C2": "CC",
    "C3": "CCC",
    "C4": "CCCC",
    "C5": "CCCCC",
    "c6": "c1ccccc1",
    "C6": "CCCCCC",
}
solvent = GenericSubstance("Solvent", data=dict_solvent, encoding="RDKIT")
speed = Categorical(
    "Speed", values=["very slow", "slow", "normal", "fast", "very fast"], encoding="INT"
)
temperature = NumericDiscrete(
    "Temperature", values=list(np.linspace(100, 200, 10)), tolerance=0.5
)
concentration = NumericDiscrete("Concentration", values=[1, 2, 5, 10], tolerance=0.4)

parameters = [solvent, speed, temperature, concentration]

# The constraints are handled when creating the searchspace object.
# We thus need to define our constraint first as follows.


def custom_function(ser: pd.Series) -> bool:
    """
    Example for a custom validator / filer
    """
    # Below we initialize the CUSTOM constraint with all the parameters this function
    # should have access to. The function can then compute a completely user-defined
    # validation of the searchspace points

    if ser.Solvent == "water":
        if ser.Temperature > 120 and ser.Concentration > 5:
            return False
        if ser.Temperature > 180 and ser.Concentration > 3:
            return False
    if ser.Solvent == "C3":
        if ser.Temperature < 150 and ser.Concentration > 3:
            return False
    return True


# Custom constraints require a configuration dictionary, stating the type, the
# # parameters involved and the corresponding python function.
# Note that the parameters are accessed by names!
dict_constraint = {
    "type": "CUSTOM",
    "parameters": ["Concentration", "Solvent", "Temperature"],
    "validator": custom_function,
}
# We can now create the constraint and consequently also the searchspace
constraint = CustomConstraint.create(config=dict_constraint)
searchspace = SearchSpace.create(parameters=parameters, constraints=[constraint])

# We finally create an objective and the baybe object
objective = Objective(
    mode="SINGLE", targets=[NumericalTarget(name="yield", mode="MAX")]
)
baybe_obj = BayBE(searchspace=searchspace, objective=objective)
print(baybe_obj)

# The following loop performs some recommendations and manually verifies that the
# given constraints are obeyed.
N_ITERATIONS = 5
for kIter in range(N_ITERATIONS):
    print(f"\n\n##### ITERATION {kIter+1} #####")

    print("### ASSERTS ###")
    print(
        "Number of entries with water, temp above 120 and concentration above 5:      ",
        (
            baybe_obj.searchspace.discrete.exp_rep["Concentration"].apply(
                lambda x: x > 5
            )
            & baybe_obj.searchspace.discrete.exp_rep["Temperature"].apply(
                lambda x: x > 120
            )
            & baybe_obj.searchspace.discrete.exp_rep["Solvent"].eq("water")
        ).sum(),
    )
    print(
        "Number of entries with water, temp above 180 and concentration above 3:      ",
        (
            baybe_obj.searchspace.discrete.exp_rep["Concentration"].apply(
                lambda x: x > 3
            )
            & baybe_obj.searchspace.discrete.exp_rep["Temperature"].apply(
                lambda x: x > 180
            )
            & baybe_obj.searchspace.discrete.exp_rep["Solvent"].eq("water")
        ).sum(),
    )
    print(
        "Number of entries with C3, temp above 180 and concentration above 3:         ",
        (
            baybe_obj.searchspace.discrete.exp_rep["Concentration"].apply(
                lambda x: x > 3
            )
            & baybe_obj.searchspace.discrete.exp_rep["Temperature"].apply(
                lambda x: x < 150
            )
            & baybe_obj.searchspace.discrete.exp_rep["Solvent"].eq("C3")
        ).sum(),
    )

    rec = baybe_obj.recommend(batch_quantity=5)
    add_fake_results(rec, baybe_obj)
    baybe_obj.add_measurements(rec)
