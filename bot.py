import os
import random
import ast
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands
from databases import Database

# set to true to read bot info form the config file
# or false to read from env variables
development = False
owner_id = "102131189187358720"

load_dotenv()

if development == True:
    import configparser
    print("development mode")
    config = configparser.ConfigParser()
    config.read('config.ini')
    bot = commands.Bot(command_prefix='*')
    TOKEN = config['discord']['BOT_TOKEN']
    GUILD = config['discord']['GUILD']
    database = Database(config['discord']['database'])
else:
    import environ
    env = environ.Env(DEBUG=(bool, False))
    bot = commands.Bot(command_prefix='#')
    TOKEN = env('BOT_TOKEN')
    GUILD = env('GUILD')
    database = Database(env('CLEARDB_DATABASE_URL'))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Making Drinks"))
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user.name} has connected to Discord!')
    print(f'{guild.name}(id: {guild.id})')
    await database.connect()


bot.run(TOKEN)