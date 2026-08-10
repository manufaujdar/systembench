"""SystemBench: end-to-end evaluation for AI systems."""

from .comparison import RegressionPolicy, compare_reports
from .models import Evaluation, Scenario, Suite, SystemResult, TraceEvent, TrialResult
from .runner import BenchmarkRunner

__all__ = [
    "BenchmarkRunner",
    "Evaluation",
    "RegressionPolicy",
    "Scenario",
    "Suite",
    "SystemResult",
    "TraceEvent",
    "TrialResult",
    "compare_reports",
]

__version__ = "0.1.1"
