# agent/prompts/__init__.py
from .scoring import SCORING_SYSTEM_PROMPT, build_scoring_user_prompt
from .outreach import OUTREACH_SYSTEM_PROMPT, build_outreach_user_prompt
from .case_study import CASE_STUDY_SYSTEM_PROMPT, build_case_study_user_prompt

__all__ = [
    "SCORING_SYSTEM_PROMPT",
    "build_scoring_user_prompt",
    "OUTREACH_SYSTEM_PROMPT",
    "build_outreach_user_prompt",
    "CASE_STUDY_SYSTEM_PROMPT",
    "build_case_study_user_prompt",
]