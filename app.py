import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from database import create_tables
from commands import Judge, Release, Clean
from utils.embeds import create_error_embed

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'봇이 로그인했습니다: {bot.user.name} (ID: {bot.user.id})')
    logger.info('데이터베이스 테이블 생성 중...')
    await create_tables()
    logger.info('데이터베이스 테이블 생성 완료')
    
    # 명령어 로딩
    logger.info('명령어 로딩 중...')
    await bot.add_cog(Judge(bot))
    logger.info('심판 명령어 로딩 완료')
    await bot.add_cog(Release(bot))
    logger.info('석방 명령어 로딩 완료')
    await bot.add_cog(Clean(bot))
    logger.info('청소 명령어 로딩 완료')
    
    # 로드된 명령어 목록 출력
    logger.info('로드된 명령어 목록:')
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
        logger.error(f'처리되지 않은 오류: {str(error)}')

bot.run(os.getenv('DISCORD_TOKEN')) 