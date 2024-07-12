"""Kernel tests."""

from typing import Any

import numpy as np
from attrs import asdict, has
from hypothesis import given

from baybe.kernels.base import Kernel

from .hypothesis_strategies.kernels import kernels

_RENAME_DICT: dict[str, str] = {
    "base_kernels": "kernels",
}
"""Dictionary for resolving name differences between BayBE and GPyTorch attributes."""


def validate_kernel_components(obj: Any, mapped: Any) -> None:
    """Validate that all kernel components are translated correctly.

    Args:
        obj: An object occurring as part of a BayBE kernel.
        mapped: The corresponding object in the translated GPyTorch kernel.
    """
    # Compare attribute by attribute
    for name, component in asdict(obj, recurse=False).items():
        # If the BayBE component is `None`, the GPyTorch component might not even
        # exist, so we skip
        if component is None:
            continue

        # Resolve attribute naming differences
        mapped_name = _RENAME_DICT.get(name, name)

        # If the attribute does not exist in the GPyTorch version, it must be an
        # initial value. Because setting initial values involves going through
        # constraint transformations on GPyTorch side (i.e., difference between
        # `<attr>` and `raw_<attr>`), the numerical values will not be exact, so
        # we check only for approximate matches.
        if (mapped_component := getattr(mapped, mapped_name, None)) is None:
            assert name.endswith("_initial_value")
            assert np.isclose(
                component, getattr(mapped, name.removesuffix("_initial_value")).item()
            )

        # If the component is itself another attrs object, recurse
        elif has(component):
            validate_kernel_components(component, mapped_component)

        # Same for collections of BayBE objects (coming from composite kernels)
        elif isinstance(component, tuple) and all(has(c) for c in component):
            for c, m in zip(component, mapped_component):
                validate_kernel_components(c, m)

        # On the lowest component level, simply check for equality
        else:
            assert component == mapped_component


@given(kernels())
def test_kernel_assembly(kernel: Kernel):
    """Turning a BayBE kernel into a GPyTorch kernel raises no errors and all its
    components are translated correctly."""  # noqa
    k = kernel.to_gpytorch()
    validate_kernel_components(kernel, k)
