import discord
from discord import activity 
from discord.ext import commands, tasks
import youtube_dl
from random import choice

client = commands.Bot(command_prefix="!")
status = ["Jamming", "Chilling"]

queue = []

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(choice(status)))
    print("Bot is online!")

@client.command(name="join", help="This commands adds the bot to voice channel")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Bot is not connected to voice channel")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@client.command(name='queue', help='This command adds a song to the queue')
async def queue_(ctx, url):
    global queue
    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')

@client.command(name="remove", help="This command removes a song from the queue")
async def remove(ctx, num):
    global queue
    try:
        del(queue[int(num)])
        await ctx.send('Your queue is now `{queue}!`')
    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')

@client.command(name="play", help="This command plays a song")
async def play(ctx):
    global queue
    server = ctx.message.guild
    voice_channel = server.voice_client
    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send('**Now playing:** {}'.format(player.title))
    del(queue[0])

@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.pause()

@client.command(name='resume', help='This command resumes the song')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.resume()

@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    await ctx.send(f'Your queue is now `{queue}!`')

@client.command(name='leave', help='This command makes the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@client.command(name='stop', help='This command stops the current song')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()

client.run("NzI2OTkyNDU3MzI1MDg0NzU0.XvlWfA.oX5UJSiIF32cOq8hMBMC97lxBSE")