docker compose up -d 
mkdir -p extras/data/MM/volumes/app/mattermost/{config,data,logs,plugins,client/plugins,bleve-indexes}
sudo chown -R 2000:2000 extras/data/MM/volumes/app/mattermost
sudo chown -R 2000:2000 extras/includes/MM_config
#sudo chmod 755 -r # at the data direcotyr
#sudo chown :www-data # at the data direcotyr
cd APP_MatterMost
docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up -d
cd ../
