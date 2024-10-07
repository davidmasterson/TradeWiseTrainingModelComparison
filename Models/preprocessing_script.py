from database import preprocessing_scripts_DAOIMPL
from datetime import datetime
from cryptography.fernet import Fernet
import boto3
from flask import session
import logging
import base64

class Preprocessing_Script:
    
    
    def __init__(self, script_name, script, upload_date, script_description, username, user_id):
        self.script_name = script_name
        self.script = script
        self.user_id = user_id
        self.upload_date = upload_date
        self.script_description = script_description
        self.user_alias = f'{username}{user_id}'
        self.encrypted_fernet_key = None

        # Check for existing cipher in KMS or create a new one
        self.cipher_key = self.check_for_existing_or_create_new_key()

        # Initialize Fernet with the decrypted cipher key
        self.cipher = Fernet(self.cipher_key)
        # Encrypt the script
       
        self.script = self.cipher.encrypt(self.script.encode())
        
    
    def check_for_existing_or_create_new_key(self):
        kms_client = boto3.client('kms', region_name='us-east-2')

        # Check if the user has a pre-existing key by alias
        aliases = kms_client.list_aliases()['Aliases']
        for alias in aliases:
            if alias['AliasName'] == f'alias/{self.user_alias}':
                # Assuming the encrypted Fernet key is stored somewhere securely.
                encrypted_key = preprocessing_scripts_DAOIMPL.get_preprocessing_script_encrypted_fernet_key_for_user(self.user_id)
                if encrypted_key:
                    # Decrypt the encrypted Fernet key with KMS
                    decrypted_key = kms_client.decrypt(CiphertextBlob=encrypted_key)['Plaintext']
                    return decrypted_key

        # If no existing KMS key or Fernet key, create a new one
        key_response = kms_client.create_key(
            Description=f'Encryption key for {self.user_alias}',
            KeyUsage='ENCRYPT_DECRYPT',
            Origin='AWS_KMS'
        )

        key_id = key_response['KeyMetadata']['KeyId']

        # Assign alias to the new key
        try:
            kms_client.create_alias(
                AliasName=f'alias/{self.user_alias}',
                TargetKeyId=key_id
            )
        except kms_client.exceptions.AlreadyExistsException:
            logging.info(f"Alias {self.user_alias} already exists.")

        # Generate a new Fernet key and encrypt it using KMS
        new_fernet_key = Fernet.generate_key()
        encrypted_cipher = self.upload_cryptography_cipher_to_kms(new_fernet_key)

        # Save the encrypted Fernet key securely (e.g., in the database)
        self.encrypted_fernet_key = base64.urlsafe_b64encode(encrypted_cipher)
        return new_fernet_key

    def upload_cryptography_cipher_to_kms(self, cipher_key):
        kms_client = boto3.client('kms', region_name='us-east-2')

        # Encrypt the Fernet key using the KMS key
        encrypted_cipher = kms_client.encrypt(
            KeyId=f'alias/{self.user_alias}',
            Plaintext=cipher_key
        )

        return encrypted_cipher['CiphertextBlob']

    def store_script(self):
        # Store encrypted script, script name, description, user_id, and alias in the database
        preprocessing_scripts_DAOIMPL.store_script(
            self.encrypted_script,
            self.script_name,
            self.user_id,
            self.script_description,
            f'alias/{self.user_alias}',  # Store the alias in the database
            self.encrypted_fernet_key
        )

    def get_script_from_database_and_decrypt(user_id, script_name):
        kms_client = boto3.client('kms', region_name='us-east-2')
        # Get the encrypted script from the database
        encrypted_script = preprocessing_scripts_DAOIMPL.get_encrypted_preprocessing_script_for_user(user_id,script_name)
        if encrypted_script:
            encrypted_script = encrypted_script[0]
        # Get the Fernet key to decrypt the script (from database or KMS)
        fernet_key = preprocessing_scripts_DAOIMPL.get_preprocessing_script_encrypted_fernet_key_for_user(user_id)
        if fernet_key:
            fernet_key = fernet_key[0][0]
        encrypted_key = base64.urlsafe_b64decode(fernet_key)
        decrypted_key = kms_client.decrypt(CiphertextBlob=encrypted_key)['Plaintext']
        # Initialize Fernet
        cipher = Fernet(decrypted_key)
        # Decrypt the script
        decrypted_script = cipher.decrypt(encrypted_script).decode('utf-8')
        return decrypted_script