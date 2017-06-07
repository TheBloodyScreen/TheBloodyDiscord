from config import token
import sys
import os
import discord
from colorama import Fore
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

sys.path.append(os.path.abspath('.'))
bot = discord.Client()


@bot.event
async def on_ready():
    print(Fore.GREEN + 'Logged in as')
    print(Fore.WHITE + "Name: " + Fore.GREEN + bot.user.name)
    print(Fore.WHITE + "ID: " + Fore.GREEN + bot.user.id)
    print(Fore.WHITE + '________________________')
    print(sys.platform)
    if sys.platform != "win32":
        await bot.change_presence(game=discord.Game(name='!info'))
        print('!info')
    else:
        await bot.change_presence(game=discord.Game(name='!info - indev'))
        print('!info - indev')
    print(Fore.GREEN + "connected successfully")
    print(Fore.WHITE + '________________________')


@bot.event
async def on_message(message):
    author = message.author
    channel = message.channel
    admin = ["Bot Commander", "admins"]
    adminCheck = any(role in admin for role in getRoles(author))
    regularCheck = "Regular" in getRoles(author)
    modCheck = "Moderator" in getRoles(author)
    msg = str(message.content).split(' ')

    if msg[0] == "!info":
        await bot.send_typing(author)
        await bot.send_message(author, embed=discord.Embed(title='Commandlist for TheBloodyDiscord.', description="\n!info\nCauses these messages.\n\n!faq\nPosts a link to the FAQ in the channel it was used in.\n\n!twitch\nPosts a link to the twitch channel in the channel it was used in.", color=0x2AE92A))

    elif msg[0] == "!faq":
        await bot.send_typing(channel)
        await bot.send_message(channel, "The FAQ is currently being worked on. Please come back later!")

    elif msg[0] == "!twitch":
        await bot.send_typing(channel)
        await bot.send_message(channel, "<https://twitch.tv/thebloodyscreen>")


def getRoles(author):
    roles = []
    for role in author.roles:
        roles.append(role.name)
    return roles


bot.run(token)
