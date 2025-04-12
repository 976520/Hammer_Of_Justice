import discord
from discord.ext import commands
import logging
from utils.embeds import create_notice_embed, create_success_embed, create_error_embed

logger = logging.getLogger(__name__)

class Clean(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='청소', aliases=['clean', 'c', 'C', 'CLEAN'])
    @commands.has_permissions(manage_channels=True)
    async def clean_channel(self, ctx, *, channel_name: str = None):
        logger.info(f"clean_channel({ctx.guild.name}, {ctx.author.name})")
        try:
            original_channel = ctx.channel
            channel_to_delete = original_channel
            
            if channel_name:
                found_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
                if found_channel:
                    channel_to_delete = found_channel
                else:
                    await ctx.send(embed=create_error_embed(f"'{channel_name}' 이런 채널 없는데요"))
                    return
            
            category = channel_to_delete.category
            position = channel_to_delete.position
            topic = channel_to_delete.topic
            slowmode_delay = channel_to_delete.slowmode_delay
            nsfw = channel_to_delete.is_nsfw()
            overwrites = channel_to_delete.overwrites
            
            await ctx.send(embed=create_notice_embed(
                title="🧹 채널 청소",
                description=f"채널 '{channel_to_delete.name}'을(를) 삭제하고 다시 생성합니다."
            ))
            
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
            
            await new_channel.send(embed=create_success_embed(
                title="✅ 청소 완료",
                description="채널이 성공적으로 청소되었습니다."
            ))
            
        except discord.Forbidden:
            await ctx.send(embed=create_error_embed("권한 없음 이슈"))
        except Exception as e:
            await ctx.send(embed=create_error_embed(str(e)))

async def setup(bot):
    await bot.add_cog(Clean(bot)) 