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

# the secret API key, plus we need a username in that record
API_TOKEN="{{'{0}':'appuser'}}".format(os.getenv('API_TOKEN'))
#convert to dict:
tokens=ast.literal_eval(API_TOKEN)

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

@app.get('/format-text/<string:text>')
@app.auth_required(auth)
def format_text(text):
    """Format text into a collapsible heading with content
    
    This endpoint accepts text as a URL parameter and returns a 
    formatted JSON response with a heading and collapsible content.
    """
    try:
        # Validate the input text
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'Invalid input. Text cannot be empty.'
            }), 400
        
        # Split the text into heading and content
        # If text doesn't contain a newline, use the first 50 characters as heading
        if '\n' in text:
            heading, content = text.split('\n', 1)
        else:
            heading = text[:50] + ('...' if len(text) > 50 else '')
            content = text
        
        # Create the formatted response
        formatted_response = {
            'heading': heading.strip(),
            'content': content.strip(),
            'is_collapsible': True
        }
        
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
