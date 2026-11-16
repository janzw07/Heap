from threading import Thread
from functools import wraps
import time

def threaded(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper

def retry(times=2, delay=1):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < times:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"ERROR in {func.__name__} : {e} . Attempts {attempts}/{times}")
                    if attempts >= times:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return deco
