docker compose restart
cd APP_MatterMost
docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml restart
cd ../
