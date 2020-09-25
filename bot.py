import os
import random
import ast
import asyncio
import discord
import time
from datetime import datetime, time
from dotenv import load_dotenv
from discord.ext import commands
from databases import Database

# set to true to read bot info form the config file
# or false to read from env variables
development = False

keywords = [
    "cheers",
    "Cheers",
    "take a shot",
    "take a drink",
    "drink",
    "Sipskie",
    "Shots",
]

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

async def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

async def add_to_db(date, time1, time2):
    new = True
    time = f"{time1}-{time2}"
    query = "SELECT * FROM stats"
    rows = await database.fetch_all(query=query)
    for row in rows:
        if str(row[0]) == str(date):
            if str(row[1]) == str(time):
                new = False
                query = "UPDATE stats SET count = (:count) WHERE Date = (:Date) AND Time = (:Time)"
                values = [
                    {"count": str(int(row[2])+1), "Date": date, "Time": time}
                ]
                await database.execute_many(query=query, values=values)
                break
    if new:
        print("new")
        query = "INSERT INTO stats(Date, Time, count) VALUES (:Date, :Time, :count)"
        values = [
            {"Date": date, "Time": time, "count": 1}
        ]
        await database.execute_many(query=query, values=values)
        new = False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Making Drinks"))
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user.name} has connected to Discord!')
    print(f'{guild.name}(id: {guild.id})')
    await database.connect()

@bot.event
async def on_message(message: str):
    utc = datetime.utcnow().time()
    date = datetime.today().strftime('%Y-%m-%d')
    between = False
    check = any(x in message.content for x in keywords)
    if check:
        for x in range(0,24):
            if not between:
                try:
                    between = await is_time_between(time(x,0), time(x+1,0))
                except:
                    # print("except")
                    between = await is_time_between(time(x,0), time(0,0))
            if between:
                between1 = x
                between2 = x+1
                break
        print(f'time is between: {between1} and {between2}\n the date is {date}\n the time is: {utc}\n a drink has been logged: {check}\n message was: "{message.content}"')
        await add_to_db(date,between1,between2)

bot.run(TOKEN)