import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_DIR = '/app/logs'
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name, log_file, level=logging.INFO):
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

request_logger = setup_logger('requests', os.path.join(LOG_DIR, 'requests.log'))
suspicious_logger = setup_logger('suspicious', os.path.join(LOG_DIR, 'suspicious.log'))
critical_logger = setup_logger('critical', os.path.join(LOG_DIR, 'critical.log'))

def log_request(prompt_length, response_length, tokens_used):
    request_logger.info(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'prompt_length': prompt_length,
        'response_length': response_length,
        'tokens_used': tokens_used
    }))

def log_suspicious(prompt_snippet, trigger_reason):
    suspicious_logger.warning(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'prompt_snippet': prompt_snippet[:200],
        'trigger_reason': trigger_reason
    }))

def log_critical(method_used, prompt_snippet):
    critical_logger.critical(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'method_used': method_used,
        'prompt_snippet': prompt_snippet[:200]
    }))
