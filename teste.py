from cryptography.fernet import Fernet


k = Fernet.generate_key()
g = Fernet(k)
with open("Zt", "wb")
    g.encrypt()
