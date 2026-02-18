import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class SkillExecutor:
    """Executes skills defined in markdown files using Gemini"""
    
    def __init__(self, skills_dir: Path, vault_path: Path):
        self.skills_dir = skills_dir
        self.vault_path = vault_path
        self.client = GeminiClient()
        
    def load_skill(self, skill_name: str) -> Optional[str]:
        """Load skill definition from markdown file"""
        # Try finding the skill in subdirectories
        for skill_path in self.skills_dir.rglob("SKILL.md"):
            if skill_path.parent.name == skill_name:
                return skill_path.read_text(encoding='utf-8')
        
        # Try direct file match
        direct_path = self.skills_dir / f"{skill_name}.md"
        if direct_path.exists():
            return direct_path.read_text(encoding='utf-8')
            
        return None

    def execute_skill(self, skill_name: str, context: Dict[str, Any], task_content: str) -> Dict[str, Any]:
        """
        Execute a skill by constructing a prompt for Gemini
        
        Args:
            skill_name: Name of the skill to execute (folder name)
            context: Dictionary of context variables (business goals, user preferences, etc.)
            task_content: The specific task or input content to process
            
        Returns:
            Dictionary containing the execution result
        """
        skill_def = self.load_skill(skill_name)
        if not skill_def:
            return {"success": False, "error": f"Skill '{skill_name}' not found"}
            
        system_instruction = f"""You are an AI assistant executing a specific skill.
        
SKILL DEFINITION:
{skill_def}

YOUR GOAL:
Execute this skill faithfully based on the provided input and context.
Follow the steps defined in the skill definition.
Output the result in Valid JSON format unless the skill specifically asks for a file or text output.
"""

        prompt = f"""
CONTEXT:
{json.dumps(context, indent=2, default=str)}

TASK INPUT:
{task_content}

EXECUTE SKILL:
Please execute the '{skill_name}' skill on the above task input.
"""

        try:
            # For now, we assume most skills should return structured data or a specific file content
            # We can refine this to handle different output types based on skill definition
            result = self.client.generate_structured_json(prompt, system_instruction=system_instruction)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Skill execution failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_plan_skill(self, task_content: str) -> Dict[str, Any]:
        """Specialized executor for create-plan skill to return Plan.md content"""
        # This is a helper to verify the specific 'create-plan' skill 
        return self.execute_skill('create-plan', {}, task_content)
