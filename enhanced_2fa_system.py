import pyotp
import qrcode
import random
import string
import time

# Simulated databases
users_db = {}
backup_codes_db = {}
failed_attempts = {}
recovery_emails_db = {}

# Rate limiting parameters
TIME_WINDOW = 300  # 5 minutes in seconds
MAX_ATTEMPTS = 3
BLOCK_DURATION = 600  # 10 minutes in seconds

def generate_secret_key():
    return pyotp.random_base32()

def generate_backup_codes():
    return [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(10)]  # Generate 10 backup codes

def generate_qr_code(secret_key, user_email):
    totp = pyotp.TOTP(secret_key)
    provision_uri = totp.provisioning_uri(name=user_email, issuer_name="YourAppName")
    img = qrcode.make(provision_uri)
    img.show()

def register_user(email, recovery_email):
    if email in users_db:
        print("User already exists!")
        return
    secret_key = generate_secret_key()
    users_db[email] = secret_key
    backup_codes = generate_backup_codes()
    backup_codes_db[email] = backup_codes
    recovery_emails_db[email] = recovery_email
    print(f"User {email} registered with secret key: {secret_key}")
    print("Backup Codes:")
    for code in backup_codes:
        print(code)
    print("Generating QR Code for 2FA setup...")
    generate_qr_code(secret_key, email)

def send_recovery_code_to_email(email):
    recovery_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    # In a real-world scenario, you'd use an email service to send the recovery code.
    # For this example, we'll just print it.
    print(f"Sending recovery code to {email}: {recovery_code}")
    return recovery_code

def verify_totp(email, provided_totp):
    if email not in users_db:
        return False
    secret_key = users_db[email]
    totp = pyotp.TOTP(secret_key)
    return totp.verify(provided_totp)

def verify_backup_code(email, provided_code):
    if email not in backup_codes_db:
        return False
    if provided_code in backup_codes_db[email]:
        backup_codes_db[email].remove(provided_code)
        return True
    return False

def is_user_blocked(email):
    if email not in failed_attempts:
        return False
    last_attempt_time, attempts = failed_attempts[email]
    if time.time() - last_attempt_time < BLOCK_DURATION and attempts >= MAX_ATTEMPTS:
        return True
    return False

def record_failed_attempt(email):
    if email not in failed_attempts:
        failed_attempts[email] = (time.time(), 1)
    else:
        last_attempt_time, attempts = failed_attempts[email]
        if time.time() - last_attempt_time > TIME_WINDOW:
            failed_attempts[email] = (time.time(), 1)
        else:
            failed_attempts[email] = (last_attempt_time, attempts + 1)

def login(email, provided_totp_or_code):
    if is_user_blocked(email):
        print("Too many failed attempts. Please wait and try again later.")
        return

    if verify_totp(email, provided_totp_or_code) or verify_backup_code(email, provided_totp_or_code):
        print("Login successful!")
        if email in failed_attempts:
            del failed_attempts[email]
    else:
        print("Invalid TOTP or backup code. Please try again.")
        record_failed_attempt(email)

if __name__ == "__main__":
    while True:
        print("\nOptions:")
        print("1. Register")
        print("2. Login")
        print("3. Send recovery code to backup email")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            email = input("Enter email to register: ")
            recovery_email = input("Enter a recovery email: ")
            register_user(email, recovery_email)
        elif choice == "2":
            email = input("Enter email to login: ")
            provided_totp_or_code = input("Enter the TOTP from your authenticator app, a backup code, or a recovery code: ")
            login(email, provided_totp_or_code)
        elif choice == "3":
            email = input("Enter your registered email: ")
            if email in recovery_emails_db:
                send_recovery_code_to_email(recovery_emails_db[email])
            else:
                print("Email not found!")
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")
