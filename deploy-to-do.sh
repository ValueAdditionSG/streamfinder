#!/bin/bash
# ============================================================
# Surgeon Intelligence Agent — Deploy Script for DigitalOcean
# ============================================================
set -e

APP_DIR="/opt/surgeon-intel"
PORT=8503
DASHSCOPE_KEY="sk-40e569790dcf47c1b8f16ed633531502"
GITHUB_RAW="https://raw.githubusercontent.com/ValueAdditionSG/streamfinder/surgeon-intel"

echo ""
echo "=== Step 1: Installing Python packages ==="
apt-get update -q
apt-get install -y python3-pip python3-venv git
python3 -m venv /opt/surgeon-intel-venv
/opt/surgeon-intel-venv/bin/pip install streamlit requests openai --quiet
echo "✓ Packages installed"

echo ""
echo "=== Step 2: Downloading app files from GitHub ==="
mkdir -p $APP_DIR/fetchers

FILES="app.py synthesizer.py fetchers/__init__.py fetchers/pubmed.py fetchers/clinical_trials.py fetchers/npi_registry.py fetchers/open_payments.py fetchers/web_search.py"

for f in $FILES; do
    curl -s "$GITHUB_RAW/$f" -o "$APP_DIR/$f"
    echo "  ✓ $f"
done

echo ""
echo "=== Step 3: Setting up systemd service ==="
cat > /etc/systemd/system/surgeon-intel.service << SVCEOF
[Unit]
Description=Surgeon Intelligence Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
Environment="DASHSCOPE_API_KEY=$DASHSCOPE_KEY"
ExecStart=/opt/surgeon-intel-venv/bin/python -m streamlit run app.py --server.port $PORT --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --theme.base dark --theme.primaryColor "#00d4aa" --server.baseUrlPath "/surgeon-intel"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable surgeon-intel
systemctl restart surgeon-intel
sleep 5

if systemctl is-active --quiet surgeon-intel; then
    echo "✓ Service running on port $PORT"
else
    echo "✗ Service failed — checking logs:"
    journalctl -u surgeon-intel -n 20 --no-pager
    exit 1
fi

echo ""
echo "=== Step 4: Adding nginx route ==="
NGINX_CONF=$(grep -rl "workshop.medtechstrategizer.com" /etc/nginx/ 2>/dev/null | grep -v ".bak" | head -1)
echo "  Using nginx config: $NGINX_CONF"

# Only add if not already there
if ! grep -q "surgeon-intel" "$NGINX_CONF"; then
    sed -i "s|        location / {|    location /surgeon-intel/ {\n        proxy_pass http://127.0.0.1:$PORT;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade \$http_upgrade;\n        proxy_set_header Connection \"upgrade\";\n        proxy_set_header Host \$host;\n        proxy_set_header X-Real-IP \$remote_addr;\n        proxy_cache_bypass \$http_upgrade;\n        proxy_buffering off;\n        proxy_read_timeout 300s;\n    }\n\n        location / {|1" "$NGINX_CONF"
    echo "  ✓ nginx route added"
else
    echo "  ✓ nginx route already exists"
fi

nginx -t && systemctl reload nginx
echo "  ✓ nginx reloaded"

echo ""
echo "======================================================"
echo "  ✅  DEPLOYMENT COMPLETE!"
echo "======================================================"
echo ""
echo "  🔗  https://workshop.medtechstrategizer.com/surgeon-intel/"
echo ""
echo "  Test: curl -s http://127.0.0.1:$PORT/surgeon-intel/ -o /dev/null -w 'HTTP %{http_code}'"
echo ""
