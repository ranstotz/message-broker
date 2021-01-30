#!/bin/bash

echo -e "Starting docker-compose locally...\n"
docker-compose build --no-cache
docker-compose up -d
