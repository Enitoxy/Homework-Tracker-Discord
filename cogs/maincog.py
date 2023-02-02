import discord
import pymongo
import os
import random

from discord import app_commands, ui
from discord.ext import commands

from dotenv import load_dotenv
from datetime import datetime
now = datetime.now()


#DOTENV
load_dotenv()
MONGODB = os.getenv('MONGODB_PASSWORD')


mdbclient = pymongo.MongoClient(f"{MONGODB}")
registered_ids = mdbclient.registered_ids


#COG CLASS
class Test(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    #PING COMMAND
    @app_commands.command(name="ping", description="Shows the latency of the bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Ping: {0}ms'.format(round(self.bot.latency, 3)), ephemeral=False)

    
    @app_commands.command(name="myhomework", description="Lists all of your homework!")
    #Cycles through _idlist with buttons
    #Has a (Mark Complete) button
    #Has a (Delete) button
    async def myhomework(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        author = interaction.user.id
        key = {'author': author}
        _idlist = "\r\n".join(f"> {id['id']}" for id in registered_ids.homework.find(key))
        print(_idlist)
        await interaction.followup.send(f"Your IDs:\n\n{_idlist}")


    @app_commands.command(name="add", description="Adds homework to your list!")
    async def add(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(addHW())

class addHW(ui.Modal, title="Add your homework!"):

    hwtitle = ui.TextInput(label="Title", style=discord.TextStyle.short, placeholder="Add a title!", required=True)
    subject = ui.TextInput(label="Subject", style=discord.TextStyle.short, placeholder="What subject?", required=True)
    description = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, placeholder="Give a description (optional)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        result = registered_ids.homework.insert_one(
            {
                "title": str(self.hwtitle),
                "subject": str(self.subject),
                "description": str(self.description),
                "complete": bool(False),
                "date": str(now.strftime("%d/%m/%Y %H:%M")),
                "author": interaction.user.id
            }
        )
        id = result.inserted_id
        await interaction.response.send_message(f"Homework added successfully!\n> Unique ID: {id}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Test(bot))