import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/api/proxy', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy_request():
    target_url = request.args.get('url')
    if not target_url:
        return Response("Error: 'url' parameter is required.", status=400)

    # If no scheme is provided, assume https
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

        # Forward the request to the target URL
    try:
            # Get the request data and headers from the incoming request
        original_request_data = request.get_data()
        headers = request.headers.to_dict()

            # Remove headers that should not be forwarded
        headers.pop('Host', None)
        headers.pop('X-Forwarded-For', None)
        headers.pop('X-Real-IP', None)
        headers.pop('Connection', None)
        headers.pop('Content-Length', None)

        method = request.method

        proxied_response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=original_request_data,
            stream=True # Use stream=True for large responses
            )

            # Prepare the response from the target URL
        response_data = proxied_response.content
        response_headers = proxied_response.headers.to_dict()

            # Remove headers that should not be included in the response
        response_headers.pop('Content-Encoding', None)
        response_headers.pop('Transfer-Encoding', None)
        response_headers.pop('Content-Length', None)
            # You might want to add CORS headers here if needed for cross-origin requests
            # response_headers['Access-Control-Allow-Origin'] = '*'

        return Response(
            response_data,
            status=proxied_response.status_code,
            headers=response_headers
            )

    except requests.exceptions.RequestException as e:
        # Handle connection errors or other request issues
        return Response(f"Error connecting to target URL: {e}", status=502)

    # This part is usually for running locally, Vercel handles it differently
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
