# main.py
#
# Driver for deejay bot. Connects bot to discord and loads cogs.
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='dj.', help_command=None, description='Music bot with builtin playlists.')


# on ready to initialize bot
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name='dj.help for list of commands'))
    try:
        bot.load_extension('music')
        bot.load_extension('help')
    except Exception as e:
        print(f'**`ERROR:`** {type(e).__name__} - {e}')
        raise e
    else:
        print('===SUCCESS===')


@bot.command(name='sleep', help='I will go to sleep(go offline)', hidden=True)
@commands.is_owner()
async def sleep(ctx):
    """Must wait at least 10 seconds so bot closes websockets to vc"""
    if len(bot.voice_clients) != 0:
        print('FAILURE: Disconnect from all VC first')
        await ctx.send('FAILURE: Disconnect from all VC first')
    else:
        print('logging out...')
        await bot.close()


# run token
bot.run("NjAyMzc1Mzc5OTUyNTk5MDQx.XTP7yg.iS-5kgP34tU_VcsFbHm6PMlvjiM")
