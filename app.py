import json
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import subprocess
import paramiko
import os
import time

app = Flask(__name__)
ssh_client = paramiko.SSHClient()
socketio = SocketIO(app)

def get_docker_status():    
    command = "docker ps --format '{{.Names}}: {{.Status}}'"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if error:
        raise Exception("Error from SSH command: " + error)

    status_dict = {"nginx": "", "redis": ""}
    for line in output.splitlines():
        print("line >> ", line)
        parts = line.split(': ')
        if len(parts) == 2:
            status_dict[parts[0]] = 'Running' if 'Up' in parts[1] else 'Stopped'
    return status_dict

def monitor_services(host, username, password): 
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, port=22, username=username, password=password)
   
    while True:
        try:
            status = get_docker_status()
            socketio.emit('service_status', status)
        except Exception as e:
            socketio.emit('service_status', {'error': str(e)})
        time.sleep(5)  # Sleep for 5 seconds before checking again

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

@socketio.on('init_connection')
def handle_connection(data):
    hostname = data['hostname']
    username = data['username']
    password = data['password']
    socketio.start_background_task(monitor_services, hostname, username, password)

@socketio.on('stop_service')
def handle_stop_service(service_name):
    # Placeholder: SSH connection setup should already exist
    try:
        # Example command to stop a Docker service
        stop_command = f"docker stop {service_name}"
        stdin, stdout, stderr = ssh_client.exec_command(stop_command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if error:
            socketio.emit('service_action', {'result': f'Error stopping {service_name}: {error}'})
        else:
            socketio.emit('service_action', {'result': f'{service_name} stopped successfully.'})
    except Exception as e:
        socketio.emit('service_action', {'result': str(e)})

@app.route('/install-prerequisites', methods=['POST'])
def install_prerequisites():
    data = request.json
    server_host = data.get('serverHost', '')
    username = data.get('username', '')
    password = data.get('password', '')

    if not validate_credentials(server_host, username, password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 400

    try:
        local_paths = ['./requirements.txt', 'install_docker.sh', 'install_fluentd.sh']
        remote_path = '.'  # Destination directory on the server
        # Transfer files to the server
        transfer_files_to_server(server_host, username, password, local_paths, remote_path) 
        # pip freeze > requirements.txt
        
        subprocess.run(['ssh', f'{username}@{server_host}', 'chmod', '+x', 'install_docker.sh'])
        subprocess.run(['ssh', f'{username}@{server_host}', './install_docker.sh'])
        subprocess.run(['ssh', f'{username}@{server_host}', 'chmod', '+x', 'install_fluentd.sh'])
        subprocess.run(['ssh', f'{username}@{server_host}', './install_fluentd.sh'])
        subprocess.run(['ssh', f'{username}@{server_host}', 'pip', 'install', '-r', 'requirements.txt'])
        return jsonify(message="Installation successful!")
    except subprocess.CalledProcessError as e:
        return jsonify(message=f"Installation failed: {str(e)}"), 500

@app.route('/receive_logs', methods=['POST'])
def receive_logs():
    # Receive log message from Fluentd agent
    log_data = request.json
    print("Received log:", log_data)
    
    # Process log message (e.g., store in database, write to file, etc.)
    # Example: Store log message in a file
    with open('logs.txt', 'a') as f:
        f.write(json.dumps(log_data) + '\n')
    
    return 'Log received successfully', 200

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
