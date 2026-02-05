# OpenClaw Demo Deployment Guide

This guide explains how to deploy the OpenClaw demo system to various platforms while maintaining security and isolation from your main OpenClaw instance.

## Architecture Overview

The OpenClaw demo system uses a **shared template architecture**:
- Common HTML template in `templates/dashboard.html`
- Template renderer in `templates/renderer.py`
- Different configurations for main system vs demo system
- Same UI code reused across all platforms and deployments

## Vercel Deployment

### Prerequisites
- Vercel account (free tier available)
- Git repository with your code

### Steps
1. Create a new project on Vercel
2. Link your GitHub repository containing the demo code
3. Set the build command to: `pip install flask`
4. Set the output directory to the root
5. Configure the build settings to use the Python runtime
6. Deploy!

Alternatively, use the Vercel CLI:
```bash
npm install -g vercel
vercel
```

### Configuration
- The demo will be available at `https://your-project.vercel.app/demo`
- No environment variables needed (uses synthetic data)
- Auto-scaling with Vercel's infrastructure
- Uses shared template architecture for consistency

## Cloudflare Workers Deployment

### Prerequisites
- Cloudflare account
- Wrangler CLI installed: `npm install -g wrangler`
- Account ID from Cloudflare dashboard

### Steps
1. Authenticate with Cloudflare:
   ```bash
   wrangler login
   ```

2. Update `wrangler.toml` with your account ID:
   ```toml
   account_id = "your_actual_account_id"
   ```

3. Deploy the worker:
   ```bash
   wrangler deploy
   ```

### Configuration
- The demo will be available at `https://your-worker.your-subdomain.workers.dev`
- Workers provide excellent global performance
- Free tier includes generous request limits
- Uses shared template architecture adapted for JavaScript

## Render Deployment

### Prerequisites
- Render account (free tier available)

### Steps
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the runtime to Python
4. Set the build command to:
   ```
   pip install flask && python vercel_server.py
   ```
5. Set the start command to:
   ```
   python vercel_server.py
   ```
6. Set the environment variable PORT to $PORT
7. Deploy!

### Configuration
- The demo will be available at `https://your-project.onrender.com`
- Auto-deploys on git pushes
- Free tier with reasonable limits
- Uses shared template architecture for consistency

## Railway Deployment

### Prerequisites
- Railway account (free tier available)

### Steps
1. Create a new project on Railway
2. Connect your GitHub repository
3. Choose Python template
4. Add the following to your Dockerfile or use the default Python setup
5. Deploy!

### Configuration
- The demo will be available at a railway.app domain
- Great for quick deployments
- Generous free tier
- Uses shared template architecture for consistency

## Fly.io Deployment

### Prerequisites
- Fly.io account
- Fly CLI installed

### Steps
1. Install Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Create fly.toml:
   ```bash
   fly launch
   ```

3. Deploy:
   ```bash
   fly deploy
   ```

### Configuration
- The demo will be available at `https://your-app.fly.dev`
- Edge computing across multiple regions
- Good free tier
- Uses shared template architecture for consistency

## GitHub Pages + Serverless Functions (Alternative)

For a hybrid approach:
1. Host the frontend on GitHub Pages
2. Use Netlify Functions or Vercel API routes for backend
3. Provides excellent performance and cost
4. Uses shared template architecture for consistency

## Security Best Practices

Regardless of platform:

1. **Never expose real data**: The demo uses synthetic data only
2. **No access to main systems**: Demo runs in complete isolation
3. **Rate limiting**: All platforms provide built-in rate limiting
4. **No secrets needed**: Demo doesn't require authentication
5. **Monitor traffic**: Keep an eye on usage patterns
6. **Template security**: Shared templates sanitize all inputs

## Custom Domain Setup

Most platforms allow custom domains:
- Vercel: Dashboard → Settings → Domains
- Cloudflare: Dashboard → Workers & Pages → Custom Domains
- Render: Dashboard → Settings → Domains
- Railway: Dashboard → Settings → Domains

## Performance Optimization

- The demo is lightweight by design
- Assets are served efficiently
- Shared template reduces code duplication
- Synthetic data generation is fast
- Caching can be implemented if needed

## Cost Considerations

- All mentioned platforms offer free tiers
- Traffic-based pricing kicks in at higher usage
- For demonstration purposes, free tiers should suffice
- Shared template architecture reduces maintenance costs
- Monitor usage to avoid unexpected charges

## Updating the Demo

After deployment:
1. Make changes to the shared template in `templates/dashboard.html`
2. Changes propagate to all platforms automatically
3. Push to the connected repository
4. Platform will auto-deploy (if configured)
5. Or manually trigger a deployment

## Benefits of Shared Template Architecture

- **Consistency**: Same UI across all platforms and deployments
- **Maintainability**: Single source of truth for UI code
- **Flexibility**: Easy to customize for different contexts
- **Efficiency**: Reduced code duplication and maintenance overhead
- **Scalability**: Easy to add new deployment platforms

Choose the platform that best fits your needs in terms of ease of deployment, performance, and cost!