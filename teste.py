from cryptography.fernet import Fernet


k = Fernet.generate_key()
g = Fernet(k)
with open("C:\\Users\\Marcu\\Documents\\Faculdade\\2022\\teste1.txt", "wb")
g.encrypt()