import discord
import pymongo
import os
import random

from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv


#DOTENV
load_dotenv()
PASS = os.getenv('MONGODB_PASSWORD')


client = pymongo.MongoClient(f"mongodb+srv://TimelessOn15Hz:{PASS}@cluster0.03k6m8r.mongodb.net/?retryWrites=true&w=majority")
id_db = client.registered_ids


#COG CLASS
class Test(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    #PING COMMAND
    @app_commands.command(name="ping", description="Shows the latency of the bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Ping: {0}ms'.format(round(self.bot.latency, 3)), ephemeral=False)


    @app_commands.command(name="register", description="Registers an ID to the database")
    async def register(self, interaction: discord.Interaction, title: str) -> None:       
        id_db.ids.insert_one(
            {
                "title": title,
                "id": id,
                "author": interaction.user.id
            }
        )
        await interaction.response.send_message("ID was registered!")

    
    @app_commands.command(name="ping", description="Shows the latency of the bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Ping: {0}ms'.format(round(self.bot.latency, 3)), ephemeral=False)


    @app_commands.command(name="myid", description="Retrieves author's registered IDs")
    async def myid(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        author = interaction.user.id
        key = {'author': author}
        _idlist = "\r\n".join(f"> {id['id']}" for id in id_db.ids.find(key))
        await interaction.followup.send(f"Your IDs:\n\n{_idlist}")


async def setup(bot):
    await bot.add_cog(Test(bot))