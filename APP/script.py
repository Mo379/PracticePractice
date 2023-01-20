import redis
import numpy as np
r = redis.Redis(host='0.0.0.0', port=6379, db=0)
while True:
    value = r.get('mykey')
    print(np.fromstring(value, dtype=int))
    if value == b'Kill':
        break
