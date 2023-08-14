worker:
	cd app && celery -A tasks worker --loglevel=info

redis:
	docker run --rm --name redis -p 6379:6379 redis