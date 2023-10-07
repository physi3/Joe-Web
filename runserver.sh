#!/bin/bash
cd /home/pi/Web/Joe-Web
echo "Opening TMUX session"
/usr/bin/tmux new-session -d -s JoeWeb '/home/pi/Downloads/Python-3.9.6/python /home/pi/Web/Joe-Web/manage.py runserver 0.0.0.0:8000 --insecure'
