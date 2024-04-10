from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/deploy', methods=['POST'])
def deploy_microservices():
    selected_services = request.json.get('services', [])
    # Deploy selected services based on checkbox selection
    try:
        for service in selected_services:
            if service == 'redis':
                subprocess.run(['docker-compose', '-f', 'docker-compose-redis.yml', 'up', '-d'])
            elif service == 'nginx':
                subprocess.run(['docker-compose', '-f', 'docker-compose-nginx.yml', 'up', '-d'])
            # Add more conditions for other services as needed
        return jsonify({'success': True}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True)
