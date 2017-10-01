import sys
import config
import random
import discord
from gtts import gTTS
import pymysql.cursors
from colorama import Fore
from debug import dbprint
from discord.ext import commands
from TwitterAPI import TwitterAPI

api = TwitterAPI(config.appKey, config.appSecret, config.oauthToken, config.oauthTokenSecret)
description = '''A learning experience bot, written in python using discory.py .'''
bot = commands.Bot(command_prefix='.', description=description)


@bot.event
async def on_ready():
    dbprint('success', 'Logged in as')
    dbprint('info', "Name: " + Fore.GREEN + bot.user.name)
    dbprint('info', "ID: " + Fore.GREEN + bot.user.id)
    dbprint('info', '________________________')
    dbprint('info', sys.platform)
    if sys.platform != "win32":
        await bot.change_presence(game=discord.Game(name='.info'))
    else:
        await bot.change_presence(game=discord.Game(name='.info - indev'))
    dbprint('success', "connected successfully")
    dbprint('info', '________________________')


@bot.command(pass_context=True)
async def info(ctx):
    await bot.delete_message(ctx.message)
    await bot.send_typing(ctx.message.author)
    await bot.send_message(ctx.message.author, embed=discord.Embed(title='Commandlist for TheBloodyDiscord.', description="\n!info\nCauses these messages.\n\n!faq\nPosts a link to the FAQ in the channel it was used in.\n\n!twitch\nPosts a link to the twitch channel in the channel it was used in.\n\nIf the bot says 'Playing .info - indev' I am currently working on the bot and there might be problems while using commands.", color=0x2AE92A))


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
# simple shit above


# everything voice --begin
@bot.group(pass_context=True)
async def voice(ctx):
    await bot.delete_message(ctx.message)
    if ctx.invoked_subcommand is None:
        await bot.say('Invalid link or subcommand')


@voice.command(pass_context=True)
async def play(ctx, cmd: str):
    if cmd:
        global voice
        voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
        global player
        player = await voice.create_ytdl_player(cmd)
        player.start()
        check = True
        while check is True:
            if player.is_done():
                await voice.disconnect()
                check = False

    else:
        await bot.say('Please specify a link!')


@voice.command(pass_context=True)
async def tts(ctx, cmd: str):
    if cmd:
        tts = gTTS(text=str(ctx.message.content).replace('.voice tts ', ''), lang='en')
        tts.save('./audio/tts.mp3')
        global voice
        voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
        global player
        player = voice.create_ffmpeg_player('./audio/tts.mp3')
        player.start()
        check = True
        while check is True:
            if player.is_done():
                await voice.disconnect()
                check = False

        else:
            await bot.say('Please specify a message!')


@voice.command(pass_context=True)
async def rimshot(ctx):
    global voice
    voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
    global player
    player = voice.create_ffmpeg_player('./audio/rimshot.mp3')
    player.start()
    check = True
    while check is True:
        if player.is_done():
            await voice.disconnect()
            check = False


@voice.command(pass_context=True)
async def alarm(ctx):
    global voice
    voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
    global player
    player = voice.create_ffmpeg_player('./audio/alarm.mp3')
    player.start()
    check = True
    while check is True:
        if player.is_done():
            await voice.disconnect()
            check = False


@voice.command()
async def stop():
    player.stop()


@voice.command()
async def leave():
    player.stop()
    await voice.disconnect()
# everything voice --end


# simple twitter post command
@bot.command(pass_context=True)
async def tweet(ctx):
    await bot.delete_message(ctx.message)
    if str(ctx.message.author) == 'TheBloodyScreen#4278':
        r = api.request('statuses/update', {'status': ctx.message.content.replace('.tweet ', '')})
        await bot.send_message(ctx.message.author, 'SUCCESS' if r.status_code == 200 else 'FAILURE')
    else:
        await bot.say("You don't have permission to use this command!")


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
    await bot.delete_message(ctx.message)
    if 'admins' in getRoles(ctx.message.author):
        for i in range(times):
            await bot.say(content)
    else:
        await bot.say("You don't have permission to use this command!")


