# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# General Instructions
- Write code following KISS, YAGNI, and DRY principles.
- When in doubt follow proven best practices for implementation.
- Do not commit to git without user approval.
- Do not run any servers, rather tell the user to run servers for testing.
- Always consider industry standard libraries/frameworks first over custom implementations.
- Never mock anything. Never use placeholders. Never omit code.
- Apply SOLID principles where relevant. Use modern framework features rather than reinventing solutions.
- Be brutally honest about whether an idea is good or bad.
- Make side effects explicit and minimal.
- Design database schema to be evolution-friendly (avoid breaking changes).

# File Organization & Modularity
- Default to creating multiple small, focused files rather than large monolithic ones
- Each file should have a single responsibility and clear purpose
- Keep files under 350 lines when possible - split larger files by extracting utilities, constants, types, or logical components into separate modules
- Separate concerns: utilities, constants, types, components, and business logic into different files
- Prefer composition over inheritance - use inheritance only for true 'is-a' relationships, favor composition for 'has-a' or behavior mixing

- Follow existing project structure and conventions - place files in appropriate directories. Create new directories and move files if deemed appropriate.
- Use well defined sub-directories to keep things organized and scalable
- Structure projects with clear folder hierarchies and consistent naming conventions
- Import/export properly - design for reusability and maintainability

# Type Hints (REQUIRED)
- **Always** use type hints for function parameters and return values
- Use `from typing import` for complex types
- Prefer `Optional[T]` over `Union[T, None]`
- Use Pydantic models for data structures

```python
# Good
from typing import Optional, List, Dict, Tuple

async def process_audio(
    audio_data: bytes,
    session_id: str,
    language: Optional[str] = None
) -> Tuple[bytes, Dict[str, Any]]:
    """Process audio through the pipeline."""
    pass
```
# Naming Conventions
- **Classes**: PascalCase (e.g., `VoicePipeline`)
- **Functions/Methods**: snake_case (e.g., `process_audio`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_AUDIO_SIZE`)
- **Private methods**: Leading underscore (e.g., `_validate_input`)
- **Pydantic Models**: PascalCase with `Schema` suffix (e.g., `ChatRequestSchema`, `UserSchema`)

# Documentation Requirements
- Every module needs a docstring
- Every public function needs a docstring
- Use Google-style docstrings
- Include type information in docstrings

```python
def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity between two texts.

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        Similarity score between 0 and 1

    Raises:
        ValueError: If either text is empty
    """
    pass
```

# Security First
- Never trust external inputs - validate everything at the boundaries
- Keep secrets in environment variables, never in code
- Log security events (login attempts, auth failures, rate limits, permission denials) but never log sensitive data (audio, conversation content, tokens, personal info)
- Authenticate users at the API gateway level - never trust client-side tokens
- Use Row Level Security (RLS) to enforce data isolation between users
- Design auth to work across all client types consistently
- Use secure authentication patterns for your platform
- Validate all authentication tokens server-side before creating sessions
- Sanitize all user inputs before storing or processing

# Error Handling
- Use specific exceptions over generic ones
- Always log errors with context
- Provide helpful error messages
- Fail securely - errors shouldn't reveal system internals

# Observable Systems & Logging Standards
- Every request needs a correlation ID for debugging
- Structure logs for machines, not humans - use JSON format with consistent fields (timestamp, level, correlation_id, event, context) for automated analysis
- Make debugging possible across service boundaries

# Using Gemini CLI for Large-Scale Code Analysis

When a task requires analyzing large files, multiple files, or entire directories that exceed Claude's context window, use the **Gemini CLI**.

**Command:** `gemini -p "@path/to/file 'Your prompt'"`

**Note:** Always critically evaluate Gemini's suggestions before implementation.

## Gemini Context Prompt

Add this context before your main prompt. It directs Gemini to act as an expert consultant for Claude.

```
You are an expert coding assistant advising another AI, Claude. Your goal is to provide precise, comprehensive technical guidance to help a human developer.

- Summarize your approach, then provide complete, runnable code examples.
- Explain key logic, best practices, and potential issues.
- If context is missing, ask specific questions about requirements, errors, or environment.
```

## Key Guidelines

### When to Use Gemini CLI

  * Analyzing entire codebases or large directories (`>100KB`).
  * Comparing multiple large files.
  * Understanding project-wide architecture, patterns, or dependencies.

### How to Include Files & Directories

Use the `@` syntax with **relative paths**.

  * **Single File:** `gemini -p "@src/main.py 'Explain this file'"`
  * **Multiple Files:** `gemini -p "@src/index.js @package.json 'Analyze dependencies'"`
  * **Directory:** `gemini -p "@src/ 'Summarize the architecture'"`
  * **Entire Project:** `gemini -p "@./ 'Give an overview of the project'"` (or use the `--all_files` flag)

### Example Use Cases

Frame your prompts as specific verification questions.

  * **Feature Check:** `gemini -p "@src/ Has dark mode been implemented? Show relevant files."`
  * **Security & Patterns:** `gemini -p "@src/ @api/ Is JWT auth used? List all auth middleware."`
  * **Test Coverage:** `gemini -p "@src/payment/ @tests/ Are there tests for the payment module?"`

# Context7 Documentation Server
**Repository**: [Context7 MCP Server](https://github.com/upstash/context7)

**When to use:**
- Working with external libraries/frameworks (React, FastAPI, Next.js, etc.)
- Need current documentation beyond training cutoff
- Implementing new integrations or features with third-party tools
- Troubleshooting library-specific issues

**Usage patterns:**
```python
# Resolve library name to Context7 ID
mcp__context7__resolve_library_id(libraryName="react")

# Fetch focused documentation
mcp__context7__get_library_docs(
    context7CompatibleLibraryID="/facebook/react",
    topic="hooks",
    tokens=8000
)
```

**Key capabilities:**
- Up-to-date library documentation access
- Topic-focused documentation retrieval
- Support for specific library versions
- Integration with current development practices

