#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || echo "请先创建虚拟环境: python3 -m venv venv"
jupyter notebook --ip=127.0.0.1 --port=8888 --no-browser
