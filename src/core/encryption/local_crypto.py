import os
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

load_dotenv()

class LocalCrypto:
    """
    AES-GCM tabanlı Yerel Şifreleme Modülü.
    Log verilerini yerel olarak şifreler ve şifresini çözer.
    Simetrik anahtar (DEK) kullanır.
    """

    def __init__(self, key: bytes = None):
        """
        :param key: 32-byte (256-bit) AES anahtarı. Eğer verilmezse rastgele üretilir.
        """
        if key:
            if len(key) != 32:
                raise ValueError("Anahtar uzunluğu 32 byte (256-bit) olmalıdır.")
            self.key = key
        else:
            # .env'den okumaya çalış
            env_key = os.getenv("AES_SECRET_KEY")
            if env_key:
                try:
                    # Base64 encoded gelmesi beklenir
                    self.key = base64.b64decode(env_key)
                except:
                    # Raw string ise encode et ve 32 byte'a tamamla/kes
                    self.key = env_key.encode('utf-8')[:32].ljust(32, b'\0')
            else:
                self.key = self.generate_key()

    @staticmethod
    def generate_key() -> bytes:
        """Kriptografik olarak güvenli 256-bit rastgele anahtar üretir."""
        return os.urandom(32)

    def encrypt(self, plaintext: str) -> dict:
        """
        Metni şifreler.
        Return: {
            "ciphertext": base64 string,
            "nonce": base64 string (IV),
            "tag": base64 string (Auth Tag)
        }
        """
        # 1. Nonce (IV) üret (GCM için 12 byte önerilir)
        nonce = os.urandom(12)

        # 2. Cipher oluştur
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce),
            backend=default_backend()
        ).encryptor()

        # 3. Şifrele
        data_bytes = plaintext.encode('utf-8')
        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()

        # 4. JSON friendly format için Base64'e çevir
        return {
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "tag": base64.b64encode(encryptor.tag).decode('utf-8')
        }

    def decrypt(self, encrypted_payload: dict) -> str:
        """
        Şifreli payload'u çözer.
        :param encrypted_payload: encrypt metodundan dönen sözlük
        Return: Decoded plaintext string
        """
        try:
            # 1. Base64 decode
            ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
            nonce = base64.b64decode(encrypted_payload["nonce"])
            tag = base64.b64decode(encrypted_payload["tag"])

            # 2. Cipher oluştur
            decryptor = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            ).decryptor()

            # 3. Çöz ve doğrula
            decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            return decrypted_bytes.decode('utf-8')

        except Exception as e:
            raise ValueError(f"Şifre çözme hatası: {str(e)}")

# Kullanım Örneği (Test için)
if __name__ == "__main__":
    crypto = LocalCrypto()
    print(f"🔑 Generated DEK: {base64.b64encode(crypto.key).decode('utf-8')}")
    
    msg = "Bu kritik bir sistem logudur. Storage'a şifreli gitmelidir."
    print(f"\n📝 Plaintext: {msg}")
    
    enc = crypto.encrypt(msg)
    print(f"🔒 Encrypted: {json.dumps(enc, indent=2)}")
    
    dec = crypto.decrypt(enc)
    print(f"🔓 Decrypted: {dec}")
    
    assert msg == dec
    print("\n✅ Doğrulama Başarılı!")
