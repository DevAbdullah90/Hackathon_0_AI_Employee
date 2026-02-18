#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Autonomous Task Completion Pattern
Keeps the AI Employee working until tasks are complete.

This implements the "Stop hook" pattern from the hackathon requirements:
1. Orchestrator creates state file with prompt
2. AI works on task
3. AI tries to exit
4. Stop hook checks: Is task file in /Done?
   - YES -> Allow exit (complete)
   - NO -> Block exit, re-inject prompt (loop continues)
5. Repeat until complete or max iterations
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration
VAULT_PATH = Path("C:/Users/LENOVO X1 YOGA/OneDrive/Desktop/hakathone zero/AI_Employee_vault")
STATE_DIR = VAULT_PATH / "state"
MAX_ITERATIONS = 10
COMPLETION_PROMISE = "<promise>TASK_COMPLETE</promise>"


class RalphWiggumLoop:
    """
    Autonomous task completion loop.
    Keeps re-running until the task is marked complete.
    """

    def __init__(self, vault_path: Path = VAULT_PATH):
        self.vault_path = vault_path
        self.state_dir = vault_path / "state"
        self.needs_action = vault_path / "Needs_Action"
        self.done_dir = vault_path / "Done"
        self.in_progress = vault_path / "In_Progress"

        # Create directories
        self.state_dir.mkdir(exist_ok=True)
        self.in_progress.mkdir(exist_ok=True)

    def create_task_state(self, task_id: str, prompt: str, completion_check: str = "file_moved") -> Path:
        """
        Create a state file for tracking task progress.

        Args:
            task_id: Unique identifier for this task
            prompt: The task prompt to execute
            completion_check: How to verify completion ('file_moved' or 'promise')

        Returns:
            Path to the state file
        """
        state = {
            "task_id": task_id,
            "prompt": prompt,
            "completion_check": completion_check,
            "created_at": datetime.now().isoformat(),
            "iterations": 0,
            "max_iterations": MAX_ITERATIONS,
            "status": "pending",
            "history": []
        }

        state_file = self.state_dir / f"{task_id}.json"
        state_file.write_text(json.dumps(state, indent=2))
        return state_file

    def check_completion(self, task_id: str, completion_check: str, target_file: Optional[str] = None) -> bool:
        """
        Check if the task is complete.

        Two strategies:
        1. file_moved: Check if target file has been moved to /Done
        2. promise: Check if AI output contains TASK_COMPLETE promise
        """
        if completion_check == "file_moved" and target_file:
            done_file = self.done_dir / target_file
            return done_file.exists()

        elif completion_check == "promise":
            # Check latest output for promise
            state_file = self.state_dir / f"{task_id}.json"
            if state_file.exists():
                state = json.loads(state_file.read_text())
                for entry in state.get("history", []):
                    if COMPLETION_PROMISE in entry.get("output", ""):
                        return True
        return False

    def run_iteration(self, task_id: str, prompt: str) -> str:
        """
        Run a single iteration of the task.
        Returns the output from the AI.
        """
        # In a real implementation, this would call Claude Code
        # For now, we simulate the execution
        print(f"[Ralph] Running iteration for task: {task_id}")
        print(f"[Ralph] Prompt: {prompt[:100]}...")

        # Simulate processing - in production, this calls Claude
        output = f"Processed task {task_id} at {datetime.now().isoformat()}"

        return output

    def run_loop(self, task_id: str, prompt: str, target_file: Optional[str] = None,
                 completion_check: str = "file_moved") -> Dict[str, Any]:
        """
        Main Ralph Wiggum loop.
        Keeps running until task is complete or max iterations reached.

        Args:
            task_id: Unique task identifier
            prompt: The task to execute
            target_file: File to check in /Done (for file_moved strategy)
            completion_check: 'file_moved' or 'promise'

        Returns:
            Result dictionary with status and history
        """
        print(f"[Ralph] Starting loop for task: {task_id}")
        print(f"[Ralph] Completion strategy: {completion_check}")

        # Create initial state
        state_file = self.create_task_state(task_id, prompt, completion_check)

        iteration = 0
        while iteration < MAX_ITERATIONS:
            iteration += 1
            print(f"\n[Ralph] === Iteration {iteration}/{MAX_ITERATIONS} ===")

            # Load current state
            state = json.loads(state_file.read_text())

            # Check if already complete
            if self.check_completion(task_id, completion_check, target_file):
                print(f"[Ralph] Task {task_id} is COMPLETE!")
                state["status"] = "completed"
                state["completed_at"] = datetime.now().isoformat()
                state_file.write_text(json.dumps(state, indent=2))
                return {
                    "status": "completed",
                    "iterations": iteration,
                    "task_id": task_id
                }

            # Run iteration
            output = self.run_iteration(task_id, prompt)

            # Update state
            state["iterations"] = iteration
            state["history"].append({
                "iteration": iteration,
                "timestamp": datetime.now().isoformat(),
                "output": output
            })
            state_file.write_text(json.dumps(state, indent=2))

            # Check for promise-based completion
            if completion_check == "promise" and COMPLETION_PROMISE in output:
                print(f"[Ralph] Promise detected! Task complete.")
                state["status"] = "completed"
                state["completed_at"] = datetime.now().isoformat()
                state_file.write_text(json.dumps(state, indent=2))
                return {
                    "status": "completed",
                    "iterations": iteration,
                    "task_id": task_id
                }

            # Brief pause between iterations
            time.sleep(1)

        # Max iterations reached
        print(f"[Ralph] Max iterations ({MAX_ITERATIONS}) reached. Task incomplete.")
        state = json.loads(state_file.read_text())
        state["status"] = "max_iterations_reached"
        state_file.write_text(json.dumps(state, indent=2))

        return {
            "status": "max_iterations_reached",
            "iterations": iteration,
            "task_id": task_id
        }

    def process_needs_action(self) -> Dict[str, Any]:
        """
        Process all files in Needs_Action folder.
        Uses Ralph loop to ensure each is handled.
        """
        results = []

        for file in self.needs_action.glob("*.md"):
            task_id = f"process_{file.stem}_{int(time.time())}"
            prompt = f"Process the file: {file.name}. Read its contents and take appropriate action based on the type (email, whatsapp, etc). Move to Done when complete."

            result = self.run_loop(
                task_id=task_id,
                prompt=prompt,
                target_file=file.name,
                completion_check="file_moved"
            )
            results.append(result)

        return {
            "processed": len(results),
            "results": results
        }


