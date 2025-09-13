# AI Context Manager - Automated Startup

This system automatically handles:
- ✅ Environment variable detection and setup
- ✅ Latest Claude model selection
- ✅ Service startup in correct order
- ✅ Health monitoring
- ✅ Automatic restarts

## Quick Start

### Option 1: Simple Launcher
```bash
./start.sh
```

### Option 2: Direct Python
```bash
uv run python3 start_ai_context_manager.py
```

### Option 3: Systemd Service (Auto-start on boot)
```bash
# Copy service file
sudo cp ai-context-manager.service /etc/systemd/system/

# Enable and start
sudo systemctl enable ai-context-manager
sudo systemctl start ai-context-manager

# Check status
sudo systemctl status ai-context-manager
```

## What It Does Automatically

1. **Finds API Key**: Searches for `ANTHROPIC_API_KEY` in:
   - Environment variables
   - `~/.bashrc` file
   - `.env` file in project directory

2. **Detects Latest Claude Model**: Automatically uses the newest available model:
   - Latest Sonnet (recommended)
   - Falls back to Opus or Haiku if needed
   - Caches model selection for 1 hour

3. **Starts Services in Order**:
   - Backend API (port 5000)
   - Monitoring Website (port 8000)
   - AI Context Manager Agent
   - Blaze Agent
   - Maya Agent

4. **Health Monitoring**: Checks all services are running properly

5. **Graceful Shutdown**: Stops all services cleanly on Ctrl+C

## Configuration

Edit `ai_context_manager_config.json` to customize:
- Service startup order and delays
- Claude model preferences
- Health check intervals
- Logging levels

## Monitoring

- **Web Interface**: http://localhost:8000
- **API Health**: http://localhost:5000/health
- **System Stats**: http://localhost:5000/api/stats

## Troubleshooting

If services fail to start:
1. Check API key is set correctly
2. Ensure ports 5000 and 8000 are available
3. Check logs for specific error messages
4. Verify all Python dependencies are installed

## Manual Override

To manually start individual services:
```bash
# Backend API
uv run python3 backend_api_service_simple.py &

# Monitoring Website  
uv run python3 monitoring_website.py &

# AI Context Manager Agent
uv run python3 ai_context_manager_agent.py &

# Other Agents
uv run python3 blaze_agent.py &
uv run python3 maya_agent.py &
```

## Environment Variables

The system automatically detects `ANTHROPIC_API_KEY` from:
- Current environment
- `~/.bashrc` export statements
- `.env` file in project root

You can also set it manually:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```
