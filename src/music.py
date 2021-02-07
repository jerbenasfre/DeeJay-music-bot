# music.py
#
# Contains all the music related commands for deejay.py
import discord
import util
import youtube_dl
import playlist_db

from discord.ext import commands
from youtube_setup import Video
from enum import Enum
from collections import deque
import random

ffmpeg_options = {
    'options': '-vn'
}


class Repeat(Enum):
    OFF = 1
    SINGLE = 2
    ALL = 3


class GuildInfo:
    """Contains information for a guild voice client"""

    def __init__(self):
        self.playlist = deque()
        self.current_song = None
        self.repeat = Repeat.OFF


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}  # used to store song playlists for a guild

    @commands.command(help='Joins the voice channel of the requested user.')
    async def join(self, ctx):
        """Joins the voice channel requested user is in"""
        if ctx.guild not in self.guilds:
            self.guilds[ctx.guild] = GuildInfo()

        # If user is in a voice channel
        if ctx.author.voice is not None:
            # If the bot is in a different voice channel, move it to the same channel as user
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(ctx.author.voice.channel)
            else:
                await ctx.author.voice.channel.connect()

            # Checks to see if bot failed to connect (One reason being no permission to join voice channel)
            if ctx.voice_client is None or not ctx.voice_client.is_connected():
                await ctx.send('I failed to join the voice channel. Please ensure I have permission to join enabled.')
        else:
            await ctx.send("You must be in a voice channel for me to join.")

    @commands.command(help='Leaves current voice channel. **Note:** Current playlist will be lost.')
    async def leave(self, ctx):
        """Leaves current voice channel, if applicable"""
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            guild = self.guilds[ctx.guild]
            if guild.current_song is not None:
                guild.current_song = None
                guild.playlist.clear()
                guild.repeat = Repeat.OFF

            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def leave_all(self, ctx):
        """Makes bot leave all connected VCs"""
        for vc in self.bot.voice_clients:
            vc.stop()
            await vc.disconnect()

    @commands.command(aliases=['s', 'list'], help='Displays current playlist.')
    async def show(self, ctx):
        if ctx.guild not in self.guilds or self.guilds[ctx.guild].current_song is None:
            await ctx.send('No songs are playing or queued.')
            return

        guild = self.guilds[ctx.guild]

        if guild.current_song is not None:
            await ctx.send(f"**Repeat:** `{str(guild.repeat)[7:]}`")
            await ctx.send('**Now playing:** ' + guild.current_song.title)

            if len(guild.playlist) > 0:
                embed = discord.Embed(color=discord.Color.dark_magenta())
                embed.title = '**Queued:**\n'
                embed.description = ''
                total_length = guild.current_song.length
                for number, video in zip(range(1, len(guild.playlist) + 1), guild.playlist):
                    embed.description += f"**{str(number)})** `{video.title}`"
                    embed.description += f"\n **Requested** by {video.requested_by.name} **Length** [{util.format_seconds(video.length)}]\n\n "
                    total_length += video.length

                embed.description += f"**Total Length**: `[{util.format_seconds(total_length)}]`"
                await ctx.send(embed=embed)

    @commands.command(aliases=['loop'], help="Type `dj.repeat single, all or off` to change repeat mode.")
    async def repeat(self, ctx, repeat_toggle=None):
        if ctx.guild not in self.guilds:
            self.guilds[ctx.guild] = GuildInfo()

        if repeat_toggle == 'single':
            self.guilds[ctx.guild].repeat = Repeat.SINGLE
            await ctx.send('Repeating current song.')

        elif repeat_toggle == 'all':
            self.guilds[ctx.guild].repeat = Repeat.ALL
            await ctx.send('Repeating playlist.')

        elif repeat_toggle == 'off':
            self.guilds[ctx.guild].repeat = Repeat.OFF
            await ctx.send('Repeat turned off.')

        else:
            await ctx.send('Type `dj.repeat single` to repeat current song\n' +
                           'Type `dj.repeat all` to repeat whole playlist\n' +
                           'Type `dj.repeat off` to turn off repeat.')

    @commands.command(
        help="Searches for video on youtube or plays given url. Type `dj.play \"url\" or \"song title\"` to use. Song "
             "title + artist for more accurate results.")
    async def play(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""
        print("THIS IS THE URL")
        print(url)

        guild = self.guilds[ctx.guild]
        if guild.current_song is not None:  # Append to playlist.
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                await ctx.send('There was an error downloading your video, sorry.')
                return

            guild.playlist.append(video)
            e = video.get_embed()
            e.description += f'\nPosition in playlist: {len(guild.playlist)}'
            await ctx.send(f"Added to playlist.", embed=e)

        else:  # Play song.
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                await ctx.send('There was an error downloading your video, sorry.')
                return

            guild.current_song = video
            self._play_song(video, ctx.voice_client, guild)
            await ctx.send("", embed=video.get_embed())

    def _play_song(self, song, voice_client, guild):
        """Handles streaming the song to the VC"""
        source = discord.FFmpegPCMAudio(song.url, executable="C:/ffmpeg/bin/ffmpeg.exe", **ffmpeg_options,
                                        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

        def after_playing(err):
            if guild.repeat == Repeat.SINGLE:
                self._play_song(guild.current_song, voice_client, guild)

            elif len(guild.playlist) > 0:
                if guild.repeat == Repeat.OFF:
                    guild.current_song = guild.playlist.popleft()
                    self._play_song(guild.current_song, voice_client, guild)

                elif guild.repeat == Repeat.ALL:
                    guild.playlist.append(guild.current_song)
                    guild.current_song = guild.playlist.popleft()
                    self._play_song(guild.current_song, voice_client, guild)
            else:
                guild.current_song = None

        voice_client.play(source, after=after_playing)

    @commands.command(aliases=['vol'], help='Changes the volume of the bot.')
    async def volume(self, ctx, volume):
        """Changes the player's volume"""
        try:
            volume = int(volume)
        except ValueError as e:
            await ctx.send('Must be a whole number')
            raise e

        if ctx.voice_client is None:
            return await ctx.send('Not connected to a voice channel.')

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command(aliases=['stop'], help='Pauses the bot.')
    async def pause(self, ctx):
        """Pauses music"""
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            if ctx.voice_client.channel != ctx.author.voice.channel:
                return await ctx.send('You must be in the same voice channel to use this command.')

            ctx.voice_client.pause()
            await ctx.send('Song paused. Type `dj.resume` to resume song.')

    @commands.command(help='Unpauses the bot.')
    async def resume(self, ctx):
        """Resumes music, if paused"""
        if ctx.voice_client is not None and ctx.voice_client.is_paused():
            if ctx.voice_client.channel != ctx.author.voice.channel:
                return await ctx.send('You must be in the same voice channel to use this command.')

            ctx.voice_client.resume()
            await ctx.send('Resuming song. Type `dj.pause` to pause song.')

    @commands.command(help='Skips the current song.')
    async def skip(self, ctx):
        """Skips the current song"""
        guild = self.guilds[ctx.guild]

        if guild.current_song is not None:
            await ctx.send(f'Skipping `{guild.current_song.title}`.')
            ctx.voice_client.stop()
        else:
            await ctx.send('There are no songs to skip.')

    @commands.command(help='Clears the current playlist.')
    async def clear(self, ctx):
        """Clears all songs on guild playlist."""
        ctx.voice_client.pause()
        self.guilds[ctx.guild].current_song = None
        await ctx.send('Clearing playlist.')
        self.guilds[ctx.guild].playlist.clear()
        ctx.voice_client.stop()

    @commands.command(help="Removes selected song from the playlist. Type `dj.remove number` to remove a song.")
    async def remove(self, ctx, index):
        """Removes a song from the nth position of a playlist"""
        guild = self.guilds[ctx.guild]
        try:
            index = int(index)
        except ValueError as e:
            await ctx.send('Must be a whole number.')
            raise e

        if len(guild.playlist) == 0:
            return await ctx.send('There are no songs to remove.')

        index = int(index) - 1

        if index < 0:
            await ctx.send('Number must be >= 1')
        elif index >= len(guild.playlist):
            await ctx.send(f'Number must be <= size of playlist: {len(guild.playlist)}')
        else:
            removed_song = guild.playlist[index]
            del guild.playlist[index]
            await ctx.send(f"`{removed_song.title}` has been removed.")

    @commands.command(help="Moves selected song to the top of the playlist. Type `dj.move number` to move a song.")
    async def move(self, ctx, index):
        """Moves a song to the top of playlist"""
        try:
            index = int(index)
        except ValueError as e:
            await ctx.send('Must be a whole number.')
            raise e

        guild = self.guilds[ctx.guild]
        index = int(index) - 1

        if len(guild.playlist) == 0:
            return await ctx.send('There are no songs to move up.')

        if index < 1:
            return await ctx.send('The song is already at the top of the list')
        if index > len(guild.playlist):
            return await ctx.send('Invalid position.')

        await ctx.send(f"Moving `{guild.playlist[index].title}` to the top.")
        guild.playlist.appendleft(guild.playlist[index])
        del guild.playlist[index + 1]

    @commands.command(help='Shuffles the playlist.')
    async def shuffle(self, ctx):
        """Shuffles the playlist."""
        if ctx.guild not in self.guilds or len(self.guilds[ctx.guild].playlist) == 0:
            return await ctx.send('There is nothing to shuffle.')

        guild = self.guilds[ctx.guild]

        random.shuffle(guild.playlist)
        await ctx.send('Shuffling playlist.')

    @commands.command(
        help="Binds and saves current playlist to requested user. Type `dj.save \"playlist name\"` to save playlist. "
             "See `dj.load` command to load a saved playlist.")
    async def save(self, ctx):
        """Writes playlist to deejay.db"""
        if ctx.guild not in self.guilds:
            self.guilds[ctx.guild] = GuildInfo()

        if self.guilds[ctx.guild].current_song is None:
            return await ctx.send('There is nothing to save.')

        playlist_name = ctx.message.content[8:]  # removes 'dj.save '

        if playlist_name is None or not all(x.isalnum() or x.isspace() for x in playlist_name) or playlist_name == '':
            return await ctx.send('You need to specify a valid playlist name.(Alphanumeric only)')

        songs = deque(self.guilds[ctx.guild].playlist)
        songs.appendleft(self.guilds[ctx.guild].current_song)

        await playlist_db.save(ctx, playlist_name, songs)

        await ctx.send('Songs saved.')

    @commands.command(help="Retrieves playlist from database if it exists. Type `dj.load \"playlist name\"` to use.")
    async def load(self, ctx):
        """Loads playlist from deejay.db. Must be in a voice channel."""
        playlist_name = ctx.message.content[8:]  # removes 'dj.load '

        if playlist_name is None or not all(x.isalnum() or x.isspace() for x in playlist_name) or playlist_name == '':
            return await ctx.send('You need to specify a valid playlist name.(Alphanumeric only)')

        playlist = await playlist_db.load(ctx, playlist_name)
        guild = self.guilds[ctx.guild]

        if playlist is not None:
            for song_info in playlist:
                if guild.current_song is not None:  # Add to playlist.
                    try:
                        video = Video(f'{song_info[0]} {song_info[1]}', ctx.author)
                    except youtube_dl.DownloadError as e:
                        return await ctx.send('There was an error downloading your video, sorry.')

                    guild.playlist.append(video)
                    e = video.get_embed()
                    e.description += f'\nPosition in playlist: {len(guild.playlist)}'
                    await ctx.send(f"Added to playlist.", embed=e)

                else:  # Play song.
                    try:
                        video = Video(f'{song_info[0]} {song_info[1]}', ctx.author)
                    except youtube_dl.DownloadError as e:
                        return await ctx.send('There was an error downloading your video, sorry.')

                    guild.current_song = video
                    self._play_song(video, ctx.voice_client, guild)
                    await ctx.send("", embed=video.get_embed())

    @commands.command(help="Deletes the playlist form database if it exists. Type `dj.delete \"playlist_name\"` to use.")
    async def delete(self, ctx):
        playlist_name = ctx.message.content[10:]  # removes 'dj.delete '

        if playlist_name is None or not all(x.isalnum() or x.isspace() for x in playlist_name) or playlist_name == '':
            return await ctx.send('You need to specify a valid playlist name.(Alphanumeric only)')

        if await playlist_db.delete_playlist(ctx, playlist_name):
            return await ctx.send(f"Playlist `{playlist_name}` deleted.")

    @commands.command(help="Edits a playlist name. Type `dj.edit \"old name\" \"new name\"` to use command.")
    async def edit_playlist(self, ctx):
        try:
            old_name, new_name = ctx.message.content[17:].split(
                ' | ')  # removes dj.edit_playlist and splits content into two.
        except ValueError:
            return await ctx.send("Type `dj.edit \"old name\" \"new name\"` to use command.")

        if old_name is None or not all(x.isalnum() or x.isspace() for x in old_name) or old_name == '':
            return await ctx.send('You need to specify a valid playlist name for old_name.(Alphanumeric only)')

        if new_name is None or not all(x.isalnum() or x.isspace() for x in new_name) or new_name == '':
            return await ctx.send('You need to specify a valid playlist name for new_name.(Alphanumeric only)')

        if await playlist_db.edit_playlist(ctx, old_name, new_name):
            await ctx.send(f"Playlist edited from `{old_name} to {new_name}`")

    @commands.command(
        help="Lists the songs of a playlist or lists all playlists a user has. Type `dj.show_playlist "
             "\"playlist name\"` to show songs or leave `\"playlist name\"` blank to show all playlists")
    async def show_playlist(self, ctx):
        playlist_name = ctx.message.content[17:]

        if playlist_name == '':
            playlists = await playlist_db.list_playlists(ctx)

            embed = discord.Embed(title=f"{ctx.author.name}'s Playlists", color=discord.Color.dark_magenta())
            embed.description = ''
            for playlist in playlists:
                embed.description += f'{playlist[0]}\n'

            return await ctx.send(embed=embed)

        if not all(x.isalnum() or x.isspace() for x in playlist_name) or playlist_name == '':
            return await ctx.send('You need to specify a valid playlist name.(Alphanumeric only)')

        playlist = await playlist_db.load(ctx, playlist_name)
        if playlist is not None:
            embed = discord.Embed(title=playlist_name, color=discord.Color.dark_magenta())
            embed.description = ''
            for song_info in playlist:
                embed.description += f"`{song_info[0]}`\n"

            return await ctx.send(embed=embed)

    @commands.command(
        help="Deletes a song from a playlist. Type `dj.delete_song \"playlist name\" \"song name\"` to use command."
             + " **Note:** \"song name\" must be the same name that is saved into the playlist.")
    async def delete_song(self, ctx):
        msg = ctx.message.content[15:]  # Removes 'dj.delete_song'

        try:
            playlist_name, song_name = msg.split(' | ')
        except ValueError:
            return await ctx.send("Type `dj.delete_song \"playlist name\" \"song_name\"` to use command.")

        if await playlist_db.delete_song(ctx, playlist_name, song_name):
            return await ctx.send(f"`{song_name}` has been deleted from `{playlist_name}`")

    @play.before_invoke
    @repeat.before_invoke
    @remove.before_invoke
    @move.before_invoke
    @clear.before_invoke
    @skip.before_invoke
    @load.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send('You are not connected to a voice channel.')
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.author.voice and ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.send('You must be in the same voice channel. To use this command.')
            raise commands.CommandError("Author not connected to the same voice channel.")
        if ctx.guild not in self.guilds:
            self.guilds[ctx.guild] = GuildInfo()


def setup(bot):
    bot.add_cog(Music(bot))
