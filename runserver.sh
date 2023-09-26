cd /home/pi/Web/Joe-Web
tmux new -A -s JoeWeb 'python3 manage.py runserver 0.0.0.0:8000 --insecure'
