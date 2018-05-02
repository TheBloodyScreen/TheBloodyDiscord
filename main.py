import sys
import random
import hashlib
import discord
from gtts import gTTS
import pymysql.cursors
from config import config
from colorama import Fore
from bloodyterminal import btext
from discord.ext import commands

description = '''A learning experience bot, written in python using discory.py .'''
bot = commands.Bot(command_prefix='.', description=description)


@bot.event
async def on_ready():
    btext.info('Logged in as')
    btext.info('Name: ' + Fore.GREEN + bot.user.name)
    btext.info("ID: " + Fore.GREEN + bot.user.id)
    btext.info('________________________')
    btext.info(sys.platform)
    if sys.platform != "win32":
        await bot.change_presence(game=discord.Game(name='.info', url="https://twitch.tv/TheBloodyScreen", type=1))
        btext.success("game set successfully")
    else:
        await bot.change_presence(game=discord.Game(name='.info - indev', url="https://twitch.tv/TheBloodyScreen", type=1))
        btext.success("game set successfully")
    btext.success("connected successfully")
    btext.info('________________________')


@bot.command(pass_context=True)
async def info(ctx):
    await bot.delete_message(ctx.message)
    await bot.send_typing(ctx.message.author)
    await bot.send_message(ctx.message.author, embed=discord.Embed(title='list of commands for TheBloodyDiscord.',
                                                                   description="\n!info\nCauses these messages."
                                                                               "\n\n!faq\nPosts a link to the FAQ in the channel it was used in."
                                                                               "\n\n!twitch\nPosts a link to the twitch channel in the channel it was used in."
                                                                               "\n\nIf the bot says 'Playing .info - indev' I am currently working on the bot and there might be problems while using commands.",
                                                                   color=0x2AE92A))


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
        ttos = gTTS(text=str(ctx.message.content).replace('.voice tts ', ''), lang='en')
        ttos.save('./audio/tts.mp3')
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
async def wirsindgeil(ctx):
    global voice
    voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
    global player
    player = voice.create_ffmpeg_player('./audio/music.mp3')
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


