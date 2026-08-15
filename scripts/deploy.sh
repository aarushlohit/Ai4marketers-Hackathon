#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERT_DIR="$ROOT_DIR/infrastructure/nginx/certs"

mkdir -p "$CERT_DIR"

if [[ ! -f "$CERT_DIR/fullchain.pem" ]]; then
  echo "Generating self-signed TLS certificate for local production..."
  openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
    -keyout "$CERT_DIR/privkey.pem" \
    -out "$CERT_DIR/fullchain.pem" \
    -subj "/CN=localhost/O=Miracle Birds/C=US"
fi

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo "Creating .env from .env.example..."
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

# Generate secure secrets if still using defaults
gen_secret() {
  openssl rand -hex 32
}

update_env() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" "$ROOT_DIR/.env"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$ROOT_DIR/.env"
  else
    echo "${key}=${value}" >> "$ROOT_DIR/.env"
  fi
}

if grep -q "change-me-in-production\|change-this-to-a-random" "$ROOT_DIR/.env"; then
  echo "Rotating insecure default secrets..."
  update_env "JWT_SECRET" "$(gen_secret)"
  update_env "SECRET_KEY" "$(gen_secret)"
  update_env "INTERNAL_API_KEY" "$(gen_secret)"
  update_env "WEBHOOK_SECRET" "$(gen_secret)"
  update_env "POSTGRES_PASSWORD" "$(gen_secret)"
  update_env "REDIS_PASSWORD" "$(gen_secret)"
  update_env "ENVIRONMENT" "production"
fi

echo "Building and starting production stack..."
cd "$ROOT_DIR"
docker compose -f docker-compose.prod.yml up --build -d

echo ""
echo "Production stack is running:"
echo "  Frontend/API (HTTPS): https://localhost"
echo "  Backend health:       https://localhost/health"
echo ""
echo "To view logs: docker compose -f docker-compose.prod.yml logs -f"
