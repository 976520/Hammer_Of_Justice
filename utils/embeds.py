import discord

def create_embed(title: str, description: str, color: int = 0x2ECC71, footer: str = None) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    if footer:
        embed.set_footer(text=footer)
    return embed

def create_error_embed(description: str) -> discord.Embed:
    return create_embed(
        title="❌ 오류",
        description=description,
        color=0xE74C3C
    )

def create_notice_embed(title: str, description: str, footer: str = None) -> discord.Embed:
    return create_embed(
        title=title,
        description=description,
        color=0x3498DB,
        footer=footer
    )

def create_success_embed(title: str, description: str, footer: str = None) -> discord.Embed:
    return create_embed(
        title=title,
        description=description,
        color=0x2ECC71,
        footer=footer
    )