# It's like "the purge," Morty. That movie "the purge"?
@bot.command(pass_context=True)
async def purge(ctx, amount):
    if 'admins' in getRoles(ctx.message.author):
        try:
            await bot.delete_message(ctx.message)
            await bot.purge_from(ctx.message.channel, limit=int(amount))
        except:
            await bot.delete_message(ctx.message)
            await bot.say(ctx.message.channel, "Please provide an int!")
    else:
        await bot.delete_message(ctx.message)
        await bot.say(ctx.message.channel, "You don't have permission to use this command!")


# show me what you got
@bot.command(pass_context=True)
async def roles(ctx):
    for server in bot.servers:
        for member in server.members:
            if member.mentioned_in(ctx.message):
                user = member
    await bot.send_message(ctx.message.channel, embed=discord.Embed(title=str(str(user)[0:-5]) + ' has the following Groups:', description=("\n".join(getRoles(user))), color=0x0000FF))


# tell me something fun
@bot.command(pass_context=True)
async def quote(ctx):
    await bot.delete_message(ctx.message)
    connection = pymysql.connect(host=config.host, user=config.user, password=config.password, db=config.db, charset=config.charset, cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT TABLE_NAME AS 'Table Name', TABLE_ROWS AS 'Rows' FROM information_schema.TABLES WHERE TABLES.TABLE_SCHEMA = 'TheBloodyDiscord' AND TABLES.TABLE_TYPE = 'BASE TABLE'"
            cursor.execute(sql)
            maxid = (str(cursor.fetchall()[0]).replace("{'Table Name': 'quotes', 'Rows': ", '')).replace('}', '')
            sql = "SELECT `quote` FROM `quotes` WHERE `id`=%s"
            cursor.execute(sql, (random.randint(1, int(maxid))))
            result = (str(cursor.fetchone()).replace("{'quote': ", '')).replace('}', '')
            dbprint('info', result)
            await bot.say(result)
    finally:
        connection.close()


@bot.command(pass_context=True)
async def quoteid(ctx):
    await bot.delete_message(ctx.message)
    connection = pymysql.connect(host=config.host, user=config.user, password=config.password, db=config.db, charset=config.charset, cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT `quote` FROM `quotes` WHERE `id`=%s"
            cursor.execute(sql, int(str(ctx.message.content).replace('.quoteid ', '')))
            result = (str(cursor.fetchone()).replace("{'quote': '", '')).replace("'}", "")
            await bot.say(result)
    finally:
        connection.close()


@bot.command(pass_context=True)
async def addquote(ctx):
    await bot.delete_message(ctx.message)
    connection = pymysql.connect(host=config.host, user=config.user, password=config.password, db=config.db, charset=config.charset, cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `quotes` (`quote`) VALUES (%s)"
            message = str(ctx.message.content).replace('.addquote ', '')
            cursor.execute(sql, message,)
        connection.commit()
    finally:
        connection.close()


# markdown helper
@bot.event
async def on_message(message):
    author = message.author
    bot.get_all_emojis()

    if message.content.startswith('CODE') and message.author != 'TheBloodyDiscord#6405' and message.author.id != '322081774622605312':
        author = str(message.author)
        await bot.delete_message(message)
        newMessage = str(message.content).replace("CODE", "```")
        await bot.send_message(message.channel, "CODE by " + str(author[0:-5]) + newMessage + "\n```")
    elif message.content.find('deadmau5') >= 0:
        await bot.add_reaction(message, ":deadmau5:230176271135408130")
    elif message.content.find('penis') >= 0:
        await bot.add_reaction(message, ":penis:232019776904364033")
    elif message.content.find('vagina') >= 0:
        await bot.add_reaction(message, ":vagina:234426457068273664")
    elif message.content.find('boob') >= 0:
        await bot.add_reaction(message, ":titcart:234430485437218829")
    elif message.content.find('ALLEMOJIS') >= 0:
        for emoji in bot.get_all_emojis():
            await bot.add_reaction(message, emoji)
    await bot.process_commands(message)


def getRoles(author):
    roles = []
    for role in author.roles:
        roles.append(role.name)
    return roles


bot.run(config.token)
