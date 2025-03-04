import os
import ast
from apiflask import APIFlask
from flask_httpauth import HTTPTokenAuth
from dotenv import load_dotenv
from flask import request, jsonify
import json

# Set how this API should be titled and the current version
API_TITLE='Events API for Watson Assistant'
API_VERSION='1.0.1'

# create the app
app = APIFlask(__name__, title=API_TITLE, version=API_VERSION)

# load .env if present
load_dotenv()
# Next, define the auth variable
auth = HTTPTokenAuth(scheme='ApiKey', header='API_TOKEN')

# the secret API key, plus we need a username in that record
API_TOKEN = os.getenv('API_TOKEN', 'MY_SECRETKEY')  
tokens = {API_TOKEN: 'appuser'}

# Add this verification callback function
@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]
    return None

# specify a generic SERVERS scheme for OpenAPI to allow both local testing
# and deployment on Code Engine with configuration within Watson Assistant
app.config['SERVERS'] = [
    {
        'description': 'Code Engine deployment',
        'url': 'https://{appname}.{projectid}.{region}.codeengine.appdomain.cloud',
        'variables':
        {
            "appname":
            {
                "default": "myapp",
                "description": "application name"
            },
            "projectid":
            {
                "default": "projectid",
                "description": "the Code Engine project ID"
            },
            "region":
            {
                "default": "us-south",
                "description": "the deployment region, e.g., us-south"
            }
        }
    },
    {
        'description': 'local test',
        'url': 'http://127.0.0.1:{port}',
        'variables':
        {
            'port':
            {
                'default': "5000",
                'description': 'local port to use'
            }
        }
    }
]


# set how we want the authentication API key to be passed
auth=HTTPTokenAuth(scheme='ApiKey', header='API_TOKEN')

# default "homepage", also needed for health check by Code Engine
@app.get('/')
def print_default():
    """ Greeting
    health check
    """
    # returning a dict equals to use jsonify()
    return {'message': 'This is the certifications API server'}


@app.post('/format-text')
@app.auth_required(auth)
def format_text():
    """Format text from a provided JSON array
    
    This endpoint accepts a JSON array of text objects and formats them
    into a structured response.
    """
    try:
        # Get the JSON data from the request
        data = request.json
        
        if not data or not isinstance(data, list):
            return jsonify({
                'status': 'error',
                'message': 'Invalid input. Expected a JSON array.'
            }), 400
        
        # Initialize the formatted response
        formatted_response = {
            'call_script': None,
            'recommendations': None,
            'account_details': None,
            'delinquency_analysis': None,
            'next_action': None
        }
        
        # Process each item in the array
        for item in data:
            if 'text' in item:
                text = item['text']
                
                # Categorize the content based on the starting text
                if text.startswith('Call Strategy Guide'):
                    formatted_response['call_script'] = text
                elif text.startswith('AI Recommended Actions'):
                    formatted_response['recommendations'] = text
                elif text.startswith("Let's analyze"):
                    formatted_response['delinquency_analysis'] = text
                elif text.startswith('Recommendation: Schedule'):
                    formatted_response['next_action'] = text
            elif 'Account_no' in item:
                # This is the account details object
                formatted_response['account_details'] = item
        
        return jsonify({
            'status': 'success',
            'formatted_data': formatted_response
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing request: {str(e)}'
        }), 500
    
# Start the actual app
# Get the PORT from environment or use the default
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=int(port))
