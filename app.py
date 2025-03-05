import os
import ast
from apiflask import APIFlask
from flask_httpauth import HTTPTokenAuth
from dotenv import load_dotenv
from flask import request, jsonify
import json
import urllib.parse

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

@app.get('/format-text/<path:input_object>')
@app.auth_required(auth)
def format_text(input_object):
    """Format input object into a single HTML dropdown component
    
    This endpoint accepts a URL-encoded JSON array and returns 
    an HTML dropdown with sections for each text item.
    """
    try:
        # Decode the URL-encoded input object
        decoded_input = urllib.parse.unquote(input_object)
        
        # Parse the JSON 
        data = json.loads(decoded_input)
        
        if not data or not isinstance(data, list):
            return jsonify({
                'status': 'error',
                'message': 'Invalid input. Expected a JSON array.'
            }), 400
        
        # Generate HTML dropdown
        dropdown_html = '<select class="custom-dropdown">'
        
        # Process each item in the array
        for index, item in enumerate(data, 1):
            if 'text' in item:
                # Split the text into heading and content
                text_parts = item['text'].split('\n', 1)
                heading = text_parts[0].strip()
                content = text_parts[1].strip() if len(text_parts) > 1 else ''
                
                # Add option to dropdown
                dropdown_html += f'<option value="{index}" data-content="{account_details.replace(\'"', "&quot;")}">{heading if "Account_no" in item else "Account Details"}</option>'
            
            elif 'Account_no' in item:
                # Convert account details to a readable format
                account_details = "\n".join([f"{k}: {v}" for k, v in item.items()])
                dropdown_html += f'<option value="{index}" data-content="{account_details.replace('"', "&quot;")}"">Account Details</option>'
        
        dropdown_html += '</select>'
        
        # Wrap the dropdown with a container for additional context
        full_html = f'''
            <div class="dropdown-container">
                {dropdown_html}
                <div class="dropdown-content"></div>
            </div>
            <script>
            document.querySelector('.custom-dropdown').addEventListener('change', function() {{
                const selectedOption = this.options[this.selectedIndex];
                const contentDiv = this.nextElementSibling;
                contentDiv.innerHTML = `<pre>${{selectedOption.getAttribute('data-content')}}</pre>`;
            }});
            </script>
        '''
        
        # Return the HTML component
        return full_html
    
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
