sleep 1
curl -XDELETE http://$ES_HOST:9200/faqs
curl -XPUT http://$ES_HOST:9200/faqs
curl -XPOST http://$ES_HOST:9200/faqs/faq/_mapping -d'{"faq": {"_all": {"analyzer": "russian_morphology"}}}'
python parse.py
