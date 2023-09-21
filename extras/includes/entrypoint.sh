#!/bin/bash
apache2ctl -D FOREGROUND
cd /var/www/html
python3 manage.py collectstatic --noinput
