#!/bin/bash
docker-compose build
docker-compose run bot python manage.py create faq4
docker-compose run bot python manage.py add faq4 data/faq4.txt
docker-compose run bot python manage.py create faq
docker-compose run bot python manage.py add faq data/FAQ.txt
docker-compose up 
