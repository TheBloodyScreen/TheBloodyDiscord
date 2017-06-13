
import sys
import discord
from discord.ext import commands
from colorama import Fore
from config import token
from debug import *
import random

description = '''A learning experience bot, written in python using discory.py .'''
bot = commands.Bot(command_prefix='.', description=description)


@bot.event
async def on_ready():
    print(Fore.GREEN + 'Logged in as')
    print(Fore.WHITE + "Name: " + Fore.GREEN + bot.user.name)
    print(Fore.WHITE + "ID: " + Fore.GREEN + bot.user.id)
    print(Fore.WHITE + '________________________')
    debug(sys.platform)
    if sys.platform != "win32":
        await bot.change_presence(game=discord.Game(name='!info'))
        debug('!info')
    else:
        await bot.change_presence(game=discord.Game(name='!info - indev'))
        debug('!info - indev')
    print(Fore.GREEN + "connected successfully")
    print(Fore.WHITE + '________________________')


@bot.command(pass_context=True)
async def info(ctx):
    await bot.delete_message(ctx.message)
    await bot.send_typing(ctx.message.author)
    await bot.send_message(ctx.message.author, embed=discord.Embed(title='Commandlist for TheBloodyDiscord.', description="\n!info\nCauses these messages.\n\n!faq\nPosts a link to the FAQ in the channel it was used in.\n\n!twitch\nPosts a link to the twitch channel in the channel it was used in.", color=0x2AE92A))

@bot.command(pass_context=True)
async def faq(ctx):
    await bot.delete_message(ctx.message)
    await bot.send_typing(ctx.message.channel)
    await bot.send_message(ctx.message.channel, "The FAQ is currently being worked on. Please come back later!")

@bot.command(pass_context=True)
async def twitch(ctx):
    await bot.delete_message(ctx.message)
    await bot.send_typing(ctx.message.channel)
    await bot.send_message(ctx.message.channel, "<https://twitch.tv/thebloodyscreen>")

# everything voice --start
@bot.group(pass_context=True)
async def voice(ctx):
    await bot.delete_message(ctx.message)
    if ctx.invoked_subcommand is None:
        await bot.say('Invalid link or subcommand')

@voice.command(pass_context=True)
async def play(ctx, cmd: str):
    if cmd != None:
        global voice
        voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
        global player
        player = await voice.create_ytdl_player(cmd)
        player.start()
    
    else:
        await bot.say('Please specify a link!')

@voice.command()
async def stop():
    player.stop()
        
@voice.command()
async def leave():
    player.stop()
    await voice.disconnect()
# everything voice --stop

# simple addition
@bot.command()
async def add(first: int, second: int):
    await bot.say(str(first) + '+' + str(second) + ' = ' + str(first + second))

# make simple choices
@bot.command()
async def choose(*choices: str):
    await bot.say(random.choice(choices))

# spam around for a bit
@bot.command(pass_context=True)
async def repeat(ctx, times: int, *, content: str):
    if 'admins' in getRoles(ctx.message.author):
        for i in range(times):
            await bot.say(content)
    else:
         await bot.say("You don't have permission to use this command!")   

# markdown helper
@bot.event
async def on_message(message):
    author = message.author
    if message.content.startswith('CODE') and author.id != '322081774622605312':
        await bot.delete_message(message)
        newMessage = str(message.content).replace("CODE", "```")
        author = str(message.author)
        await bot.send_message(message.channel, "CODE by " + str(author[0:-5]) + newMessage + "\n```")
    await bot.process_commands(message)

def getRoles(author):
    roles = []
    for role in author.roles:
        roles.append(role.name)
    return roles


bot.run(token)
