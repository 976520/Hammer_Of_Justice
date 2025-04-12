import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from database import create_tables
from commands import Judge, Release, Clean
from utils.embeds import create_error_embed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    await create_tables()
    logger.info('OKAY')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'member':
            await ctx.send(embed=create_error_embed("멤버 파라미터 없음"))
        elif error.param.name == 'reason':
            await ctx.send(embed=create_error_embed("사유 파라미터 없음"))
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(embed=create_error_embed("멤버 낫파운드"))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=create_error_embed("권한 없음"))

async def setup():
    await bot.add_cog(Judge(bot))
    await bot.add_cog(Release(bot))
    await bot.add_cog(Clean(bot))

bot.run(os.getenv('DISCORD_TOKEN')) 