def start_ralph_loop(prompt: str, completion_promise: str = COMPLETION_PROMISE,
                     max_iterations: int = MAX_ITERATIONS):
    """
    CLI entry point for starting a Ralph loop.

    Usage:
        python ralph_wiggum_loop.py "Process all files in /Needs_Action" --max-iterations 10
    """
    loop = RalphWiggumLoop()
    task_id = f"cli_task_{int(time.time())}"

    result = loop.run_loop(
        task_id=task_id,
        prompt=prompt,
        completion_check="promise"
    )

    print(f"\n[Ralph] Final result: {result}")
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else MAX_ITERATIONS
        start_ralph_loop(prompt, max_iterations=max_iter)
    else:
        # Demo mode
        print("Ralph Wiggum Loop - Autonomous Task Completion")
        print("=" * 50)
        print("\nUsage:")
        print('  python ralph_wiggum_loop.py "Your task prompt here" [max_iterations]')
        print("\nExample:")
        print('  python ralph_wiggum_loop.py "Process all emails in Needs_Action" 5')
        print("\nRunning demo...")

        loop = RalphWiggumLoop()
        result = loop.run_loop(
            task_id="demo_task",
            prompt="Demo: Process pending items and mark complete",
            completion_check="promise"
        )
        print(f"\nDemo result: {result}")
