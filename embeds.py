import discord

color = 0x000000


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
