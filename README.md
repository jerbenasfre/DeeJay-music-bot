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

- clear \- Clears the current playlist.

- delete \- Deletes the playlist form database if it exists. Type dj.delete "playlist_name" to use.

- delete_song \- Deletes a song from a playlist. Type dj.delete_song "playlist name" "song name" to use command. Note: "song name" must be the same name that is saved into the playlist.

- edit_playlist \- Edits a playlist name. Type dj.edit "old name" "new name" to use command.

- join \- Joins the voice channel of the requested user.

- leave \- Leaves current voice channel. Note: Current playlist will be lost.

- load \- Retrieves playlist from database if it exists. Type dj.load "playlist name" to use.

- move \- Moves selected song to the top of the playlist. Type dj.move number to move a song.

- pause \- Pauses the bot.

- play \- Searches for video on youtube or plays given url. Type dj.play "url" or "song title" to use. Song title + artist for more accurate results.

- remove \- Removes selected song from the playlist. Type dj.remove number to remove a song.

-- repeat \- Type dj.repeat single, all or off to change repeat mode.

- resume \- Unpauses the bot.

- save \- Binds and saves current playlist to requested user. Type dj.save "playlist name" to save playlist. See dj.load command to load a saved playlist.

- show \- Displays current playlist.

- show_playlist \- Lists the songs of a playlist or lists all playlists a user has. Type dj.show_playlist "playlist name" to show songs or leave "playlist name" blank to show all playlists

- shuffle \- Shuffles the playlist.

- skip \- Skips the current song.

- volume \- Changes the volume of the bot.

Owner only commands:
- dj.sleep \- disconnects the bot from discord. MUST WAIT FOR AT LEAST 10 secs AFTER LEAVING VCS.
- dj.leave_all \- disconnects bot from all voice clients.
