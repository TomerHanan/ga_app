# Kubernetes Helm Chart Setup

This Helm chart deploys a FastAPI application with a PostgreSQL database on Kubernetes.

## Architecture

### Components

1. **FastAPI Application Deployment**
   - Container: `ga-app:latest`
   - Port: 8000
   - Connects to PostgreSQL using environment variables
   - Includes health checks on `/health` endpoint

2. **PostgreSQL Deployment**
   - Container: `postgres:15-alpine`
   - Port: 5432
   - Storage: EmptyDir (temporary, data lost on pod restart)
   - Authentication: Username/password from values.yaml

3. **Services**
   - `my-app`: Exposes the FastAPI application (ClusterIP, port 8000)
   - `my-app-postgresql`: Exposes PostgreSQL internally (ClusterIP, port 5432)

4. **Secrets**
   - `my-app-postgresql-secret`: Stores PostgreSQL password

## Configuration

### values.yaml

Key configuration values:

```yaml
# Application image
image:
  repository: ga-app
  tag: latest
  pullPolicy: IfNotPresent

# Application service
service:
  type: ClusterIP
  port: 8000

# PostgreSQL configuration
postgresql:
  enabled: true
  auth:
    username: postgres
    password: postgres
    database: postgres
  service:
    type: ClusterIP
    port: 5432
```

## Environment Variables

The FastAPI application receives the following environment variables:

- `POSTGRES_HOST`: PostgreSQL service hostname (my-app-postgresql)
- `POSTGRES_DB`: Database name (from postgresql.auth.database)
- `POSTGRES_USER`: Database username (from postgresql.auth.username)
- `POSTGRES_PASSWORD`: Database password (from secret)

## Deployment

### Deploy the chart

```bash
helm install my-release ./my-app
```

### Verify deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# View logs
kubectl logs -l app.kubernetes.io/name=my-app
kubectl logs -l app=my-app-postgresql
```

### Port forwarding for testing

```bash
# Access FastAPI app
kubectl port-forward svc/my-app 8000:8000

# Access PostgreSQL
kubectl port-forward svc/my-app-postgresql 5432:5432
```

## API Endpoints

Once deployed, the FastAPI application provides:

- `GET /health` - Health check
- `POST /write` - Create a log entry
  ```json
  {"message": "Your message"}
  ```
- `GET /logs` - Get latest logs (default limit: 10)
- `GET /logs/{id}` - Get specific log by ID

## File Structure

```
my-app/
├── Chart.yaml                          # Chart metadata
├── values.yaml                         # Default configuration
├── templates/
│   ├── _helpers.tpl                   # Helm helper functions
│   ├── deployment.yaml                # FastAPI deployment
│   ├── service.yaml                   # FastAPI service
│   ├── postgresql-deployment.yaml     # PostgreSQL deployment
│   ├── postgresql-service.yaml        # PostgreSQL service
│   └── postgresql-secret.yaml         # PostgreSQL secret
```

## Storage

PostgreSQL uses **EmptyDir** for storage, which means:
- Data is temporary and lost when the pod is deleted
- Suitable for development and testing
- For production, change to PersistentVolumeClaim in postgresql-deployment.yaml

### To use PersistentVolume:

1. Update `postgresql-deployment.yaml`:
```yaml
volumes:
- name: postgresql-storage
  persistentVolumeClaim:
    claimName: {{ include "my-app.fullname" . }}-postgresql-pvc
```

2. Create a PersistentVolumeClaim template if needed

## Customization

To customize the deployment:

1. **Change image**: Update `image.repository` and `image.tag` in values.yaml
2. **Change replica count**: Update `replicaCount` in values.yaml
3. **Change PostgreSQL version**: Update postgres image version in postgresql-deployment.yaml
4. **Add resource limits**: Update `resources` section in values.yaml

## Notes

- The application automatically creates the `logs` table on startup
- Environment variables are passed directly to the container
- PostgreSQL credentials are managed via Kubernetes Secrets
- The chart uses Helm's templating for dynamic values
