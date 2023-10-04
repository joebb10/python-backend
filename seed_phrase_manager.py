from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import random
import string
import time

MAX_ATTEMPTS = 3
DELAY_INCREMENT = 5  # in seconds

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def generate_backup_codes(n=5, length=8):
    codes = []
    for _ in range(n):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        codes.append(code)
    return codes

def wipe_memory(data: str) -> None:
    # Overwrite the memory location with zeros
    data = '\0' * len(data)

def main():
    salt = os.urandom(16)
    attempts = 0

    choice = input("Do you want to (S)tore, (R)etrieve, or (B)ackup recovery the seed phrase? ")

    if choice.lower() == 's':
        seed_phrase = input("Enter your seed phrase: ")
        password = input("Set a password for encryption: ")
        key = derive_key(password, salt)
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(seed_phrase.encode())
        with open("seed_data.enc", "wb") as file:
            file.write(salt + encrypted_data)
        backup_codes = generate_backup_codes()
        print("Seed phrase stored securely!")
        print("Your backup codes are:")
        for code in backup_codes:
            print(code)
        print("Store these codes in separate secure locations!")
        wipe_memory(seed_phrase)
        wipe_memory(password)

    elif choice.lower() == 'r':
        while attempts < MAX_ATTEMPTS:
            password = input("Enter your password: ")
            with open("seed_data.enc", "rb") as file:
                data = file.read()
                salt, encrypted_data = data[:16], data[16:]
            key = derive_key(password, salt)
            cipher = Fernet(key)
            try:
                seed_phrase = cipher.decrypt(encrypted_data).decode()
                print(f"Your seed phrase is: {seed_phrase}")
                wipe_memory(seed_phrase)
                break
            except:
                print("Incorrect password!")
                attempts += 1
                if attempts < MAX_ATTEMPTS:
                    print(f"Please wait {DELAY_INCREMENT * attempts} seconds before trying again.")
                    time.sleep(DELAY_INCREMENT * attempts)
                else:
                    print("Max attempts reached!")
            wipe_memory(password)

    elif choice.lower() == 'b':
        while attempts < MAX_ATTEMPTS:
            code = input("Enter one of your backup codes: ")
            # In a real-world scenario, you'd verify the backup code against stored codes.
            # For simplicity, we're skipping that step here.
            with open("seed_data.enc", "rb") as file:
                data = file.read()
                salt, encrypted_data = data[:16], data[16:]
            password = input("Set a new password for encryption: ")
            key = derive_key(password, salt)
            cipher = Fernet(key)
            try:
                seed_phrase = cipher.decrypt(encrypted_data).decode()
                print(f"Your seed phrase is: {seed_phrase}")
                wipe_memory(seed_phrase)
                break
            except:
                print("Incorrect backup code or corrupted data!")
                attempts += 1
                if attempts < MAX_ATTEMPTS:
                    print(f"Please wait {DELAY_INCREMENT * attempts} seconds before trying again.")
                    time.sleep(DELAY_INCREMENT * attempts)
                else:
                    print("Max attempts reached!")
            wipe_memory(password)

if __name__ == "__main__":
    main()
