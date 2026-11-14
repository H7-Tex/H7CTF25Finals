from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from config import Config
from rate_limiter import check_global_rate_limit
from defenses import sanitize_input, filter_output
from groq_client import get_ai_response
from logger import log_request, log_suspicious

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'AI Guardian Challenge'
    }), 200

@app.route('/api/challenge', methods=['POST'])
def challenge():
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'error': 'Missing required field: prompt',
                'success': False
            }), 400
        
        user_prompt = data['prompt']
        
        if not isinstance(user_prompt, str):
            return jsonify({
                'error': 'Prompt must be a string',
                'success': False
            }), 400
        
        allowed, retry_after = check_global_rate_limit(Config.RATE_LIMIT_SECONDS)
        if not allowed:
            return jsonify({
                'error': f'Rate limit exceeded. Please wait {Config.RATE_LIMIT_SECONDS} seconds between requests.',
                'retry_after': retry_after,
                'success': False
            }), 429
        
        if len(user_prompt) > Config.MAX_INPUT_LENGTH:
            return jsonify({
                'error': f'Input exceeds maximum length of {Config.MAX_INPUT_LENGTH} characters.',
                'success': False
            }), 400
        
        is_safe, reason = sanitize_input(user_prompt)
        if not is_safe:
            return jsonify({
                'error': f'Input rejected: {reason}',
                'success': False
            }), 400
        
        try:
            ai_response, tokens_used = get_ai_response(user_prompt)
        except Exception as e:
            return jsonify({
                'error': 'AI service temporarily unavailable',
                'success': False
            }), 503
        
        filtered_response = filter_output(ai_response, Config.SECRET_FLAG)
        
        log_request(len(user_prompt), len(filtered_response), tokens_used)
        
        return jsonify({
            'response': filtered_response,
            'success': True,
            'tokens_used': tokens_used
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'success': False
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500

if __name__ == '__main__':
    os.makedirs('/app/logs', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
