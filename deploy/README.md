# Production Deployment

This deployment puts Host Nginx in front of the Docker services and terminates HTTPS with Certbot. Docker services only listen on loopback addresses, so port 80/443 on the server is owned by Host Nginx.

```text
User
  -> https://geo.example.com
     -> Host Nginx
        -> frontend container on 127.0.0.1:8080
  -> https://api.geo.example.com
     -> Host Nginx
        -> backend container on 127.0.0.1:8000
```

## Server Requirements

Ubuntu 22.04 or 24.04 with a public IP and DNS records:

```text
geo.example.com  -> server IP
api.geo.example.com -> server IP
```

## Automatic Setup

```bash
export DOMAIN=geo.example.com
export API_DOMAIN=api.geo.example.com
export CERTBOT_EMAIL=admin@example.com
export REPO_URL=https://github.com/your-org/GEO-Production-System.git
chmod +x deploy/server_setup.sh
./deploy/server_setup.sh
```

The script installs Docker, Compose, Nginx and Certbot, clones the repository, builds the containers, installs the Host Nginx config and requests certificates.

## Manual Setup

1. Install dependencies:

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo apt-get update
sudo apt-get install -y docker-compose-plugin nginx certbot python3-certbot-nginx
```

2. Clone and configure:

```bash
sudo mkdir -p /opt/geo-production-system
sudo git clone <repository-url> /opt/geo-production-system
cd /opt/geo-production-system
sudo cp .env.example .env
sudo cp frontend/.env.production.example frontend/.env.production
```

Update `.env`:

```bash
API_BASE_URL=https://api.geo.example.com
OPENAI_API_KEY=your-key
MODEL_NAME=gpt-4o-mini
JWT_SECRET=replace-with-a-long-random-secret
```

3. Start production services:

```bash
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
curl http://127.0.0.1:8000/health
```

Expected health response:

```json
{"status":"running","service":"geo-production-system","version":"2.2.0"}
```

4. Install the HTTP bootstrap config first. This allows Nginx to start before certificates exist; Certbot will add the HTTPS server blocks:

```bash
sudo cp deploy/nginx/geo.http.conf.example /etc/nginx/sites-available/geo.conf
sudo ln -sfn /etc/nginx/sites-available/geo.conf /etc/nginx/sites-enabled/geo.conf
sudo nginx -t
sudo systemctl reload nginx
```

5. Issue HTTPS certificates:

```bash
sudo certbot --nginx -d geo.example.com
sudo certbot --nginx -d api.geo.example.com
sudo systemctl reload nginx
```

The final HTTPS-only reference config is [geo.conf.example](nginx/geo.conf.example). Use it after certificates are issued only if you prefer to manage Nginx without the Certbot-generated config.

## Validation

```bash
curl -I https://geo.example.com
curl https://api.geo.example.com/health
curl -I https://api.geo.example.com
```

Then create a project in the web console, upload `backend/input/demo_customer.xlsx`, run the GEO pipeline and download reports.

## Production Security

- Host Nginx enforces HTTP -> HTTPS redirects, TLS 1.2+, HSTS and common security headers.
- Upload size is limited to `50m` in both Host Nginx and the frontend container.
- Backend container does not use `--reload` and `APP_ENV` is `production`.
- API keys and JWT secrets are kept in `.env`, which is not committed.
