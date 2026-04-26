# agent/tasks/__init__.py
from .scoring import execute_scoring_task
from .outreach import execute_outreach_task
from .case_study import execute_case_study_task

__all__ = [
    "execute_scoring_task",
    "execute_outreach_task",
    "execute_case_study_task",
]