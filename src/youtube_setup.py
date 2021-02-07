import youtube_dl as ytdl
import util
import discord

ytdl_options = {
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist",
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

class Video:
    """Class containing information about a particular video."""
    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        with ytdl.YoutubeDL(ytdl_options) as ydl:
            video = self._get_info(url_or_search)
            video_format = video["formats"][0]
            self.url = video_format["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.length = video["duration"]
            self.thumbnail = video["thumbnail"] if "thumbnail" in video else None
            self.uploader = video["uploader"]
            self.requested_by = requested_by

    def _get_info(self, video_url):
        with ytdl.YoutubeDL(ytdl_options) as ydl:
            
            info = ydl.extract_info(video_url, download = False)
            video = None
            
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            #ydl.prepare_filename(video)
            return video

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=self.title, url=self.video_url, color=discord.Color.dark_magenta(),
            description=f"Length: {util.format_seconds(self.length)}")
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar_url)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed
