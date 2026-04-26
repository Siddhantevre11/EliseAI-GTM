"""
agent.py — Lead Enrichment Pipeline (redirects to agent/pipeline.py)

For backwards compatibility. New code should use agent.pipeline directly.
"""

from agent.pipeline import run_pipeline, run_batch

__all__ = ["run_pipeline", "run_batch"]