import time

last_request_time = None

def check_global_rate_limit(rate_limit_seconds=60):
    global last_request_time
    
    current_time = time.time()
    
    if last_request_time is not None:
        time_since_last = current_time - last_request_time
        
        if time_since_last < rate_limit_seconds:
            retry_after = int(rate_limit_seconds - time_since_last)
            return False, retry_after
    
    last_request_time = current_time
    return True, 0

def reset_rate_limit():
    global last_request_time
    last_request_time = None
