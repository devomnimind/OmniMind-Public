# Environment Configuration Guide

This document outlines the secrets and environment variables required to configure the `staging` and `production` environments for OmniMind's CI/CD pipelines.

## 1. GitHub Repository Secrets

These secrets should be added in **Settings > Secrets and variables > Actions > New repository secret**. They are available globally to all workflows.

| Secret Name | Description | Required By |
| :--- | :--- | :--- |
| `CODECOV_TOKEN` | Token from Codecov.io for uploading coverage reports. | `ci.yml` |
| `HUGGING_FACE_HUB_TOKEN` | Token for downloading/uploading models to Hugging Face. | Application Runtime |

> **Note:** `GITHUB_TOKEN` is automatically provided by GitHub and does not need to be configured.

## 2. GitHub Environment Secrets

These secrets should be added in **Settings > Environments > [staging/production] > Add secret**. They are specific to deployments.

### Common Secrets (Staging & Production)

| Secret Name | Description |
| :--- | :--- |
| `OMNIMIND_QDRANT_URL` | URL for the Qdrant vector database. |
| `OMNIMIND_QDRANT_API_KEY` | API Key for Qdrant authentication. |
| `OMNIMIND_SUPABASE_URL` | URL for the Supabase instance. |
| `OMNIMIND_SUPABASE_ANON_KEY` | Anonymous key for Supabase client. |
| `OMNIMIND_SUPABASE_SERVICE_ROLE_KEY` | Service role key for Supabase admin tasks. |
| `OMNIMIND_DASHBOARD_USER` | Username for the web dashboard (default: `dashboard`). |
| `OMNIMIND_DASHBOARD_PASS` | Password for the web dashboard. |
| `JWT_SECRET` | **Critical:** Secure random string for signing JWT tokens. |

### Deployment Specifics (Examples)

Depending on your deployment target (Kubernetes, SSH, AWS, etc.), you will need additional secrets in the `deploy-staging` and `deploy-production` jobs.

| Secret Name | Description |
| :--- | :--- |
| `KUBE_CONFIG` | Base64 encoded Kubernetes config (if deploying to K8s). |
| `SSH_PRIVATE_KEY` | SSH Key for remote server access (if deploying via SSH). |
| `SSH_HOST` | IP address or hostname of the target server. |

## 3. Application Environment Variables

These variables are referenced in `config/omnimind.yaml` and must be injected into the Docker container or Kubernetes pod at runtime.

```bash
# Database
OMNIMIND_QDRANT_URL=...
OMNIMIND_QDRANT_API_KEY=...
OMNIMIND_QDRANT_COLLECTION=omnimind_prod

# Supabase
OMNIMIND_SUPABASE_URL=...
OMNIMIND_SUPABASE_ANON_KEY=...
OMNIMIND_SUPABASE_SERVICE_ROLE_KEY=...
OMNIMIND_SUPABASE_PROJECT=...

# Auth
OMNIMIND_DASHBOARD_USER=admin
OMNIMIND_DASHBOARD_PASS=secure_password_here

# AI
HUGGING_FACE_HUB_TOKEN=hf_...
```

## 4. PyPI Publishing (Release Workflow)

The `release.yml` workflow uses **Trusted Publishing (OIDC)** by default.

1.  Go to [PyPI.org](https://pypi.org/manage/account/publishing/).
2.  Add a new publisher.
3.  Owner: `[Your GitHub Username]`
4.  Repository: `omnimind`
5.  Workflow name: `release.yml`
6.  Environment: `release` (or leave blank for all).

*If you prefer using a token instead of OIDC, add `PYPI_API_TOKEN` to Repository Secrets and update `release.yml`.*

## 5. Automação (Opcional)

Se você já tem arquivos `.env` locais e quer enviá-los automaticamente para o GitHub sem digitar um por um, use o script incluído:

1.  Certifique-se de ter o [GitHub CLI](https://cli.github.com/) instalado e autenticado (`gh auth login`).
2.  Execute o script para cada ambiente:

```bash
# Para segredos globais (se houver algum no .env)
./scripts/upload_secrets.sh .env

# Para ambiente de Staging
./scripts/upload_secrets.sh .env.staging staging

# Para ambiente de Production
./scripts/upload_secrets.sh .env.production production
```

**Atenção:** Nunca commite seus arquivos `.env` no Git!
