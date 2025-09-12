# AI Context Manager

Intelligent AI context management system for any project. Solve the problem of AI assistant forgetfulness with a persistent, learning knowledge base.

## Features

- **Persistent Learning** - Remembers solutions across AI conversations
- **Automated Maintenance** - Self-organizing and optimizing context
- **Version Control** - Track all changes with full history
- **Pattern Recognition** - Learns from recurring issues and solutions
- **Multi-Project Support** - Use across any type of project
- **Easy Integration** - Simple CLI interface and configuration

## Installation

```bash
pip install ai-context-manager
```

## Quick Start

### 1. Initialize a Project

```bash
ai-context init "My Project" --type web_application
```

### 2. Run Maintenance

```bash
ai-context maintain
```

### 3. Set Up Automation

```bash
ai-context install --cron --interval 30
```

## Supported Project Types

- `web_application` - React, Vue, Angular, etc.
- `backend_development` - APIs, microservices, databases
- `mobile_development` - iOS, Android, React Native
- `data_engineering` - ETL pipelines, data warehouses
- `machine_learning` - ML models, data science
- `devops` - Infrastructure, CI/CD, monitoring
- `desktop_application` - Desktop apps, GUI applications
- `general` - Any other type of project

## Configuration

Create `.ai-context.yaml` in your project root:

```yaml
project:
  name: "My Project"
  type: "web_application"

maintenance:
  auto_run: true
  interval_minutes: 30

integration:
  git_hooks: true
  cron_job: true
```

## CLI Commands

- `ai-context init` - Initialize new project
- `ai-context maintain` - Run maintenance
- `ai-context version` - Show version history
- `ai-context learn` - Analyze patterns
- `ai-context status` - Show project status
- `ai-context migrate` - Migrate from old system

## Examples

### Web Application
```bash
ai-context init "My React App" --type web_application
```

### Data Science Project
```bash
ai-context init "ML Pipeline" --type machine_learning
```

### DevOps Infrastructure
```bash
ai-context init "Kubernetes Cluster" --type devops
```

## Benefits

- **No More AI Forgetfulness** - Persistent knowledge across sessions
- **Automated Organization** - Self-maintaining context structure
- **Learning System** - Gets smarter with each use
- **Version Control** - Track all changes and rollback if needed
- **Cross-Project Reuse** - Use the same system across all projects

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: https://github.com/ai-context-manager/ai-context-manager/issues
- Documentation: https://ai-context-manager.readthedocs.io
