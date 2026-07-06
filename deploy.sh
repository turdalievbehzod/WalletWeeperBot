#!/usr/bin/env bash
# =============================================================================
#  deploy.sh — Production deployment for Daily Expenses TMA
#  Subdomains:
#    walletweeper.yasheritsa.com      → frontend  (localhost:3000)
#    api.walletweeper.yasheritsa.com  → Django API (localhost:8000)
#
#  Usage:
#    sudo bash deploy.sh          — full first-time setup (nginx + SSL)
#    sudo bash deploy.sh --no-ssl — skip certbot (useful before DNS propagates)
#    sudo bash deploy.sh --reload — only reload nginx config (no re-install)
# =============================================================================
set -euo pipefail

# ─── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "${GREEN}  ✓${NC}  $*"; }
info() { echo -e "${BLUE}  →${NC}  $*"; }
warn() { echo -e "${YELLOW}  !${NC}  $*"; }
step() { echo -e "\n${BOLD}${BLUE}══ $* ══${NC}"; }
die()  { echo -e "\n${RED}  ✗  ERROR: $*${NC}\n" >&2; exit 1; }

# ─── Config ────────────────────────────────────────────────────────────────────
DOMAIN_FRONT="walletweeper.yasheritsa.com"
DOMAIN_API="api.walletweeper.yasheritsa.com"
EMAIL="turdalievbehzod58@gmail.com"
NGINX_CONF="/etc/nginx/sites-available/daily-expenses"
NGINX_LINK="/etc/nginx/sites-enabled/daily-expenses"

# ─── Argument parsing ──────────────────────────────────────────────────────────
SKIP_SSL=false
RELOAD_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --no-ssl)    SKIP_SSL=true ;;
    --reload)    RELOAD_ONLY=true ;;
    --help|-h)
      echo "Usage: sudo bash deploy.sh [--no-ssl] [--reload]"
      exit 0 ;;
  esac
done

# ─── Root guard ────────────────────────────────────────────────────────────────
[[ $EUID -ne 0 ]] && die "Run as root: sudo bash deploy.sh"

# ─── Quick reload path (skip install) ─────────────────────────────────────────
if [[ "$RELOAD_ONLY" == true ]]; then
  step "Reloading nginx config only"
  nginx -t && systemctl reload nginx
  ok "Nginx reloaded"
  exit 0
fi

# ══════════════════════════════════════════════════════════════════════════════
step "1 / 5  Updating system packages"
# ══════════════════════════════════════════════════════════════════════════════
apt-get update -qq
apt-get upgrade -y -qq
ok "Packages updated"

# ══════════════════════════════════════════════════════════════════════════════
step "2 / 5  Installing nginx & certbot"
# ══════════════════════════════════════════════════════════════════════════════
apt-get install -y -qq nginx certbot python3-certbot-nginx
systemctl enable nginx
systemctl start  nginx
ok "nginx $(nginx -v 2>&1 | grep -o '[0-9.]*$') installed and running"
ok "certbot $(certbot --version 2>&1 | grep -o '[0-9.]*') installed"

# ══════════════════════════════════════════════════════════════════════════════
step "3 / 5  Writing nginx config"
# ══════════════════════════════════════════════════════════════════════════════

# Remove default site if still present
[[ -f /etc/nginx/sites-enabled/default ]] && rm /etc/nginx/sites-enabled/default && warn "Removed default site"

cat > "$NGINX_CONF" << 'NGINX_EOF'
# ─── Rate limiting zones ───────────────────────────────────────────────────────
limit_req_zone  $binary_remote_addr  zone=api_limit:10m   rate=60r/m;
limit_req_zone  $binary_remote_addr  zone=auth_limit:10m  rate=10r/m;

# ─── Upstream definitions ──────────────────────────────────────────────────────
upstream django_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream frontend_app {
    server 127.0.0.1:3000;
    keepalive 16;
}

# ─────────────────────────────────────────────────────────────────────────────
#  Frontend  →  walletweeper.yasheritsa.com
# ─────────────────────────────────────────────────────────────────────────────
server {
    listen 80;
    server_name walletweeper.yasheritsa.com;

    # Security headers
    add_header X-Frame-Options        "SAMEORIGIN"   always;
    add_header X-Content-Type-Options "nosniff"      always;
    add_header Referrer-Policy        "strict-origin" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;
    gzip_min_length 1024;

    location / {
        proxy_pass         http://frontend_app;
        proxy_http_version 1.1;

        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (needed for Vite HMR / live-server)
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 60s;
        proxy_connect_timeout 10s;
    }

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}

# ─────────────────────────────────────────────────────────────────────────────
#  Django API  →  api.walletweeper.yasheritsa.com
# ─────────────────────────────────────────────────────────────────────────────
server {
    listen 80;
    server_name api.walletweeper.yasheritsa.com;

    # Security headers
    add_header X-Frame-Options        "DENY"        always;
    add_header X-Content-Type-Options "nosniff"     always;
    add_header Referrer-Policy        "no-referrer" always;

    # Max upload (avatar / receipt images)
    client_max_body_size 10m;

    location / {
        # Rate limit: 60 req/min general, burst of 20
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass         http://django_backend;
        proxy_http_version 1.1;

        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection        "";   # keepalive to upstream

        proxy_read_timeout    90s;
        proxy_connect_timeout 10s;
        proxy_send_timeout    90s;
    }

    # Stricter rate limit on auth endpoint
    location /api/v1/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;

        proxy_pass         http://django_backend;
        proxy_http_version 1.1;

        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django admin — allow only from localhost for safety
    location /admin/ {
        allow 127.0.0.1;
        deny  all;

        proxy_pass         http://django_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
NGINX_EOF

ok "Config written to $NGINX_CONF"

# ══════════════════════════════════════════════════════════════════════════════
step "4 / 5  Enabling config & reloading nginx"
# ══════════════════════════════════════════════════════════════════════════════

# Symlink to sites-enabled (idempotent)
[[ -L "$NGINX_LINK" ]] && rm "$NGINX_LINK"
ln -s "$NGINX_CONF" "$NGINX_LINK"
ok "Symlink created: sites-enabled/daily-expenses"

# Validate and reload
nginx -t
systemctl reload nginx
ok "nginx reloaded successfully"

# ══════════════════════════════════════════════════════════════════════════════
step "5 / 5  Obtaining SSL certificates via Certbot"
# ══════════════════════════════════════════════════════════════════════════════

if [[ "$SKIP_SSL" == true ]]; then
    warn "Skipping SSL (--no-ssl). Run without the flag after DNS propagates."
else
    info "Requesting certificate for $DOMAIN_FRONT and $DOMAIN_API ..."

    certbot --nginx \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --redirect \
        -d "$DOMAIN_FRONT" \
        -d "$DOMAIN_API"

    ok "SSL certificates issued and nginx auto-configured for HTTPS"

    # Verify auto-renewal works
    certbot renew --dry-run --quiet
    ok "Auto-renewal dry-run passed"
fi

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}  Deployment complete!${NC}"
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Frontend  →  https://${DOMAIN_FRONT}"
echo -e "  API       →  https://${DOMAIN_API}/api/v1/"
echo ""
echo -e "  ${YELLOW}Make sure your services are running:${NC}"
echo -e "  ${BLUE}  docker compose up -d          ${NC}# backend + db + redis"
echo -e "  ${BLUE}  cd frontend && npm run build  ${NC}# build the React app"
echo -e "  ${BLUE}  npx serve -s dist -p 3000     ${NC}# serve built frontend"
echo -e "  ${BLUE}  cd bot && python main.py       ${NC}# start Telegram bot"
echo ""
