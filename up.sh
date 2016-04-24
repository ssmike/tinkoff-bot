#!/bin/bash
docker-compose build
docker-compose run bot python manage.py create faq4
docker-compose run bot python manage.py add faq4 data/faq4.txt
docker-compose up 
