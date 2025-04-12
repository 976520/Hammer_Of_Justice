import discord
from discord.ext import commands
import logging
from utils.embeds import create_success_embed

logger = logging.getLogger(__name__)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='도움', aliases=['help', '기능','소개','정보', '명령어', '도움말', 'H', 'HELP', 'h'])
    async def help(self, ctx, command_name: str = None):
        logger.info(f"help({ctx.guild.name}, {ctx.author.name}, {command_name})")
        
        embed = create_success_embed(
            title="📖 정보",
            description=f"ping = {self.bot.latency * 1000}ms \n [내 서버에서 심판의 망치 사용하기](https://discord.com/oauth2/authorize?client_id=1351368587977162752&permissions=8&integration_type=0&scope=bot)"
        )
            
        embed.add_field(name="/심판 <유저> <?사유>", value="유저에게 타임아웃을 적용합니다 (전과 <= 3 이면 60초, 아니면 1주일)", inline=True)
        embed.add_field(name="/석방 <유저> <?전과삭제>", value="유저에게 적용된 타임아웃을 해제합니다 (전과삭제 = True 이면 전과 1 감소)", inline=True)
        embed.add_field(name="/청소 <?채널>", value="채널을 삭제 후 재생성합니다 (채널 이름 입력 시 해당 채널만 청소)", inline=True)
        

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
