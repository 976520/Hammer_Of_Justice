import discord
from discord.ext import commands
import datetime
import logging
from database import get_user_count, update_user_count
from utils.embeds import create_warning_embed, create_error_embed

logger = logging.getLogger(__name__)

class Judge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='심판')
    @commands.has_permissions(moderate_members=True)  
    async def judge(self, ctx, member: discord.Member, *, reason: str = "없"):
        logger.info(f"심판 명령어 실행 - 서버: {ctx.guild.name}, 실행자: {ctx.author.name}, 대상: {member.name}, 사유: {reason}")
        
        user_id = str(member.id)
        server_id = str(ctx.guild.id)
        
        count = await get_user_count(user_id, server_id) + 1
        logger.info(f"사용자 전과 횟수 조회 - 사용자: {member.name}, 전과: {count}회")
        
        await update_user_count(user_id, server_id, count)
        
        if count <= 3:
            timeout_duration = datetime.timedelta(minutes=1) 
            duration_text = "60초"
        else:
            timeout_duration = datetime.timedelta(weeks=1) 
            duration_text = "1주일"
        
        try:
            await member.timeout(timeout_duration, reason=reason)
            logger.info(f"타임아웃 적용 성공 - 사용자: {member.name}, 기간: {duration_text}")
            
            try:
                dm_embed = create_warning_embed(
                    title="✉️ 통지서",
                    description=f"당신은 **{ctx.guild.name}** 서버에서 {duration_text}동안 타임아웃 되었습니다.",
                    footer=f"전과 {count}회"
                )
                dm_embed.add_field(name="사유", value=reason, inline=True)
                await member.send(embed=dm_embed)
                logger.info(f"DM 전송 성공 - 사용자: {member.name}")
            except discord.Forbidden:
                logger.warning(f"DM 전송 실패 (권한 없음) - 사용자: {member.name}")
                await ctx.send(f"{member.mention}에게 메시지가 안보내져요")
            except Exception as e:
                logger.error(f"DM 전송 중 오류 발생 - 사용자: {member.name}, 오류: {str(e)}")
                print(e)
            
            embed = create_warning_embed(
                title="⚖️ 처벌",
                description=f"전과 {count}범 {member.mention}를 {duration_text}동안 구금했습니다.",
                footer=f"by {ctx.author.display_name}"
            )
            embed.add_field(name="사유", value=reason, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            logger.error(f"타임아웃 적용 실패 (권한 없음) - 사용자: {member.name}")
            await ctx.send(embed=create_error_embed("봇 권한 이슈"))
        except Exception as e:
            logger.error(f"타임아웃 적용 중 오류 발생 - 사용자: {member.name}, 오류: {str(e)}")
            await ctx.send(embed=create_error_embed(str(e)))

async def setup(bot):
    await bot.add_cog(Judge(bot)) 