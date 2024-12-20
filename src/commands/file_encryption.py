import base64
import os
import hashlib
from cryptography.fernet import Fernet

class FileEncryption:
    def __init__(self, shell):
        self.shell = shell

    def generate_key(self, password):
        """Generate encryption key from password"""
        salt = b'salt_for_enhanced_shell'
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key

    def encrypt_command(self, args):
        """Encrypt a file"""
        if len(args) < 2:
            print("Usage: encrypt <input_file> -o <output_file>")
            return

        input_file = args[0]
        output_file = args[-1] if args[-2] == '-o' else input_file + '.enc'
        
        try:
            # Prompt for password
            password = input("Enter encryption password: ")
            
            # Generate key
            key = self.generate_key(password)
            fernet = Fernet(base64.urlsafe_b64encode(key))
            
            # Read and encrypt file
            with open(input_file, 'rb') as f:
                data = f.read()
            
            encrypted_data = fernet.encrypt(data)
            
            # Write encrypted data
            with open(output_file, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"File encrypted: {output_file}")
        
        except Exception as e:
            print(f"Encryption error: {e}")

    def decrypt_command(self, args):
        """Decrypt a file"""
        if len(args) < 2:
            print("Usage: decrypt <input_file> -o <output_file>")
            return

        input_file = args[0]
        output_file = args[-1] if args[-2] == '-o' else input_file.replace('.enc', '')
        
        try:
            # Prompt for password
            password = input("Enter decryption password: ")
            
            # Generate key
            key = self.generate_key(password)
            fernet = Fernet(base64.urlsafe_b64encode(key))
            
            # Read and decrypt file
            with open(input_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Write decrypted data
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
            
            print(f"File decrypted: {output_file}")
        
        except Exception as e:
            print(f"Decryption error: {e}")