# AI Context Manager

[![GitHub](https://img.shields.io/github/license/reshdesu/ai-context-manager)](https://github.com/reshdesu/ai-context-manager/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/ai-context-manager)](https://pypi.org/project/ai-context-manager/)

**Intelligent AI context management system for any project.**

AI Context Manager helps AI assistants maintain persistent context across conversations, automatically organize and optimize context files, and learn from your development patterns.

##  Features

- **Persistent AI Context**: Maintain context across conversations with AI assistants
- **Automated Maintenance**: Automatically organize, optimize, and version control context files
- **Pattern Learning**: Learn from your development patterns and suggest improvements
- **Multi-Project Support**: Manage context for different project types
- **Self-Hosting**: The system uses itself for its own development (ultimate dogfooding)
- **Professional Packaging**: Ready for PyPI distribution with proper CLI interface

##  Installation

### From Source (Development)

```bash
git clone https://github.com/reshdesu/ai-context-manager.git
cd ai-context-manager
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install ai-context-manager
```

##  Quick Start

### 1. Initialize AI Context for Your Project

```bash
ai-context init "My Project" --type web_application
```

This creates a comprehensive AI context system in your project:
- `ai_context/core.json` - Essential project information and rules
- `ai_context/architecture.json` - Project structure and technical details
- `ai_context/user_experience.json` - User needs and pain points
- `ai_context/troubleshooting.json` - Common issues and solutions
- `ai_context/learning_history.json` - Development learnings and patterns

### 2. Check Status

```bash
ai-context status
```

### 3. Maintain Context

```bash
ai-context maintain
```

##  Commands

| Command | Description |
|---------|-------------|
| `ai-context init <name> [--type <type>]` | Initialize AI context for a project |
| `ai-context status` | Show status of AI context system |
| `ai-context maintain` | Maintain and optimize context files |
| `ai-context version` | Show version information |

### Project Types

- `general` - General purpose project
- `web_application` - Web applications (React, Vue, Django, Flask, etc.)
- `desktop_application` - Desktop applications (Electron, Qt, etc.)
- `data_engineering` - Data science and ML projects
- `mobile_application` - Mobile apps (React Native, Flutter, etc.)

##  Self-Hosting

AI Context Manager uses itself for its own development - this is the ultimate validation of its effectiveness.

### Self-Hosted Context

The AI Context Manager maintains its own development context in `ai_context_self/`:
- Documents its own development decisions
- Tracks its own learning patterns
- Validates features by using them on itself
- Creates living documentation of the development process

### Self-Maintenance

```bash
# Create self-hosted context
python3 self_hosted_ai_context.py

# Maintain self-hosted context
python3 self_maintenance.py
```

##  Project Structure

```
ai-context-manager/
├── ai_context_manager/          # Core package
│   ├── __init__.py
│   ├── cli.py                   # Command-line interface
│   └── core.py                  # Core functionality
├── ai_context_self/             # Self-hosted context
│   ├── core.json
│   ├── architecture.json
│   ├── user_experience.json
│   ├── troubleshooting.json
│   └── learning_history.json
├── templates/                   # Project templates
│   ├── general/
│   ├── web_application/
│   ├── desktop_application/
│   └── data_engineering/
├── examples/                    # Usage examples
├── tests/                       # Test suite
├── setup.py                     # Package configuration
├── pyproject.toml              # Modern Python packaging
└── README.md                   # This file
```

##  Development

### Setup Development Environment

```bash
git clone https://github.com/reshdesu/ai-context-manager.git
cd ai-context-manager
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Run Tests

```bash
pytest
```

### Development Workflow

1. **Read Self-Hosted Context**: Start by reading `ai_context_self/` files
2. **Follow Self-Hosting Rules**: Use the system on itself
3. **Test New Features**: Validate by using on this project first
4. **Document Decisions**: Update `learning_history.json`
5. **Maintain Context**: Run self-maintenance regularly

##  Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Principles

- **Self-Hosting**: The system must work for its own development
- **Dogfooding**: Test features by using them on this project first
- **Documentation**: Document all development decisions in context
- **Quality**: Maintain high code quality and comprehensive testing

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Inspired by the need for persistent AI context in development workflows
- Built with self-hosting principles - the system uses itself for development
- Designed for maximum effectiveness and ease of use

##  Links

- **GitHub Repository**: [https://github.com/reshdesu/ai-context-manager](https://github.com/reshdesu/ai-context-manager)
- **PyPI Package**: Coming soon
- **Documentation**: [https://github.com/reshdesu/ai-context-manager/wiki](https://github.com/reshdesu/ai-context-manager/wiki)

##  Status

-  Core functionality implemented
-  CLI interface working
-  Self-hosting system operational
-  Professional packaging ready
-  PyPI distribution (in progress)
-  Advanced features (planned)
-  Web interface (planned)
-  Team collaboration (planned)

---

**The AI Context Manager is its own best customer and its own best test case.**
