from flask import Flask, request, jsonify
import subprocess
import paramiko
import os

app = Flask(__name__)
ssh_client = paramiko.SSHClient()

def validate_credentials(server_host, username, password):
    # Attempt to establish an SSH connection to the server
    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("hostname >> ", server_host)
        print("username >> ", username)
        print("password >> ", password)
        ssh_client.connect(hostname=server_host, username=username, password=password)
        
        return True
    except Exception as e:
        print(f"Error validating credentials: {e}")
        return False

def transfer_files_to_server(server_host, username, password, local_paths, remote_path):
    try:
        # Create SSH client
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=server_host, username=username, password=password)
        
        # Create SFTP client
        sftp_client = ssh_client.open_sftp()
        
        # Transfer files
        for local_path in local_paths:
            filename = os.path.basename(local_path)
            sftp_client.put(local_path, f"{remote_path}/{filename}")
        
        sftp_client.close()
        print("Files transferred successfully.")
    except Exception as e:
        print(f"Error transferring files: {e}")

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/install-prerequisites', methods=['POST'])
def install_prerequisites():
    data = request.json
    server_host = data.get('serverHost', '')
    username = data.get('username', '')
    password = data.get('password', '')

    if not validate_credentials(server_host, username, password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 400

    try:
        local_paths = ['./install_docker.sh']
        remote_path = '.'  # Destination directory on the server
        # Transfer files to the server
        transfer_files_to_server(server_host, username, password, local_paths, remote_path) 

        subprocess.run(['ssh', f'{username}@{server_host}', 'chmod +x ./install_docker.sh', './install_docker.sh'])
        return jsonify(message="Installation successful!")
    except subprocess.CalledProcessError as e:
        return jsonify(message=f"Installation failed: {str(e)}"), 500

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
        local_paths = ['./docker-compose-redis.yml', './docker-compose-nginx.yml']
        remote_path = '.'  # Destination directory on the server
        # Transfer files to the server
        transfer_files_to_server(server_host, username, password, local_paths, remote_path)

        # Start Docker daemon if the connection is successful
        stdin, stdout, stderr = ssh_client.exec_command('systemctl start docker')

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
