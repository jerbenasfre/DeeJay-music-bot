# DeeJay-music-bot
A simple musicbot written in Discord.py that utilizes YoutubeDL and ffmpeg to stream audio. Use the dj.help command to get a list of commands(or check Commands below)!
I made this bot because the most popular bots at the time did not support saved playlists (or if they did, you had to be a supporter on patreon). 

## Getting Started
1) Go to https://discordapp.com/developers/applications/ and create an application for the discord bot.
2) Get a token under the Bot tab and place in bot.run("token here") in main.py.
3) Invite the bot to your discord server by creating a link in OAuth2.

## Prerequisites
Python 3.7+ 

Discord.py 1.3.0a+

ffmpeg

YoutubeDL

sqlite

## Installing
Go to https://www.python.org/downloads/ to install Python.

Run py -3 -m pip install -U discord.py\[voice\] in command prompt for Windows to get/update Discord.py

Run py -3 -m pip install -U Youtube-dl in command prompt to get/update YoutubeDL.

Run py -3 -m pip install -U buttons in command prompt for pagination for help commands.

Download ffmpeg from https://ffmpeg.org/ffmpeg.html

Place folder into C Drive (or wherever you prefer), and rename it to ffmpeg for reference.

Add path/ffmpeg/bin into your path variables.

Download sqlite from https://sqlitebrowser.org/dl/

## Commands

Commands for bot prefaced with "dj."

- dj.help \- see commands list in discord.
- dj.join \- joins the vc of requested user.
- dj.leave \- leaves current vc. Note, leaving clears the playlist.
- dj.play youtube_url  \- plays video in voice chat. Queues if a song is currently playing.
- dj.pause \- pauses the current song.
- dj.resume \- resumes the current song.
- dj.show \- shows current song and queued songs.
- dj.volume int \- changes the volume of the bot.
- dj.repeat \[single|queue/all|off\] \- Repeats current song or queue or turns repeat off.
- dj.skip int \- skips current song or the nth song.
- dj.move int \- moves the nth song to the top of the playlist.
- dj.remove int \- removes the nth song.
- dj.clear \- clears all songs from guild playlist.
- dj.shuffle \- shuffles the playlist

Owner only commands:
- dj.sleep \- disconnects the bot from discord. MUST WAIT FOR AT LEAST 10 secs AFTER LEAVING VCS.
- dj.leave_all \- disconnects bot from all voice clients.
