# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_bootstrapper_base import *  # noqa: F403,E402


def generate_readme(config: Dict[str, Any]) -> str:
    """Generate README.md content."""
    name = config.get("name", "my-project")
    desc = config.get("description", "A SaaS application")
    stack = config.get("stack", "nextjs")

    return f"""# {name}

{desc}

## Tech Stack

- **Framework**: {stack}
- **Database**: {config.get('database', 'PostgreSQL')}
- **Auth**: {config.get('auth', 'JWT')}

## Getting Started

### Prerequisites

- Node.js 18+ / Python 3.11+
- Docker & Docker Compose

### Development

```bash
# Clone the repo
git clone <repo-url>
cd {name}

# Copy environment variables
cp .env.example .env

# Start with Docker
docker compose up -d

# Or run locally
{'npm install && npm run dev' if stack in ('nextjs', 'express') else 'pip install -r requirements.txt && uvicorn app.main:app --reload'}
```

### Testing

```bash
{'npm test' if stack in ('nextjs', 'express') else 'pytest'}
```

## Project Structure

```
{name}/
├── {'src/' if stack in ('nextjs', 'express') else 'app/'}
├── tests/
├── docker-compose.yml
├── .env.example
└── README.md
```

## License

MIT
"""
def generate_env_example(config: Dict[str, Any]) -> str:
    """Generate .env.example file."""
    lines = [
        "# Application",
        f"APP_NAME={config.get('name', 'my-app')}",
        "NODE_ENV=development",
        "PORT=3000",
        "",
        "# Database",
    ]
    db = config.get("database", "postgresql")
    if db == "postgresql":
        lines.extend(["DATABASE_URL=postgresql://user:password@localhost:5432/mydb", ""])
    elif db == "mongodb":
        lines.extend(["MONGODB_URI=mongodb://localhost:27017/mydb", ""])
    elif db == "mysql":
        lines.extend(["DATABASE_URL=mysql://user:password@localhost:3306/mydb", ""])

    if config.get("auth"):
        lines.extend([
            "# Auth",
            "JWT_SECRET=change-me-in-production",
            "JWT_EXPIRY=7d",
            ""
        ])

    if config.get("features", {}).get("email"):
        lines.extend(["# Email", "SMTP_HOST=smtp.example.com", "SMTP_PORT=587", "SMTP_USER=", "SMTP_PASS=", ""])

    if config.get("features", {}).get("storage"):
        lines.extend(["# Storage", "S3_BUCKET=", "S3_REGION=us-east-1", "AWS_ACCESS_KEY_ID=", "AWS_SECRET_ACCESS_KEY=", ""])

    return "\n".join(lines)
def generate_db_service(db: str) -> str:
    if db == "postgresql":
        return """  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
"""
    elif db == "mongodb":
        return """  db:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db
"""
    return ""
def generate_redis_service(config: Dict[str, Any]) -> str:
    if config.get("features", {}).get("redis"):
        return """  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
"""
    return ""
