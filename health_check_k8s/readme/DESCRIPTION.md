This module provides enhanced health check endpoints for Odoo deployments in
Kubernetes environments.

Unlike Odoo's built-in `/web/health` endpoint which only verifies the web
server is running, this module performs actual connectivity checks to ensure
the application can serve requests properly.

## Endpoint

**`/health/ready`** - Kubernetes readiness probe. Returns:
- **HTTP 200** with JSON body when all checks pass
- **HTTP 503** with JSON body when any check fails

Checks performed:
- Database connection is active (executes `SELECT 1`)
- Filestore is accessible (opens a file for writing)

The JSON response includes diagnostic details:
```json
{
  "status": "healthy",
  "database": {"ok": true, "time_ms": 1.2},
  "filestore": {"ok": true}
}
```

Use this for both liveness and readiness probes, or just readiness if you
prefer a simpler liveness check.

## Use Case

When a PostgreSQL primary fails over to a replica, existing Odoo workers may
retain stale connections that appear valid but fail on actual queries. The
standard `/web/health` endpoint continues returning 200 OK while the
application logs connection errors. This module's readiness probe will fail
in this scenario, allowing Kubernetes to restart the pod or stop routing
traffic to it.
