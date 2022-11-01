docker compose down 
cd APP_MatterMost
docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml down
cd ../
