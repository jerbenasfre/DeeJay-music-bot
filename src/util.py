# util.py
#
# Contains simple helper methods

import discord
from discord.ext.buttons import Paginator

class Page(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_restrictions()
        except discored.HTTPException:
            pass
            

def format_seconds(time_seconds):
    """Formats some number of seconds into a string of format d days, x hours, y minutes, z seconds"""
    seconds = time_seconds
    hours = 0
    minutes = 0

    while seconds >= 60:
        if seconds >= 60 * 60:
            seconds -= 60 * 60
            hours += 1
        elif seconds >= 60:
            seconds -= 60
            minutes += 1

    return f"{hours}h {minutes}m {seconds}s"
