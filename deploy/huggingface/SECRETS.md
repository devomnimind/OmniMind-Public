# Secrets Configuration for Hugging Face Space

## Required Secrets

Configure the following secrets in your Hugging Face Space settings at:
https://huggingface.co/spaces/fabricioslv/omnimind-tests/settings

### Core Authentication
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `HUGGING_FACE_HUB_TOKEN` | Hugging Face API token | `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `GITHUB_TOKEN` | GitHub API token | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

### External Services (Optional but Recommended)
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `IBM_API_KEY` | IBM Quantum API key | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `IBM_CRN` | IBM Cloud Resource Name | `crn:v1:bluemix:public:quantum-computing:...` |

### Database Services (Optional)
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `OMNIMIND_SUPABASE_URL` | Supabase URL | `https://xxxxxxxxxxxxxxxx.supabase.co` |
| `OMNIMIND_SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `OMNIMIND_SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `OMNIMIND_QDRANT_API_KEY` | Qdrant API key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### Application Settings
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `HF_SPACE_URL` | Hugging Face Space URL | `https://username-space.hf.space` |
| `OMNIMIND_INTERACTIVE` | Interactive mode flag | `true` |

## Priority Setup

### Minimum Required (for basic test execution):
- `HUGGING_FACE_HUB_TOKEN`
- `GITHUB_TOKEN`

### Recommended (for full test coverage):
- All Core Authentication secrets
- OPENROUTER_API_KEY (for AI model tests)
- GEMINI_API_KEY (for Google AI tests)

### Optional (for integration tests):
- IBM credentials (quantum computing tests)
- Supabase credentials (database tests)
- Qdrant credentials (vector database tests)

## How to Configure

1. Go to your Space settings
2. Navigate to the "Secrets" tab
3. Add each secret with its corresponding value
4. Save and restart the Space

## Security Notes

- Never commit actual secret values to the repository
- Use masked/placeholder values in documentation
- Rotate keys regularly
- Monitor Space logs for any exposed credentials

## Environment Variables vs Secrets

The Space uses secrets (configured in UI) rather than environment variables from the repository for security. This prevents accidental exposure of sensitive credentials in the git history.