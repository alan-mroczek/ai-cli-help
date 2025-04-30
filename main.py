#!/usr/bin/env python3
"""Entry point for Command Helper."""
import argparse
import subprocess
from typing import List, Optional
from pathlib import Path

from utils import (
    load_env,
    build_context,
    spinner
)
from model import get_suggestions

PROJECT_DIR = Path(__file__).resolve().parent
cfg = load_env()

def parse_args() -> argparse.Namespace:
    """Parse and return command line arguments with defaults from environment."""
    parser = argparse.ArgumentParser(
        prog="aih",
        description="""Suggest shell commands with LLM assistance."""
    )
    parser.add_argument("prompt", nargs="+", help="Describe what you want to do")
    parser.add_argument(
        "--context",
        action="store_true",
        default=cfg.get("INCLUDE_CONTEXT", "").lower() in ("true", "yes", "1"),
        help="Include directory & git context in the LLM prompt (default from INCLUDE_CONTEXT in .env)",
    )
    parser.add_argument(
        "--model",
        default=cfg.get("MODEL", cfg.get("OPENAI_MODEL", "openai/gpt-4o-mini")),
        help="Override model name (default from MODEL in .env)",
    )
    parser.add_argument(
        "--max", 
        dest="max_suggestions", 
        type=int, 
        default=int(cfg.get("MAX_SUGGESTIONS", 3)),
        help="Max suggestions (default from MAX_SUGGESTIONS in .env)"
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        default=cfg.get("REQUIRE_CONFIRMATION", "").lower() not in ("true", "yes", "1"),
        help="Skip command confirmation prompt (default from REQUIRE_CONFIRMATION in .env)"
    )
    return parser.parse_args()


class ChoiceResult:
    """Result from the choose function with different possible actions."""
    def __init__(self, cmd=None, action=None, comment=None):
        self.cmd = cmd  # Selected command
        self.action = action  # 'execute', 'regenerate', 'comment'
        self.comment = comment  # User comment if action is 'comment'


def display_suggestions(suggestions: List[str]) -> None:
    """Display the command suggestions."""
    print("\nSuggestions:")
    for idx, cmd in enumerate(suggestions, start=1):
        print(f"  {idx}. {cmd}")
    
    print("\nOptions:")
    print("  Enter a number to select a command")
    print("  r - Regenerate suggestions")
    print("  c - Add a comment or clarification")
    print("  0 or empty - Quit")


def choose(suggestions: List[str]) -> ChoiceResult:
    """Present suggestions and get user choice, including regenerate and comment options."""
    result = ChoiceResult()
    
    while True:
        display_suggestions(suggestions)
        
        choice = input("\nYour choice: ").strip().lower()
        
        if not choice:
            return result  # Empty choice, return None cmd

        if choice == "r":
            result.action = "regenerate"
            return result
            
        if choice == "c":
            comment = input("Enter your comment or clarification: ").strip()
            if comment:
                result.action = "comment"
                result.comment = comment
                return result
            continue  # No comment provided, ask again
        
        if choice.isdigit():
            idx = int(choice)
            if idx == 0:
                return result  # Quit selected
            if 1 <= idx <= len(suggestions):
                result.cmd = suggestions[idx-1]
                result.action = "execute"
                return result
        
        print("Invalid choice. Please try again.")


def confirm(cmd: str) -> bool:
    """Ask for confirmation before executing a command."""
    ans = input(f"Execute '{cmd}'? [y/N]: ").strip().lower()
    return ans in {"y", "yes"}


def build_full_context(args, prev_suggestions: List[str] = None, user_comment: str = None) -> Optional[str]:
    """Build the full context including commands.md, environment context, and user feedback."""
    # Get commands.md content regardless of context flag
    cmd_md_path = PROJECT_DIR / "commands.md"
    commands_content = ""
    if cmd_md_path.is_file():
        try:
            with open(cmd_md_path, 'r') as f:
                commands_content = f.read().strip()
        except Exception:
            pass
    
    # Get additional context info if context flag is set
    additional_ctx = build_context() if args.context else None
    
    # Combine contexts
    context_parts = []
    
    if commands_content:
        context_parts.append("IMPORTANT USER PREFERENCES - This document shows what the user might want. Use this information whenever relevant:\n\n" + commands_content)
    
    if additional_ctx:
        context_parts.append(additional_ctx)
        
    # Add previous suggestions and user comment if available
    if prev_suggestions and user_comment:
        feedback = "Previous suggestions:\n"
        for idx, sugg in enumerate(prev_suggestions, start=1):
            feedback += f"{idx}. {sugg}\n"
        feedback += f"\nUser comment: {user_comment}"
        context_parts.append(feedback)
    
    # Join all context parts with double newlines
    return "\n\n".join(context_parts) if context_parts else None


def execute_command(cmd: str, skip_confirm: bool = False) -> None:
    """Execute the selected command with optional confirmation."""
    if skip_confirm or confirm(cmd):
        print("Running...\n")
        subprocess.run(cmd, shell=True)
    else:
        print("Aborted.")


def get_command_suggestions(prompt: str, context: Optional[str], model_name: str, max_suggestions: int) -> List[str]:
    """Get command suggestions from the model with a spinner."""
    with spinner("Thinking..."):
        suggestions = get_suggestions(
            prompt=prompt,
            context=context,
            model_name=model_name,
            max_suggestions=max_suggestions,
        )
    
    if not suggestions:
        print("No suggestions.\n")
    
    return suggestions


def main() -> None:
    """Main program logic."""
    args = parse_args()
    user_prompt = " ".join(args.prompt)
    prev_suggestions = []
    user_comment = None
    
    while True:
        # Build context for the model
        ctx = build_full_context(args, prev_suggestions, user_comment)
        
        # Get suggestions
        suggestions = get_command_suggestions(
            prompt=user_prompt,
            context=ctx,
            model_name=args.model,
            max_suggestions=args.max_suggestions,
        )

        if not suggestions:
            return

        # Save suggestions for potential regeneration
        prev_suggestions = suggestions.copy()
        
        # Get user choice
        choice_result = choose(suggestions)
        
        # Handle the different actions
        if not choice_result or not choice_result.action:
            print("Aborted.")
            return
            
        if choice_result.action == "regenerate":
            print("Regenerating suggestions...")
            continue
            
        if choice_result.action == "comment":
            user_comment = choice_result.comment
            print("Adding your comment and regenerating...")
            continue
            
        if choice_result.action == "execute":
            execute_command(choice_result.cmd, args.no_confirm)
            return


if __name__ == "__main__":
    try:
        print("Command Helper - Your AI Assistant for Shell Commands")
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
