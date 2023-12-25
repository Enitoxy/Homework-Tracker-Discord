"""
components.db
~~~~~~~~~~~~~~~~~~~~~

Extension for asynchronous MongoDB connection.
"""

import glob
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from colorama import init as colorama_init
from colorama import Fore, Style

uri = "mongodb+srv://clusterzero.cco7h0p.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
cert = glob.glob("./certificates/X509-cert*.pem")
client = AsyncIOMotorClient(
    uri,
    tls=True,
    tlsCertificateKeyFile=cert[0],
    server_api=ServerApi('1')
    )

colorama_init(autoreset=True)

c = (
    Style.RESET_ALL,
    Fore.LIGHTBLACK_EX,
    Fore.LIGHTGREEN_EX,
    Fore.RED
    )

try:
    client.admin.command('ping') #type: ignore
    print(f"{c[1]}----------------------\n{c[2]}Ping!{c[0]} - Connected to MongoDB!")
except Exception as e:
    print(f"{c[3]}{e}")