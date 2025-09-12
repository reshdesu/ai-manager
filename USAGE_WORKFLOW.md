# AI Context Manager Usage Workflow

## How We Use AI Context Manager in This Project

This document explains how the AI Context Manager project uses itself for development - the ultimate dogfooding approach.

## Self-Hosting Workflow

### 1. **Development Process**

When working on AI Context Manager development:

```bash
cd /home/yamnik/ai-context-manager

# Always start by reading the self-hosted context
uv run ai-context status

# Check what the AI Context Manager knows about itself
cat ai_context_self/core.json | jq '.ai_assistant_rules'

# Run self-maintenance to ensure context is up to date
uv run python3 self_maintenance.py
```

### 2. **Making Changes**

Before making any changes to the AI Context Manager:

```bash
# 1. Read the self-hosted context
uv run ai-context status

# 2. Understand current state
cat ai_context_self/learning_history.json | jq '.conversation_learnings'

# 3. Make your changes to the code

# 4. Test changes using the system on itself
uv run ai-context --help
uv run ai-context init "Test Project" --type general

# 5. Update self-hosted context with new learnings
uv run python3 self_maintenance.py

# 6. Commit changes
git add . && git commit -m "Description of changes"
git push
```

### 3. **Context Maintenance**

Regular maintenance of the AI Context Manager's own context:

```bash
# Daily maintenance
uv run python3 self_maintenance.py

# Check for changes in context files
uv run ai-context status

# Update learning history with new insights
# Edit ai_context_self/learning_history.json manually
```

## Integration with Other Projects

### 1. **Global Availability Setup**

To make AI Context Manager available for all projects:

```bash
cd /home/yamnik/ai-context-manager

# Set up global availability
uv run python3 scripts/setup_global_ai_context.py

# This creates:
# - ai-context-global.py (global script)
# - templates/mandatory_ai_context/ (project template)
```

### 2. **Using with BlackBlaze Project**

From the BlackBlaze project:

```bash
cd /home/yamnik/blackblaze2-backup

# Use AI Context Manager via integration script
python3 scripts/use_ai_context_manager.py status
python3 scripts/use_ai_context_manager.py maintain

# Check what AI Context Manager knows about BlackBlaze
cat ai_context/core.json | jq '.project'
```

## AI Assistant Usage Rules

### For AI Assistants Working on AI Context Manager

**MANDATORY**: Always read these files before starting work:

1. **`ai_context_self/core.json`** - Essential rules and self-hosting guidelines
2. **`ai_context_self/architecture.json`** - Package structure and development workflow
3. **`ai_context_self/user_experience.json`** - Developer experience and user needs
4. **`ai_context_self/troubleshooting.json`** - Development debugging guides
5. **`ai_context_self/learning_history.json`** - Development learnings and decisions

### Self-Hosting Rules

From `ai_context_self/core.json`:

```json
"self_hosting_rules": [
  "Always use the AI Context Manager's own context when developing it",
  "Test new features by using them on this project first",
  "Document learnings in this context system",
  "Validate that the system works by using it on itself"
],
"mandatory_requirements": [
  "CRITICAL: AI Context Manager is MANDATORY for ALL projects",
  "Every project MUST have AI Context Manager integration",
  "All AI assistants MUST read project's ai_context files",
  "Context maintenance is MANDATORY and cannot be skipped",
  "Self-hosting principles MUST be applied to all projects",
  "Global AI Context Manager availability is REQUIRED"
]
```

## Development Commands

### Core AI Context Manager Commands

```bash
# Initialize AI context for a new project
uv run ai-context init "Project Name" --type web_application

# Check status of AI context system
uv run ai-context status

# Maintain and optimize context files
uv run ai-context maintain

# Show version information
uv run ai-context version
```

### Self-Hosting Commands

```bash
# Create self-hosted context (if missing)
uv run python3 self_hosted_ai_context.py

# Maintain self-hosted context
uv run python3 self_maintenance.py

# Validate self-hosting functionality
uv run python3 scripts/validate_self_hosting.py

# Check AI context configuration
uv run python3 scripts/check_ai_context.py
```

### Development Tools

```bash
# Code formatting and linting
uv run black .
uv run ruff check .
uv run isort .

# Type checking
uv run mypy .

# Run tests
uv run pytest

# Pre-commit hooks
uv run pre-commit run --all-files
```

## Project Integration Examples

### Example 1: Adding a New CLI Command

```bash
# 1. Read self-hosted context
cat ai_context_self/core.json | jq '.project.entry_points'

# 2. Make changes to ai_context_manager/cli.py

# 3. Test the new command
uv run ai-context --help  # Should show new command

# 4. Test with a real project
uv run ai-context init "Test" --type general

# 5. Update self-hosted context
uv run python3 self_maintenance.py

# 6. Update learning history
# Edit ai_context_self/learning_history.json with new insights

# 7. Commit changes
git add . && git commit -m "Add new CLI command: xyz"
git push
```

### Example 2: Improving Context Maintenance

```bash
# 1. Read current maintenance approach
cat ai_context_self/architecture.json | jq '.development_workflow.maintenance'

# 2. Make improvements to core.py maintenance logic

# 3. Test improvements on self-hosted context
uv run python3 self_maintenance.py

# 4. Validate improvements work
uv run ai-context maintain

# 5. Update architecture documentation
# Edit ai_context_self/architecture.json

# 6. Update learning history
# Edit ai_context_self/learning_history.json

# 7. Commit changes
git add . && git commit -m "Improve context maintenance algorithm"
git push
```

## Validation and Testing

### Self-Hosting Validation

The AI Context Manager must always pass these tests:

```bash
# 1. Can it read its own context?
uv run ai-context status

# 2. Can it maintain its own context?
uv run python3 self_maintenance.py

# 3. Can it learn from its own development?
cat ai_context_self/learning_history.json | jq '.conversation_learnings'

# 4. Can it validate itself?
uv run python3 scripts/validate_self_hosting.py
```

### Integration Testing

Test integration with other projects:

```bash
# Test with BlackBlaze project
cd /home/yamnik/blackblaze2-backup
python3 scripts/use_ai_context_manager.py status

# Test global availability (when set up)
ai-context status  # If global symlink is created

# Test project template
cd /tmp
cp -r /home/yamnik/ai-context-manager/templates/mandatory_ai_context/* .
python setup_mandatory_ai_context.py "Test Project"
```

## Key Principles

### 1. **Self-Hosting First**
- Every feature must work on the AI Context Manager project itself
- Use the system to develop the system
- Validate effectiveness by using it on itself

### 2. **Context-Driven Development**
- Always read context files before making changes
- Update context files when making changes
- Document learnings in the context system

### 3. **Mandatory Usage**
- AI Context Manager is mandatory for all projects
- No project can be developed without AI context
- Global availability ensures consistency

### 4. **Living Documentation**
- Context files serve as living documentation
- Learning history tracks development insights
- Architecture evolves with the system

## Benefits of This Approach

1. **Immediate Validation** - Features are tested on a real project (itself)
2. **Living Documentation** - Context files document the development process
3. **Quality Assurance** - System must work for its own development
4. **User Confidence** - Demonstrates effectiveness through self-use
5. **Continuous Improvement** - System learns from its own development

**The AI Context Manager is its own best customer and its own best test case!**
