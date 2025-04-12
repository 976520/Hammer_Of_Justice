import discord
from discord.ext import commands
from database import get_user_count
from utils.embeds import create_success_embed, create_error_embed

class Release(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='석방')
    @commands.has_permissions(moderate_members=True)
    async def release(self, ctx, member: discord.Member):
        user_id = str(member.id)
        server_id = str(ctx.guild.id)
        count = await get_user_count(user_id, server_id)

        try:
            await member.timeout(None)
            
            embed = create_success_embed(
                title="🕊️ 석방",
                description=f"전과 {count}범 {member.mention}를 석방했습니다.",
                footer=f"by {ctx.author.display_name}"
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send(embed=create_error_embed("봇 권한 이슈"))
        except Exception as e:
            await ctx.send(embed=create_error_embed(str(e)))

async def setup(bot):
    await bot.add_cog(Release(bot)) 