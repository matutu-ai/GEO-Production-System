#!/usr/bin/env bash
set -euo pipefail

# Production setup for Ubuntu 22.04/24.04.
#
# Required variables:
#   DOMAIN         main site domain, default geo.example.com
#   API_DOMAIN     API domain, default api.geo.example.com
#   DEPLOY_DIR     deployment directory, default /opt/geo-production-system
#   REPO_URL       git clone URL, replace with the real repository
#
# Optional:
#   CERTBOT_EMAIL  email used by Let's Encrypt
#   SKIP_CERTBOT=1 skips HTTPS certificate issuance

DOMAIN="${DOMAIN:-geo.example.com}"
API_DOMAIN="${API_DOMAIN:-api.geo.example.com}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/geo-production-system}"
REPO_URL="${REPO_URL:-https://github.com/matutu-ai/GEO-Production-System.git}"

echo "==> Installing Docker, Nginx and Certbot"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sudo sh
fi
sudo apt-get update
sudo apt-get install -y docker-compose-plugin nginx certbot python3-certbot-nginx

echo "==> Preparing ${DEPLOY_DIR}"
if [ ! -d "${DEPLOY_DIR}/.git" ]; then
  sudo git clone "${REPO_URL}" "${DEPLOY_DIR}"
fi
cd "${DEPLOY_DIR}"

if [ ! -f .env ]; then
  sudo cp .env.example .env
  sudo sed -i "s|https://api.geo.example.com|https://${API_DOMAIN}|g" .env
  sudo sed -i "s|JWT_SECRET=geo-production-system-local-secret|JWT_SECRET=$(openssl rand -hex 32)|g" .env
fi

if [ ! -f frontend/.env.production ]; then
  sudo cp frontend/.env.production.example frontend/.env.production
  sudo sed -i "s|https://api.geo.example.com|https://${API_DOMAIN}|g" frontend/.env.production
fi

echo "==> Starting Docker services"
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

echo "==> Installing Host Nginx HTTP bootstrap"
sudo sed \
  -e "s|api.geo.example.com|${API_DOMAIN}|g" \
  -e "s|geo.example.com|${DOMAIN}|g" \
  deploy/nginx/geo.http.conf.example \
  | sudo tee /etc/nginx/sites-available/geo.conf >/dev/null
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sfn /etc/nginx/sites-available/geo.conf /etc/nginx/sites-enabled/geo.conf
sudo nginx -t
sudo systemctl reload nginx

echo "==> Backend health check"
curl -fsS http://127.0.0.1:8000/health
printf "\n"

if [ "${SKIP_CERTBOT:-0}" = "1" ]; then
  echo "SKIP_CERTBOT=1, run certbot manually after DNS is ready."
else
  if [ -z "${CERTBOT_EMAIL:-}" ]; then
    echo "CERTBOT_EMAIL is not set; run certbot manually:"
  else
    sudo certbot --nginx --non-interactive --agree-tos -m "${CERTBOT_EMAIL}" -d "${DOMAIN}"
    sudo certbot --nginx --non-interactive --agree-tos -m "${CERTBOT_EMAIL}" -d "${API_DOMAIN}"
    sudo systemctl reload nginx
  fi
  echo "sudo certbot --nginx -d ${DOMAIN}"
  echo "sudo certbot --nginx -d ${API_DOMAIN}"
fi

echo "==> Done"
echo "Frontend: https://${DOMAIN}"
echo "API: https://${API_DOMAIN}"
