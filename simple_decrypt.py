import math
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Hash import MD5

BLOCKSIZE = 256


h = MD5.new()
with open('/home/cse/Lab3/Q5files/R5.py', 'rb') as afile: 
    buf = afile.read(BLOCKSIZE)
    while len(buf) > 0:
        h.update(buf)
        buf = afile.read(BLOCKSIZE)


key = h.digest()


file_path = "/home/cse/Lab3/Q5files/Encrypted5"  
with open(file_path, 'rb') as enc_file:
    iv = enc_file.read(16)
    encrypted_data = enc_file.read() 


cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)


output_file = 'Decrypted5.txt'
with open(output_file, 'wb') as dec_file:
    dec_file.write(decrypted_data)

print(f'Decryption complete! The decrypted file is saved as {output_file}.')
