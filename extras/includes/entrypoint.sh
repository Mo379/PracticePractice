#!/bin/sh
cd /var/www/html/
apache2ctl -D FOREGROUND
useradd -m -s /bin/bash celeryuser
python3 -m celery -A PP2 worker --uid=celeryuser -l info
