import discord
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands, tasks
import os
import json
from datetime import datetime, timedelta
import asyncio
import logging
import colorlog
import embeds
import admin

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CATEGORY_NAME = "Auctions"
MIN_BID_INCREMENT = 1000

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
client = commands.Bot(command_prefix=".", intents=intents)

colorlog_format = "%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(message)s"
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(colorlog_format, datefmt="%Y-%m-%d %H:%M:%S")
)

# Create a logger
logger = colorlog.getLogger()
logger.setLevel(colorlog.INFO)  # Set to DEBUG or INFO as needed
logger.addHandler(handler)

auctions_lock = asyncio.Lock()


@client.event
async def on_ready():
    await client.tree.sync()
    logging.info(f"{client.user} has connected to Discord!")
    client.loop.create_task(check_auctions())
    
@client.tree.command(name="help", description="Learn how to interact with Truman Auctions")
async def Help(interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    await interaction.followup.send(embed=embeds.help())

def load_auctions():
    if not os.path.exists("auctions.json"):
        with open("auctions.json", "w") as file:
            json.dump({"auctions": []}, file, indent=4)
    with open("auctions.json", "r") as file:
        return json.load(file)


async def check_auctions():
    global auctions_data
    await client.wait_until_ready()
    while not client.is_closed():
        current_time_unix = int(datetime.now().timestamp())

        for auction in auctions_data["auctions"]:
            if (
                auction["status"] == "active"
                and current_time_unix > auction["end_time"]
            ):
                auction["status"] = "ended"
                channel = client.get_channel(auction["channel_id"])
                if channel:
                    if auction["bids"]:
                        highest_bid = auction["bids"][-1]
                        winner_embed = embeds.auction_win(
                            highest_bid["user_id"],
                            auction["item_name"],
                            highest_bid["amount"],
                            auction["end_time"],
                        )
                        await channel.send(
                            embed=winner_embed, content=f"<@{highest_bid['user_id']}>"
                        )
                    else:
                        await channel.send(
                            f"The auction for '{auction['item_name']}' has ended with no bids placed."
                        )

        # Filter out auctions that have ended
        auctions_data["auctions"] = [
            auction
            for auction in auctions_data["auctions"]
            if auction["status"] != "ended"
        ]

        await save_auctions(auctions_data)

        # Wait for a minute before checking again
        await asyncio.sleep(60)


auctions_data = load_auctions()


async def add_auction(channel_id, item_name, seller_id, start_price, end_time):
    new_auction = {
        "channel_id": channel_id,  # Use the Discord channel ID
        "item_name": item_name,
        "seller_id": seller_id,
        "start_price": start_price,
        "bids": [],
        "end_time": end_time,
        "status": "active",
    }

    auctions_data["auctions"].append(new_auction)
    await save_auctions(auctions_data)
    return new_auction


async def add_bid(channel_id, user_id, bid_amount):
    for auction in auctions_data["auctions"]:
        if auction["channel_id"] == channel_id and auction["status"] == "active":
            current_highest_bid = (
                auction["bids"][-1]["amount"]
                if auction["bids"]
                else auction["start_price"]
            )
            if bid_amount <= current_highest_bid:
                return (
                    None,
                    f"Your bid must be higher than the current bid of {current_highest_bid}.",
                )
            elif bid_amount < current_highest_bid + MIN_BID_INCREMENT:
                return None, f"Bids must increase by at least {MIN_BID_INCREMENT}."

            new_bid = {
                "user_id": user_id,
                "amount": bid_amount,
                "timestamp": int(datetime.now().timestamp()),
            }
            auction["bids"].append(new_bid)
            await save_auctions(auctions_data)
            return new_bid, None
    return None, "Auction not found or inactive."


@client.tree.command(name="create", description="Create an auction.")
@app_commands.describe(item="Item you are auctioning.", duration="Duration of auction.")
@app_commands.choices(
    duration=[
        discord.app_commands.Choice(name="1 Day", value="one_day"),
        discord.app_commands.Choice(name="1 Week", value="one_week"),
        discord.app_commands.Choice(name="2 Weeks", value="two_weeks"),
    ]
)
async def create(
    interaction: discord.Interaction,
    item: str,
    duration: discord.app_commands.Choice[str],
    start_price: int,
) -> None:
    await interaction.response.defer()
    category = discord.utils.get(interaction.guild.categories, name=CATEGORY_NAME)
    try:
        if category is None:
            category = await interaction.guild.create_category(CATEGORY_NAME)
        auction_channel = await interaction.guild.create_text_channel(
            item, category=category
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "I do not have permission to create channels or categories.", ephemeral=True
        )
        return
    current_time = datetime.now()
    duration_mapping = {
        "one_day": timedelta(days=1),
        "one_week": timedelta(weeks=1),
        "two_weeks": timedelta(weeks=2),
    }
    end_time = int((current_time + duration_mapping[duration.value]).timestamp())
    await add_auction(
        auction_channel.id, item, interaction.user.id, start_price, end_time
    )
    auction_embed = embeds.auction(
        interaction.user.id, item, end_time, start_price, MIN_BID_INCREMENT
    )
    await auction_channel.send(embed=auction_embed)
    interaction_embed = embeds.create(item, auction_channel.id)
    await interaction.followup.send(embed=interaction_embed)


@client.tree.command(name="bid", description="Place a bid on the current auction.")
@app_commands.describe(bid_amount="The amount you want to bid.")
async def bid(interaction: discord.Interaction, bid_amount: int) -> None:
    new_bid, error = await add_bid(
        interaction.channel.id, interaction.user.id, bid_amount
    )
    if error:
        await interaction.response.send_message(error, ephemeral=True)
        return
    await interaction.channel.send(
        f"<@{interaction.user.id}> has placed a bid of {bid_amount}!"
    )
    await interaction.response.send_message(
        f"Your bid of {bid_amount} has been placed.", ephemeral=True
    )


# Save auctions to JSON file
async def save_auctions(auctions_data):
    with open("auctions.json", "w") as file:
        json.dump(auctions_data, file, indent=4)
        
client.tree.add_command(admin.adminCommands(client=client))


async def shutdown():
    logging.info("Shutting down...")
    await save_auctions(auctions_data)
    await client.close()


async def main():
    async with client:
        await client.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(shutdown())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
