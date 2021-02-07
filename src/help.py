# help.py
#
# Help menu for the bot. Lists out all the commands users can use.

import discord
from discord.ext import commands


class Help(commands.Cog, name='Help'):
    """Help formatter"""
    
    def __init__(self,bot):
        self.bot = bot

    async def setup_help(self, ctx, entity=None, title=None):
        entity = entity or self.bot
        title = title or self.bot.description

        pages = []

        if isinstance(entity, commands.Command):
            filtered_comands = (
                list(set(entityall_commands.values()))

                if hasattr(entity,"all_commands")
                else []
            )

    @commands.command(hidden=True)
    async def help(self, ctx, *, entity=None):
        #if not entity:
        #    await self.setup_help(ctx)

        
        embed = discord.Embed(title='**Commands**')
        cog_info = ''
        for command in sorted(self.bot.commands, key=lambda x: x.name):
            if not command.hidden:
                cog_info += f'**{command.name}** - {command.help}\n\n'
        embed.description = cog_info

        await ctx.send(embed=embed)
            
def setup(bot):
    bot.add_cog(Help(bot))
