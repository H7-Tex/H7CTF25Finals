import re
import base64
from logger import log_suspicious, log_critical

INJECTION_KEYWORDS = [
    'ignore previous', 'disregard', 'system prompt', 'reveal flag',
    'forget your', 'new instructions', 'override', 'bypass security', 'master access code',
    'flag'
]

ROLEPLAY_PATTERNS = [
    'pretend', 'act as', 'simulate', 'roleplay', 'role play',
    'imagine you are', 'you are now', 'become', 'transform into'
]

def detect_base64(text):
    base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
    matches = re.findall(base64_pattern, text)
    
    for match in matches:
        try:
            decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
            if len(decoded) > 5:
                return True
        except:
            continue
    
    return False

def detect_hex_encoding(text):
    hex_patterns = [
        r'(?:\\x[0-9a-fA-F]{2}){5,}',  # \x41\x42...
        r'(?:0x[0-9a-fA-F]{2}\s*){5,}',  # 0x41 0x42...
        r'(?:[0-9a-fA-F]{2}\s){5,}',  # 41 42 43...
    ]
    
    for pattern in hex_patterns:
        if re.search(pattern, text):
            return True
    
    return False

def sanitize_input(prompt):
    prompt_lower = prompt.lower()
    
    for keyword in INJECTION_KEYWORDS:
        if keyword in prompt_lower:
            log_suspicious(prompt, f"Injection keyword detected: {keyword}")
            return False, f"Input contains restricted pattern: '{keyword}'"
    
    for pattern in ROLEPLAY_PATTERNS:
        if pattern in prompt_lower:
            log_suspicious(prompt, f"Role-play attempt detected: {pattern}")
            return False, f"Role-play attempts are not allowed"
    
    if detect_base64(prompt):
        log_suspicious(prompt, "Base64 encoding detected")
        return False, "Encoded content detected and blocked"
    
    if detect_hex_encoding(prompt):
        log_suspicious(prompt, "Hex encoding detected")
        return False, "Encoded content detected and blocked"
    
    return True, None

def filter_output(response, flag):
    flag_pattern = r'H7CTF\{[^}]+\}'
    
    if re.search(flag_pattern, response):
        log_critical("Exact flag pattern detected in response", response)
        response = re.sub(flag_pattern, '[REDACTED]', response)
    
    return response
