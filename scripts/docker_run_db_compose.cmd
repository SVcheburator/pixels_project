@echo off

PUSHD ..
docker compose  --env-file .env --file docker-compose.yml  up -d 
POPD

   

