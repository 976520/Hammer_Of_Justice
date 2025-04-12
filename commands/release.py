import discord
from discord.ext import commands
import logging
from database import get_user_count
from utils.embeds import create_success_embed, create_error_embed

logger = logging.getLogger(__name__)

class Release(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='석방')
    @commands.has_permissions(moderate_members=True)
    async def release(self, ctx, member: discord.Member):
        logger.info(f"석방 명령어 실행 - 서버: {ctx.guild.name}, 실행자: {ctx.author.name}, 대상: {member.name}")
        
        user_id = str(member.id)
        server_id = str(ctx.guild.id)
        count = await get_user_count(user_id, server_id)
        logger.info(f"사용자 전과 횟수 조회 - 사용자: {member.name}, 전과: {count}회")

        try:
            await member.timeout(None)
            logger.info(f"타임아웃 해제 성공 - 사용자: {member.name}")
            
            embed = create_success_embed(
                title="🕊️ 석방",
                description=f"전과 {count}범 {member.mention}를 석방했습니다.",
                footer=f"by {ctx.author.display_name}"
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            logger.error(f"타임아웃 해제 실패 (권한 없음) - 사용자: {member.name}")
            await ctx.send(embed=create_error_embed("봇 권한 이슈"))
        except Exception as e:
            logger.error(f"타임아웃 해제 중 오류 발생 - 사용자: {member.name}, 오류: {str(e)}")
            await ctx.send(embed=create_error_embed(str(e)))

async def setup(bot):
    await bot.add_cog(Release(bot)) 