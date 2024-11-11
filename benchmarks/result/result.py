"""Basic result classes for benchmarking."""

from uuid import UUID

from attrs import define, field
from attrs.validators import instance_of
from pandas import DataFrame

from baybe.serialization.core import converter
from baybe.serialization.mixin import SerialMixin
from benchmarks.definition.config import BenchmarkScenarioSettings
from benchmarks.result.metadata_class import ResultMetadata


@define(frozen=True)
class Result(SerialMixin):
    """A single result of the benchmarking."""

    benchmark_identifier: UUID = field(validator=instance_of(UUID))
    """The unique identifier of the benchmark running which can be set
    to compare different executions of the same benchmark setting."""

    settings: BenchmarkScenarioSettings = field(
        validator=instance_of(BenchmarkScenarioSettings)
    )
    """Settings which were applied to the benchmark."""

    benchmark_result: DataFrame = field(validator=instance_of(DataFrame))
    """The result of the benchmarked callable."""

    metadata: ResultMetadata = field(validator=instance_of(ResultMetadata))
    """The metadata of the benchmark result."""


converter.register_unstructure_hook(UUID, lambda x: str(x))
converter.register_structure_hook(UUID, lambda x, _: UUID(x))
