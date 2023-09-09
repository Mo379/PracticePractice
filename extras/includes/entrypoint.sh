#!/bin/bash
cd /var/www/html/
useradd -m -s /bin/bash celeryuser
python3 -m celery -A PP2 worker --uid=celeryuser -l info &
apache2ctl -D FOREGROUND
