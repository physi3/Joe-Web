#!/bin/bash
cd /home/joe/Web/Joe-Web
echo "Opening TMUX session"
/usr/bin/tmux new-session -d -s JoeWeb '/home/joe/Web/Joe-Web/Joe-Web/bin/python /home/joe/Web/Joe-Web/manage.py runserver 0.0.0.0:8000 --insecure'
