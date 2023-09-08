#!/bin/sh
apache2ctl -D FOREGROUND
python3 -m celery -A PP2 worker -l info -D
