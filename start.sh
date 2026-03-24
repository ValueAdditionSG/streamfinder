#!/bin/bash
# Start Surgeon Intelligence Agent on port 8503
cd /home/admin/.openclaw/workspace/projects/surgeon-intel
export DASHSCOPE_API_KEY="sk-40e569790dcf47c1b8f16ed633531502"

/home/linuxbrew/.linuxbrew/bin/python3.11 -m streamlit run app.py \
  --server.port 8503 \
  --server.address 127.0.0.1 \
  --server.headless true \
  --browser.gatherUsageStats false \
  --theme.base dark \
  --theme.primaryColor "#00d4aa"
