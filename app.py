import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from database import create_tables
from commands import Judge, Release, Clean
from utils.embeds import create_error_embed

# 로깅 설정
log_file = os.path.join(os.getcwd(), 'bot.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'심판의 망치 등장: {bot.user.name} (ID: {bot.user.id})')
    await create_tables()
    
    await bot.add_cog(Judge(bot))
    await bot.add_cog(Release(bot))
    await bot.add_cog(Clean(bot))
    
    logger.info('bot.commands:')
    for command in bot.commands:
        logger.info(f'- {command.name}')

@bot.event
async def on_command_error(ctx, error):
    logger.error(f'명령어 오류 발생: {str(error)}')
    if isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'member':
            await ctx.send(embed=create_error_embed("멤버 파라미터 없음"))
        elif error.param.name == 'reason':
            await ctx.send(embed=create_error_embed("사유 파라미터 없음"))
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(embed=create_error_embed("멤버 낫파운드"))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=create_error_embed("권한 없음"))
    else:
        logger.error({str(error)})

bot.run(os.getenv('DISCORD_TOKEN')) 