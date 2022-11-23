docker exec -i container_pp2 bash -c 'python3 manage.py dbrestore --noinput'
docker exec -i container_pp2 bash -c 'python3 manage.py djstripe_sync_models --noinput'
