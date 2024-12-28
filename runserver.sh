#!/bin/bash
cd /var/www/Joe-Web
echo "Opening TMUX session"
/usr/bin/tmux new-session -d -s JoeWeb 'venv/bin/python -m gunicorn -c config/gunicorn/dev.py'