# It's like "the purge," Morty. You know that movie "the purge"?
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
    connection = pymysql.connect(host=config['database']['discord']['host'],
                                 user=config['database']['discord']['user'],
                                 password=config['database']['discord']['pass'],
                                 db=config['database']['discord']['db'],
                                 charset=config['database']['discord']['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT TABLE_NAME AS 'Table Name', TABLE_ROWS AS 'Rows' FROM information_schema.TABLES WHERE TABLES.TABLE_SCHEMA = 'TheBloodyDiscord' AND TABLES.TABLE_TYPE = 'BASE TABLE'"
            cursor.execute(sql)
            maxid = (str(cursor.fetchall()[0]).replace("{'Table Name': 'quotes', 'Rows': ", '')).replace('}', '')
            sql = "SELECT `quote` FROM `quotes` WHERE `id`=%s"
            cursor.execute(sql, (random.randint(1, int(maxid))))
            result = (str(cursor.fetchone()).replace("{'quote': ", '')).replace('}', '')
            await bot.say(result)
    finally:
        connection.close()


@bot.command(pass_context=True)
async def qamount(ctx):
    await bot.delete_message(ctx.message)
    connection = pymysql.connect(host=config['database']['discord']['host'],
                                 user=config['database']['discord']['user'],
                                 password=config['database']['discord']['pass'],
                                 db=config['database']['discord']['db'],
                                 charset=config['database']['discord']['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT TABLE_NAME AS 'Table Name', TABLE_ROWS AS 'Rows' FROM information_schema.TABLES WHERE TABLES.TABLE_SCHEMA = 'TheBloodyDiscord' AND TABLES.TABLE_TYPE = 'BASE TABLE'"
            cursor.execute(sql)
            maxid = (str(cursor.fetchall()[0]).replace("{'Table Name': 'quotes', 'Rows': ", '')).replace('}', '')
            await bot.say(str(maxid))
    finally:
        connection.close()


@bot.command(pass_context=True)
async def quoteid(ctx):
    await bot.delete_message(ctx.message)
    connection = pymysql.connect(host=config['database']['discord']['host'],
                                 user=config['database']['discord']['user'],
                                 password=config['database']['discord']['pass'],
                                 db=config['database']['discord']['db'],
                                 charset=config['database']['discord']['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

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
    connection = pymysql.connect(host=config['database']['discord']['host'],
                                 user=config['database']['discord']['user'],
                                 password=config['database']['discord']['pass'],
                                 db=config['database']['discord']['db'],
                                 charset=config['database']['discord']['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `quotes` (`quote`) VALUES (%s)"
            message = str(ctx.message.content).replace('.addquote ', '')
            cursor.execute(sql, message,)
        connection.commit()
    finally:
        connection.close()


# wow account stuff
@bot.group(pass_context=True)
async def account(ctx):
    channel = ctx.message.channel

    if ctx.invoked_subcommand is None:
        if str(channel.type) != 'private':
            await bot.say('invalid link or subcommand')
            await bot.say('Also: these commands only work in private chats with me')


@account.command(pass_context=True)
async def create(ctx):
    connection = pymysql.connect(host=config['database']['trinity']['host'],
                                 user=config['database']['trinity']['user'],
                                 password=config['database']['trinity']['pass'],
                                 db=config['database']['trinity']['db'],
                                 cursorclass=pymysql.cursors.DictCursor)
    message = ctx.message.content.split()
    hexhash = hashlib.sha1((message[2] + ':' + message[3]).upper().encode('utf-8')).hexdigest()
    if "--" in ctx.message.content:
        await bot.say('You used illegal characters. Please try again!')
        pass
    else:
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `account` (`username`, `sha_pass_hash`, `expansion`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (message[2].upper(), hexhash.upper(), 2))
            connection.commit()
            await bot.say("account created! you should now be able to login to the server")
            await bot.say("remember to set the realmlist to thebloodyscreen.com")
        except:
            await bot.say("the account creation seems to have failed, please contact TheBloodyScreen!")
        finally:
            connection.close()


@account.command(pass_context=True)
async def delete(ctx):
    connection = pymysql.connect(host=config['database']['trinity']['host'],
                                 user=config['database']['trinity']['user'],
                                 password=config['database']['trinity']['pass'],
                                 db=config['database']['trinity']['db'],
                                 cursorclass=pymysql.cursors.DictCursor)
    message = ctx.message.content.split()

    if "--" in ctx.message.content:
        await bot.say('You used illegal characters. Please try again!')
        pass
    else:
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM `account` WHERE username = %s AND sha_pass_hash = %s"
                btext.debug(hashlib.sha1((message[2] + ':' + message[3]).upper().encode('utf-8')).hexdigest().upper())
                cursor.execute(sql, (message[2].upper(), hashlib.sha1((message[2] + ':' + message[3]).upper().encode('utf-8')).hexdigest().upper()))
            connection.commit()
            await bot.say("account deleted! THIS IS NOT REVERSABLE!")
        except pymysql.Error as e:
            btext.debug(str(e))
            await bot.say("the account deletion seems to have failed, please contact TheBloodyScreen!")
        finally:
            connection.close()


@account.command(pass_context=True)
async def help(ctx):
    channel = ctx.message.channel
    if str(channel.type) == 'private':
        await bot.send_message(ctx.message.author, embed=discord.Embed(title='TheBloodyLichKing Help', description="""\nThe available subcommands are:
                                                                                                                      \n\nhelp\ndisplays this message
                                                                                                                      \n\ncreate name password\ntries to create server account: 'name' with password 'password'
                                                                                                                      \n\ndelete name password\ntries to delete server account: 'name' with password 'password(NOT YET IMPLEMENTED)'
                                                                                                                      \n\nExample:
                                                                                                                      \n.account create testname testpassword""", color=0x2900AD))
    else:
        await bot.say('DO NOT use these commands in public channels! Please PM me!')


# markdown helper
@bot.event
async def on_message(message):
    author = message.author
    bot.get_all_emojis()

    if message.content.startswith('CODE') and message.author != 'TheBloodyDiscord#6405' and message.author.id != '322081774622605312' and message.author.id != '385007074863480832':
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
        await bot.send_message(message.channel, "<:titcart:234430485437218829>")
    elif message.content.find('ALLEMOJIS') >= 0:
        for emoji in bot.get_all_emojis():
            await bot.add_reaction(message, emoji)
    elif message.content.startswith("<@322081774622605312>"):
        await bot.send_message(message.channel, "\n%s\nI'm having a hard time replying to mentions.\nPlease use !info." % author.mention)

    await bot.process_commands(message)


def getRoles(author):
    roles = []
    for role in author.roles:
        roles.append(role.name)
    return roles


bot.run(config['discord']['token'])
