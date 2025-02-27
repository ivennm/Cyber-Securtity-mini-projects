import hashlib
import subprocess
import time
import tempfile

gang_file = '/home/cse/Lab1/Q6/gang'
salted_passwords_file = '/home/cse/Lab1/Q6/SaltedPWs'
pwned_passwords_file = '/home/cse/Lab1/Q6/PwnedPWs100k'
login_program = '/home/cse/Lab1/Q6/Login.pyc'

temp_file = tempfile.NamedTemporaryFile(delete=False)
output_file = temp_file.name
print(f"Using temporary file: {output_file}")

with open(gang_file, 'r') as file:
    gang_members = [line.strip() for line in file]

salted_credentials = {}
with open(salted_passwords_file, 'r') as file:
    for line in file:
        parts = line.strip().split(',')
        if len(parts) == 3:
            username, salt, hashed_pw = parts
            salted_credentials[username] = (salt, hashed_pw)

with open(pwned_passwords_file, 'r') as file:
    pwned_passwords = [line.strip() for line in file]

def hash_with_salt(salt, password):
    combined = salt + password
    return hashlib.sha256(combined.encode()).hexdigest()

def try_login(username, password):
    try:
        result = subprocess.run(['python3', login_program, username, password], capture_output=True, text=True)
        return "Login successful." in result.stdout
    except Exception as e:
        print(f"Error trying {username} with password {password}: {e}")
        return False

start_time = time.strftime("%Y-%m-%d %H:%M:%S")
print(f"Start time: {start_time}\n")

found_credentials = {}

for member in gang_members:
    if member in salted_credentials:
        salt, correct_hash = salted_credentials[member]
        print(f"Trying to find password for {member}...")
        for base_password in pwned_passwords:
            for digit in range(10):
                guess = f"{base_password}{digit}"
                hashed_guess = hash_with_salt(salt, guess)
                if hashed_guess == correct_hash:
                    print(f"Password found for {member}: {guess}")
                    if try_login(member, guess):
                        print(f"Login successful for {member} with password: {guess}")
                        found_credentials[member] = guess
                        break
            if member in found_credentials:
                break

try:
    with open(output_file, 'w') as file:
        for username, password in found_credentials.items():
            file.write(f"{username},{password}\n")
    print(f"Successfully wrote found credentials to {output_file}")
except IOError as e:
    print(f"Error writing to file {output_file}: {e}")

end_time = time.strftime("%Y-%m-%d %H:%M:%S")
print(f"End time: {end_time}")
elapsed_time = end_time - start_time
print(f"End time: {end_time}")
print(f"Elapsed time: {elapsed_time:.2f} seconds")