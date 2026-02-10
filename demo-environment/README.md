# OpenClaw Demo Environment

Welcome to the OpenClaw Demo Environment! This is a completely isolated environment that showcases OpenClaw's capabilities using synthetic data and mock services.

## Security & Isolation

- 🔒 **Complete isolation** from real systems
- 🛡️ **Synthetic data only** - no access to real information
- 🌐 **No network access** to real services
- 🔐 **No credentials** accessible in demo mode

## Features Demonstrated

- Calendar and scheduling management
- Contact organization
- Financial portfolio tracking
- Smart home/IoT device simulation
- Web research capabilities
- Task management
- Code assistance

## Getting Started

### Prerequisites
- Python 3.8+
- Flask installed (`pip install flask`)

### Quick Start

1. Navigate to the demo environment directory:
   ```bash
   cd /home/fred/.openclaw/workspace/demo-environment
   ```

2. Start the demo:
   ```bash
   ./scripts/start_demo.sh
   ```

3. Interact with the demo agent by typing commands like:
   - `calendar` - View synthetic calendar events
   - `contacts` - View synthetic contact information
   - `finance` - View synthetic portfolio data
   - `iot` - View simulated smart home devices
   - `help` - See all available commands

4. Type `quit` to exit the demo

### Alternative Start

You can also run the demo agent directly:
```bash
python3 demo_agent.py --config ./config/demo_config.yaml
```

## Demo Scenarios

### Basic Demo
Demonstrates core OpenClaw capabilities with simple commands.

### Financial Analysis Demo
Showcases the portfolio tracking and analysis features.

### Smart Home Demo
Simulates IoT device management and automation.

### Productivity Demo
Focuses on calendar, contacts, and task management.

## Managing the Demo

- **Reset**: Run `./scripts/reset_demo.sh` to return to a clean state
- **Configuration**: Edit `config/demo_config.yaml` to modify demo behavior
- **Data**: Modify `data/synthetic_data.json` to customize demo data

## Architecture

- `demo_agent.py` - Main demo agent that responds to commands
- `config/demo_config.yaml` - Demo-specific configuration
- `data/synthetic_data.json` - All demo data is contained here
- `mocks/` - Simulated service APIs
- `scripts/` - Utility scripts for managing the demo

## Customization

To customize the demo for your needs:

1. Modify the synthetic data in `data/synthetic_data.json`
2. Adjust configuration in `config/demo_config.yaml`
3. Extend the demo agent in `demo_agent.py` with new commands

## Safety

- This demo environment is completely safe to share publicly
- No real data is accessible from this environment
- All data is synthetic and can be freely shared
- Mock services return predetermined responses

## Support

For questions about the demo environment, please refer to the main OpenClaw documentation or contact the development team.