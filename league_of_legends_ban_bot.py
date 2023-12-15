import discord
import pytz
import pandas as pd
from discord_slash import SlashCommand
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta

################# ESSENTIALS #################
bot = commands.Bot(command_prefix='SMITER-', intents=discord.Intents().all())
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
   print("Ready to smite!")
############## END ESSENTIALS ################

# WARNING LIST FUNCTIONS

# returns index of user if found in warning list
def find_user(user_id):
    csv_file = 'warning_list.csv'
    df = pd.read_csv(csv_file)
    user_list = list(df.user)
    warning_list = list(df.warning)
    if user_id in user_list:
        index = user_list.index(user_id)
    return index

# true if in warning list, false if not
def user_in_list(user_id):
    csv_file = 'warning_list.csv'
    df = pd.read_csv(csv_file)
    user_list = list(df.user)
    try:
        position = user_list.index(user_id)
        return True
    except ValueError:
        return False

# adds user to warning list
def append_to_warning(user_id,warning):
    csv_file = 'warning_list.csv'
    data = {'user':[user_id],'warning':[warning]}
    dataframe = pd.DataFrame(data)
    if user_in_list(user_id) == False:
        dataframe.to_csv(csv_file,index=False,mode='a',header=False)

# returns amount of warnings for a specific user
def user_warnings(user_id):
    csv_file = 'warning_list.csv'
    df = pd.read_csv(csv_file)
    index = find_user(user_id)
    return df.loc[index, 'warning']

# adds a warning for a specific user
def add_warning(user_id, amount):
    csv_file = 'warning_list.csv'
    df = pd.read_csv(csv_file)
    index = find_user(user_id)
    df.loc[index, 'warning'] += amount
    df.to_csv(csv_file,index=False)

# FINDER COMMAND
@bot.command()
async def find_lol(message):
    found = False
    channel = message.channel
    await channel.send("Searching for League of Legends players...")
    for guild in bot.guilds:
        print("Searching in " + guild.name)
        for member in guild.members:
            for activity in member.activities:
                if(activity.name == "League of Legends"):
                    # GET START TIME
                    lol_index = member.activities.index(activity)
                    start_time = member.activities[lol_index].start     

                    # TIMEZONE OBJECTS
                    GMT = pytz.timezone('Asia/Manila')
                    UTC = pytz.timezone('Etc/UTC')

                    # LOCALIZATION
                    localized_time = UTC.localize(start_time)
                    new_timezone_timestamp = localized_time.astimezone(GMT)
                    displayed_time = new_timezone_timestamp.strftime("%H:%M %m-%d-%Y")

                    # TIME LIMIT
                    time_add = timedelta(minutes=30)
                    time_limit = new_timezone_timestamp + time_add
                    displayed_limit = time_limit.strftime("%H:%M %m-%d-%Y")

                    found = True
                    embed = discord.Embed(
                    title = "This user is currently playing League of Legends.",
                    description = member.mention + "#" + member.discriminator,
                    color = discord.Color.red()
                    )   
                    embed.add_field(name = "Time started: ",value = displayed_time)
                    embed.add_field(name = "Time limit: ", value = displayed_limit)
                    embed.set_footer(text="This user has until " + displayed_limit + " to stop playing League of Legends. Failure will result in ban. <3")
                    embed.set_image(url=member.avatar_url)
                    if new_timezone_timestamp > time_limit:
                        embed_text = "BAN KA NA!!! NALAMPASAN MO TIME LIMIT!"
                    elif new_timezone_timestamp < time_limit:
                        embed_text = "Baban kita pag nalampasan mo na time limit"
                    embed.add_field(name=embed_text,value = '-')
                    await channel.send(embed=embed)
        
        if found == False:
            embed = discord.Embed(
            title = "No one found, congratulations!",
            color = discord.Color.green()
            )   
            embed.set_image(url='https://i.kym-cdn.com/photos/images/original/002/114/638/e26.jpg')
            await channel.send(embed=embed)

# DETECT ANYTHING LOL RELATED FUNCTION 
@bot.event
async def on_message(message):
    channel = message.channel
    message_lowered = message.content.lower().split()
    lol_keywords=["of", "league", "lol", "legends", "league of legends"]
    laro_keywords=["play", "invite", "laro", "g"]
    if any(lol_keyword in message_lowered for lol_keyword in lol_keywords) and any(laro_keyword in message_lowered for laro_keyword in laro_keywords):

        if user_in_list(message.author.id):
            add_warning(message.author.id,1)
        else:
            append_to_warning(message.author.id,1)
        author_warnings = user_warnings(message.author.id)

        embed = discord.Embed(
        title = "You have said something related to League of Legends.",
        description = "BAWAL LOL DITO! WARNING KA!",
        color = discord.Color.red()
        )            
        embed.add_field(name='Name:',value=message.author,inline=True)
        embed.add_field(name='Warnings:', value=author_warnings,inline=True)
        await message.reply(embed=embed)
    await bot.process_commands(message)

# IF MEMBER PLAYS LOL IMMEDIATELY ALERT FUNCTION
@bot.event
async def on_member_update(before,after):
    if isinstance(after.activity,discord.activity.Game) == True:
        # Main Variables
        start_time = after.activity.start 
        channel = bot.get_channel(#put your channel here)
    
        # TIMEZONE OBJECTS
        GMT = pytz.timezone('Asia/Manila')
        UTC = pytz.timezone('Etc/UTC')

        # LOCALIZATION
        localized_time = UTC.localize(start_time)
        new_timezone_timestamp = localized_time.astimezone(GMT)
        displayed_time = new_timezone_timestamp.strftime("%H:%M %m-%d-%Y")

        # TIME LIMIT
        time_add = timedelta(minutes=30)
        time_limit = new_timezone_timestamp + time_add
        displayed_limit = time_limit.strftime("%H:%M %m-%d-%Y")

        # LEAGUE OF LEGENDS PROMPT
        for activity in after.activities:
            if(after.activity.name == "League of Legends"):
                # EMBEDDING SECTION
                embed = discord.Embed(
                title = after.name + " has started playing " + after.activity.name,
                description = "This user is playing " + after.activity.name,
                color = discord.Color.red()
                )            
                embed.add_field(name = "Time started: ",value = displayed_time)
                embed.add_field(name = "Time limit: ", value = displayed_limit)
                embed.set_footer(text="This user has until " + displayed_limit + " to stop playing League of Legends. Failure will result in ban. <3")
                await channel.send(embed=embed)

            # GENSHIN IMPACT PROMPT
            elif after.activity.name == 'Genshin Impact':
                embed = discord.Embed(
                title = 'Genshin Bakla',
                description = after.mention + ' masaya kaba talaga jan',
                color = discord.Color.magenta()
                )            
                await channel.send(embed=embed)

bot.run('')