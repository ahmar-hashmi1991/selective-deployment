from flask import Flask, request, jsonify
import subprocess
import paramiko

app = Flask(__name__)

def validate_credentials(server_host, username, password):
    # Attempt to establish an SSH connection to the server
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("hostname >> ", server_host)
        print("username >> ", username)
        print("password >> ", password)
        ssh_client.connect(hostname=server_host, username=username, password=password)
        
        # Start Docker daemon if the connection is successful
        stdin, stdout, stderr = ssh_client.exec_command('sudo systemctl start docker')
        ssh_client.close()
        return True
    except Exception as e:
        print(f"Error validating credentials: {e}")
        return False

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/deploy', methods=['POST'])
def deploy_microservices():
    data = request.json
    selected_services = data.get('services', [])
    server_host = data.get('serverHost', '')
    username = data.get('username', '')
    password = data.get('password', '')

    # Validate credentials
    if not validate_credentials(server_host, username, password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 400

    try:
        for service in selected_services:
            if service == 'redis':
                # Example command to deploy Redis service on the specified server
                subprocess.run(['ssh', f'{username}@{server_host}', 'docker-compose', '-f', 'docker-compose-redis.yml', 'up', '-d'])
            elif service == 'nginx':
                # Example command to deploy Nginx service on the specified server
                subprocess.run(['ssh', f'{username}@{server_host}', 'docker-compose', '-f', 'docker-compose-nginx.yml', 'up', '-d'])
            # Add more conditions for other services as needed
        return jsonify({'success': True}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
