import redis

r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # Should print True if the connection is successful
