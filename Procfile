web: daphne -b 0.0.0.0 -p $PORT bongeats.asgi:application
worker: celery -A bongeats worker -P solo -E -l info  