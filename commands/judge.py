import discord
from discord.ext import commands
import datetime
from database import get_user_count, update_user_count

class Judge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='심판')
    @commands.has_permissions(moderate_members=True)  
    async def judge(self, ctx, member: discord.Member, *, reason: str = "없"):
        user_id = str(member.id)
        server_id = str(ctx.guild.id)
        
        count = get_user_count(user_id, server_id) + 1
        
        update_user_count(user_id, server_id, count)
        
        if count <= 3:
            timeout_duration = datetime.timedelta(minutes=1) 
            duration_text = "60초"
        else:
            timeout_duration = datetime.timedelta(weeks=1) 
            duration_text = "1주일"
        
        try:
            await member.timeout(timeout_duration, reason=reason)
            
            try:
                dm_embed = discord.Embed(
                    title="✉️ 통지서",
                    description=f"당신은 **{ctx.guild.name}** 서버에서 {duration_text}동안 타임아웃 되었습니다.",
                    color=0xFF5733
                )
                dm_embed.add_field(name="사유", value=reason, inline=True)
                dm_embed.add_field(name="전과", value=f"{count}회", inline=True)
                
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                await ctx.send(f"{member.mention}에게 메시지가 안보내져요")
            except Exception as e:
                print(e)
            
            embed = discord.Embed(
                title="⚖️ 처벌",
                description=f"전과 {count}범 {member.mention}를 {duration_text}동안 구금했습니다.",
                color=0xFF5733
            )
            embed.add_field(name="사유", value=reason, inline=True)
            embed.set_footer(text=f"by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("봇 권한 이슈")
        except Exception as e:
            await ctx.send(e)

async def setup(bot):
    await bot.add_cog(Judge(bot)) 