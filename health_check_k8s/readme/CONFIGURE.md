## Kubernetes Configuration

Configure your deployment's probes to use these endpoints:

```yaml
startupProbe:
  httpGet:
    path: /health/ready
    port: 8069
  failureThreshold: 30
  periodSeconds: 5
  # Allows up to 2.5 minutes for container startup

livenessProbe:
  httpGet:
    path: /health/ready
    port: 8069
  periodSeconds: 15
  timeoutSeconds: 2
  failureThreshold: 3
  # ~45 seconds to restart a hung process

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8069
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
  # ~30 seconds to stop traffic to unhealthy pod
```

The startup probe handles container initialization, allowing tighter
liveness/readiness thresholds once the application is running. For major
upgrades, use a separate Job resource rather than relying on probe tolerance.

## Notes

- Access logs for `/health/*` endpoints are automatically suppressed to
  avoid log noise from frequent probe requests.
- Use the probe's `timeoutSeconds` setting to control how long checks can
  take before being considered failed.
