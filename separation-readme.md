# OpenClaw Dashboard System - Separated Deployments

This repository now has separate deployments for the main dashboard and demo system to ensure security and isolation.

## Architecture

### Main Dashboard
- Located in: `ui/` directory
- Connects to PostgreSQL with real data
- For internal/private use only
- Access to sensitive information

### Demo Dashboard
- Located in: `demo-dashboard/` directory
- Uses synthetic data only
- For public-facing demonstrations
- Complete isolation from main system

## Deployment Structure

### Main Dashboard (Internal)
- Runs locally using: `launch_dashboard.sh`
- Connects to your PostgreSQL database
- Full access to real project data
- Not exposed to public internet

### Demo Dashboard (Public)
- Deployed to Vercel: `demo-dashboard/`
- Uses generated synthetic data
- Completely isolated from main system
- Public URL for demonstrations

## Deployment Instructions

### Deploy Demo to Vercel
```bash
# Make sure you're logged into Vercel
vercel login

# Deploy the demo
./deploy-demo-to-vercel.sh
```

### Run Main Dashboard Locally
```bash
# From the main project directory
./launch_dashboard.sh
```

## Security Benefits

1. **Complete Isolation**: Demo system has zero access to main database
2. **No Sensitive Data**: Demo uses only synthetic data
3. **Separate Environments**: Different codebases, different deployments
4. **Risk Mitigation**: Public exposure affects only demo data

## Development

When updating the dashboard UI:
1. Update the shared template in `templates/dashboard.html`
2. Changes automatically apply to both systems
3. Test locally before deploying to Vercel

The demo system maintains the same look and feel as the main system while ensuring security through complete isolation.