# Docker Security Best Practices for Moltbot Helpers

## Secure Docker Configuration

### 1. Non-Root User Execution
Always run containers as non-root users to limit potential damage from vulnerabilities:

```dockerfile
RUN groupadd -r moltbot && useradd -r -g moltbot -m -s /bin/bash moltbot
USER moltbot
```

### 2. Minimal Attack Surface
- Use minimal base images (python:3.12-slim)
- Install only necessary dependencies
- Remove unnecessary packages after installation
- Use multi-stage builds when possible

### 3. Secure Volume Mounts
- Mount only necessary volumes
- Use read-only mounts where possible
- Ensure host directories have proper permissions
- Avoid mounting sensitive host directories unnecessarily

### 4. Runtime Security
- Run containers with minimal privileges
- Use read-only root filesystem when possible
- Limit resource usage to prevent DoS
- Disable privileged mode unless absolutely necessary

## Docker Run Best Practices

### Secure Execution
```bash
# Recommended: Run with user namespace remapping
docker run --user 1000:1000 --read-only --tmpfs /tmp ...

# For moltbot-helpers, use externalized data sources:
docker run --rm \
  -v /path/to/data:/data/_openclaw \
  -v /path/to/workspace:/workspace \
  moltbot-helpers-quick pt list
```

### Environment Variables
- Pass sensitive data via mounted files rather than environment variables when possible
- Use Docker secrets for sensitive data in swarm mode
- Avoid logging sensitive information

## Image Security

### Building Secure Images
- Use official base images from trusted sources
- Keep base images updated
- Scan images for vulnerabilities
- Minimize the number of layers

### Image Signing and Verification
- Sign images with Docker Content Trust
- Verify image signatures before running
- Use specific image tags rather than 'latest'

## Container Runtime Security

### Network Security
- Use custom networks instead of default bridge
- Limit inter-container communication
- Use network policies where available
- Avoid using host networking unless necessary

### File System Security
- Use volume mounts for persistent data
- Ensure proper file permissions on mounted volumes
- Use tmpfs for temporary data that doesn't need to persist
- Regularly audit file access patterns

## Security Tools and Scanning

### Image Scanning
Regularly scan images using tools like:
- Trivy
- Clair
- Docker Scout
- Anchore

### Runtime Monitoring
- Monitor container logs for suspicious activity
- Track resource usage for anomalies
- Log all access to sensitive data
- Alert on unexpected network connections

## Incident Response

If a security vulnerability is discovered in the Docker setup:
1. Immediately stop affected containers
2. Investigate the scope of the issue
3. Update the Dockerfile to address the vulnerability
4. Rebuild and test the images
5. Deploy the updated images
6. Audit all affected systems