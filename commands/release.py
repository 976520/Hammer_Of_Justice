import discord
from discord.ext import commands
import logging
from database import get_user_count, set_user_count
from utils.embeds import create_success_embed, create_error_embed, create_notice_embed

logger = logging.getLogger(__name__)

class Release(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='석방', aliases=['release', 'r', 'R', 'RELEASE', 'ㄱ'])
    @commands.has_permissions(moderate_members=True)
    async def release(self, ctx, member: discord.Member, clear_record: bool = False):
        logger.info(f"release({ctx.guild.name}, {ctx.author.name}, {member.name}, clear_record={clear_record})")
        
        user_id = str(member.id)
        server_id = str(ctx.guild.id)
        count = await get_user_count(user_id, server_id)

        if member.timed_out_until is None:
            await ctx.send(embed=create_notice_embed(f"{member.mention}은(는) 타임아웃 상태가 아닙니다."))
            return

        try:
            await member.timeout(None)
            
            if clear_record and count > 0:
                await set_user_count(user_id, server_id, count - 1)
                count -= 1
                clear_msg = "(전과 -1)"
            else:
                clear_msg = "(전과 유지)"
            
            embed = create_success_embed(
                title="🕊️ 석방",
                description=f"전과 {count}범 {member.mention}를 석방했습니다.\n{clear_msg}",
                footer=f"by {ctx.author.display_name}"
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send(embed=create_error_embed("봇 권한 이슈"))
        except Exception as e:
            await ctx.send(embed=create_error_embed(str(e)))

async def setup(bot):
    await bot.add_cog(Release(bot)) 