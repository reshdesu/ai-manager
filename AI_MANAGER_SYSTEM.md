# AI Manager

A comprehensive AI agent communication and monitoring system with intelligent agents.

## Quick Start

### Start AI Manager
```bash
./scripts/start.sh
```

### Stop AI Manager
```bash
./scripts/stop.sh
```

### Check Status
```bash
./scripts/status.sh
```

## Access Points

- **Monitoring Website**: http://localhost:8000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## Components

### Services
- **Backend API Server** (Port 5000) - REST API for agent communication
- **Monitoring Website** (Port 8000) - Web interface with terminal aesthetic

### AI Agents
- **blaze-agent** - Backup and storage management
- **maya-agent** - 3D modeling and animation
- **ai-context-manager** - Core system manager and coordinator

## Features

- ✅ **Claude Integration** - All agents have full Claude API access
- ✅ **Autonomous Operation** - Agents run independently with intelligent decision making
- ✅ **Real-time Monitoring** - Web interface with traffic light status indicators
- ✅ **Agent Communication** - Inter-agent messaging and coordination
- ✅ **Self-hosting** - AI Manager manages itself (dogfooding approach)

## Troubleshooting

### Environment Variables
The system automatically loads `ANTHROPIC_API_KEY` from your `~/.bashrc` file. If you see "ANTHROPIC_API_KEY not found" warnings, ensure it's properly set in your bashrc.

### Services Not Starting
If services fail to start:
1. Run `./scripts/stop.sh` to clean up
2. Run `./scripts/start.sh` to restart everything
3. Check status with `./scripts/status.sh`

### Website Not Accessible
If the monitoring website is down:
1. Check if port 8000 is available: `ss -tlnp | grep 8000`
2. Restart AI Manager: `./scripts/stop.sh && ./scripts/start.sh`

## Architecture

The system uses a REST API architecture instead of WebSockets for better reliability:
- HTTP polling every 3 seconds for real-time updates
- Agent registration and heartbeat system
- Inter-agent communication via HTTP POST
- Traffic light status indicators for core systems

## Development

All agents are independent Python modules that inherit from `BaseIntelligentAgent` and provide:
- Claude API integration
- Autonomous task execution
- Message processing
- Performance tracking
- Fallback responses when Claude is unavailable
