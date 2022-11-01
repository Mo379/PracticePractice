docker compose up -d 
mkdir -p extras/data/MM/volumes/app/mattermost/{config,data,logs,plugins,client/plugins,bleve-indexes}
sudo chown -R 2000:2000 extras/data/MM/volumes/app/mattermost
cd APP_MatterMost
docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up -d
cd ../
