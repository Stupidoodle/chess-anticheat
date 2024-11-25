from cryptography.fernet import Fernet
from typing import Dict, Any
import base64
import json


class DataEncryption:
    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)

    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt sensitive data."""
        json_data = json.dumps(data)
        encrypted_data = self.fernet.encrypt(json_data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt sensitive data."""
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.fernet.decrypt(decoded_data)
        return json.loads(decrypted_data.decode())


class DataMasking:
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive information in logs and reports."""
        masked_data = data.copy()
        sensitive_fields = ["ip_address", "user_agent", "email"]

        for field in sensitive_fields:
            if field in masked_data:
                value = str(masked_data[field])
                masked_data[field] = f"{value[:3]}...{value[-3:]}"

        return masked_data
