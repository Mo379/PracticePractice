docker-compose up -d 
cd APP_MatterMost
docker-compose -f docker-compose.yml -f docker-compose.without-nginx.yml up -d
cd ../
