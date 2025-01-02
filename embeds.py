import discord

color = 0x000000
warnEmoji = "<:crimWarn:1142111019771105451>"


def create(item: str, auction_id: int) -> discord.Embed:
    embed = discord.Embed(title=f"Created Auction!", color=color)

    embed.add_field(
        name=f"Auction Created for {item}",
        value=f"Go visit the auction at <#{auction_id}>",
        inline=False,
    )

    return embed


def auction(
    user_id: int, item: str, duration: int, start_price: int, min_bid_increment
) -> discord.Embed:
    embed = discord.Embed(title=f"New Auction!", color=color)
    embed.add_field(
        name="Seller",
        value=f"<@{user_id}>",
        inline=False,
    )
    embed.add_field(
        name="Item Being Auctioned",
        value=f"{item}",
        inline=False,
    )
    embed.add_field(
        name="Starting Bid",
        value=f"${start_price}",
        inline=False,
    )
    embed.add_field(
        name="Ends at",
        value=f"<t:{duration}:f>",
        inline=False,
    )
    embed.add_field(
        name="Minimum Bid Increase",
        value=f"${min_bid_increment}",
        inline=False,
    )
    embed.set_footer(text="Bid using /bid (amount)")

    return embed


def auction_win(winner_id, item, highest_bid, end_time) -> discord.Embed:
    embed = discord.Embed(title=f"Auction Ended!", color=color)
    embed.add_field(name="Winner!", value=f"<@{winner_id}>", inline=False)
    embed.add_field(name="Item Won!", value=f"{item}", inline=False)
    embed.add_field(name="Highest Bid", value=f"${highest_bid}", inline=False)
    embed.add_field(name="Auction Ended", value=f"<t:{end_time}:f>", inline=False)

    return embed

def info_embeds(info) -> discord.Embed:
    embeds = []
    for block in info:
        local_embed = discord.Embed(title=block[0], color=color)
        local_embed.add_field(
            name=" ",
            value=block[1],
            inline=False,
        )
        embeds.append(local_embed)

    return embeds

def error(message: str) -> discord.Embed:
    """A general purpose error embed

    Args:
        message (str): The error message

    Returns:
        discord.Embed: An embed
    """
    return discord.Embed(
        title=f"{warnEmoji} There occurred an error while executing the command {warnEmoji}",
        description=message,
        color=color,
    )

def success(message: str) -> discord.Embed:
    """A general purpose success embed

    Args:
        message (str): The success message

    Returns:
        discord.Embed: An embed
    """
    return discord.Embed(
        title=":white_check_mark: Success! :white_check_mark:",
        description=message,
        color=color,
    )