"""
Scenario Validator (Root Alias).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.scenario.validator import ScenarioValidator, ValidationResult

__all__ = [
    "ScenarioValidator",
    "ValidationResult",
]
