"""
agent/llm_router.py — Task-Based LLM Routing

Centralizes all LLM calls with dynamic model/temperature selection based on task type.
"""

import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any

from groq import Groq

load_dotenv = __import__('dotenv', fromlist=['load_dotenv']).load_dotenv


class TaskType(Enum):
    """LLM task types with different model/temperature requirements."""
    SCORING = "scoring"           # temp: 0.0 - deterministic tier/score
    OUTREACH = "outreach"         # temp: 0.5 - creative email/talking points
    CASE_STUDY = "case_study"     # temp: 0.5 - creative storytelling


@dataclass
class TaskConfig:
    """Configuration for a task type."""
    model: str
    temperature: float
    max_tokens: int


# Default task configurations
TASK_CONFIGS = {
    TaskType.SCORING: TaskConfig(
        model=os.getenv("LLM_MODEL_SCORING", "llama-3.1-8b-instant"),
        temperature=0.0,
        max_tokens=512,
    ),
    TaskType.OUTREACH: TaskConfig(
        model=os.getenv("LLM_MODEL_OUTREACH", "llama-3.3-70b-versatile"),
        temperature=0.5,
        max_tokens=1024,
    ),
    TaskType.CASE_STUDY: TaskConfig(
        model=os.getenv("LLM_MODEL_CASE_STUDY", "llama-3.3-70b-versatile"),
        temperature=0.5,
        max_tokens=512,
    ),
}


class LLMRouter:
    """
    Centralized LLM router that assigns models and temperatures based on task type.
    
    Usage:
        router = LLMRouter()
        result = router.execute(TaskType.SCORING, system_prompt, user_prompt)
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self._fallback_mode = not bool(self.api_key)
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.client is not None
    
    def execute(
        self,
        task_type: TaskType,
        system_prompt: str,
        user_prompt: str,
        progress_callback: Callable[[str], None] = None,
    ) -> dict:
        """
        Execute an LLM task with task-specific model and temperature.
        
        Args:
            task_type: The type of task (SCORING, OUTREACH, CASE_STUDY)
            system_prompt: System prompt for the task
            user_prompt: User prompt with data context
            progress_callback: Optional callback for progress updates
        
        Returns:
            dict: Parsed JSON response from the LLM
        """
        if self._fallback_mode:
            return {"error": "LLM not available (no API key)"}
        
        config = TASK_CONFIGS[task_type]
        
        if progress_callback:
            progress_callback(f"LLM ({task_type.value}): {config.model}")
        
        try:
            response = self.client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                response_format={"type": "json_object"},
            )
            
            text = (response.choices[0].message.content or "").strip()
            return self._parse_json(text)
            
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_json(self, text: str) -> dict:
        """Parse JSON from LLM response, handling markdown fences."""
        # Strip markdown fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]).strip()
        
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Find the JSON object
        start = text.find("{")
        if start != -1:
            depth = 0
            end = -1
            for i, ch in enumerate(text[start:], start):
                if ch == "{": 
                    depth += 1
                elif ch == "}": 
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            
            if end != -1:
                try:
                    return json.loads(text[start:end+1])
                except json.JSONDecodeError:
                    pass
        
        return {"error": "Failed to parse JSON from LLM response", "raw": text[:500]}


def generate_gtm_intel(
    task_type: TaskType,
    system_prompt: str,
    user_prompt: str,
    progress_callback: Callable[[str], None] = None,
) -> dict:
    """
    Convenience function for generating GTM intelligence.
    
    Centralizes all LLM interactions into a single function call.
    
    Args:
        task_type: Type of task (SCORING, OUTREACH, CASE_STUDY)
        system_prompt: Task-specific system prompt
        user_prompt: Data context user prompt
        progress_callback: Optional progress callback
    
    Returns:
        dict: LLM-generated content
    """
    router = LLMRouter()
    return router.execute(task_type, system_prompt, user_prompt, progress_callback)