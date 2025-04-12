import discord
from discord.ext import commands

class Clean(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='청소')
    @commands.has_permissions(manage_channels=True)
    async def clean_channel(self, ctx, *, channel_name: str = None):
        try:
            original_channel = ctx.channel
            channel_to_delete = original_channel
            
            if channel_name:
                found_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
                if found_channel:
                    channel_to_delete = found_channel
                else:
                    embed = discord.Embed(
                        title="❌ 오류",
                        description=f"'{channel_name}' 채널을 찾을 수 없습니다.",
                        color=0xE74C3C
                    )
                    await ctx.send(embed=embed)
                    return
            
            category = channel_to_delete.category
            position = channel_to_delete.position
            topic = channel_to_delete.topic
            slowmode_delay = channel_to_delete.slowmode_delay
            nsfw = channel_to_delete.is_nsfw()
            overwrites = channel_to_delete.overwrites
            
            embed = discord.Embed(
                title="🧹 채널 청소",
                description=f"채널 '{channel_to_delete.name}'을(를) 삭제하고 다시 생성합니다.",
                color=0x3498DB
            )
            await ctx.send(embed=embed)
            
            await channel_to_delete.delete(reason="더럽다 더러워")
            
            new_channel = await ctx.guild.create_text_channel(
                name=channel_to_delete.name,
                category=category,
                topic=topic,
                slowmode_delay=slowmode_delay,
                nsfw=nsfw,
                overwrites=overwrites,
                position=position,
                reason="더럽다 더러워"
            )
            
            embed = discord.Embed(
                title="✅ 청소 완료",
                description=f"채널이 성공적으로 청소되었습니다.",
                color=0x2ECC71
            )
            await new_channel.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ 오류",
                description="채널을 관리할 권한이 없습니다.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=e,
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Clean(bot)) 