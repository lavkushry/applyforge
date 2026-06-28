# ApplyForge Deployment Guidelines

This guide details the procedures and topologies for deploying the ApplyForge platform across different environments.

## Deployment Topologies

ApplyForge is architected to support containerized deployments, ensuring consistency between local development and production environments.

### 1. Single-Node Docker Compose (Current Default)
The repository currently includes a `docker-compose.yml` optimized for local development and rapid single-node staging deployments. This configuration orchestrates the following services:
- **API**: FastAPI application running via Uvicorn.
- **Web**: Next.js frontend application.
- **Worker**: Celery worker instance bundled with Playwright dependencies.
- **Database**: PostgreSQL relational database.
- **Message Broker**: Redis, serving both as the Celery broker and result backend.

### 2. Distributed Cloud Native (Future Target)
For high availability and scale, the target production architecture involves:
- **Compute**: Managed Kubernetes (EKS/GKE) or container instances (ECS/Cloud Run) hosting the API and Web services.
- **Database**: Managed PostgreSQL (e.g., Amazon RDS, Google Cloud SQL).
- **Cache & Broker**: Managed Redis (e.g., Amazon ElastiCache, Google Memorystore).
- **Storage**: S3-compatible object storage for resumes, PDFs, and Playwright diagnostic screenshots (currently constrained to local disk).

## Environment Configuration

Secure and correct environment variable configuration is critical for successful deployment.

### API Environment (`apps/api/.env`)
Required configurations include:
- `DATABASE_URL`: Connection string for the PostgreSQL database.
- `REDIS_URL`: Connection string for the Redis broker.
- `SECRET_KEY`: Cryptographically secure key used for session cookie signing.
- **Optional Integrations**: `OPENAI_API_KEY`, `GOOGLE_OAUTH_CLIENT_ID`, `MICROSOFT_OAUTH_CLIENT_ID`, etc.

### Web Environment (`apps/web/.env.local`)
Required configurations include:
- `NEXT_PUBLIC_API_URL`: The externally accessible URL of the FastAPI backend.

### Worker Environment (`apps/worker/.env`)
Required configurations include:
- `DATABASE_URL`: Must match the API database connection string.
- `REDIS_URL`: Must match the API broker connection string.

*Note: Avoid committing actual `.env` files to version control. Always use the provided `.env.example` templates as a starting point.*

## Pre-Deployment Verification

Before executing a deployment, ensure the following checks pass:

1. **Database Schema**: Verify that the PostgreSQL instance is accessible and that the `Base.metadata.create_all(...)` routine in `main.py` executes successfully (Note: Full Alembic migrations are pending finalization).
2. **Broker Connectivity**: Ensure both the API and Worker containers can successfully connect to the Redis instance.
3. **Playwright Binaries**: Confirm that the worker container image has successfully downloaded and installed the required Playwright browser binaries during the build phase.

## Deployment Execution (Docker Compose)

To deploy using the provided Docker Compose configuration:

1. Ensure all environment files (`.env`) are populated with production-appropriate values.
2. Build the Docker images:
   ```bash
   docker compose build
   ```
3. Start the services in detached mode:
   ```bash
   docker compose up -d
   ```
4. Monitor the initialization logs to ensure successful startup:
   ```bash
   docker compose logs -f
   ```

## Post-Deployment Smoke Tests

Following deployment, execute these manual verifications:

1. **Frontend Accessibility**: Navigate to the Web URL and verify the login screen renders.
2. **API Health**: Access the API documentation endpoint (`/docs`) to confirm the backend is responsive.
3. **Worker Registration**: Access the Flower dashboard (if configured) or check the worker logs to verify it has successfully connected to Redis and is listening for tasks.
4. **End-to-End Test**: Create a test user account, upload a sample resume, and verify that the parsing task is successfully queued to and processed by the worker.

## Known Deployment Limitations

- **Schema Evolution**: The system currently relies on SQLAlchemy's `create_all` at startup. A robust workflow utilizing Alembic for schema migrations is required for production data longevity.
- **Stateful File Storage**: Artifacts like generated PDFs and Playwright screenshots are currently written to local disk. Deployments requiring multiple API or Worker instances will encounter shared-state issues until an S3-compatible storage backend is implemented.
