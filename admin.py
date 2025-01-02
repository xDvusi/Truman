import discord
import aiohttp
import asyncio
import embeds

class adminCommands(discord.app_commands.Group):
    def __init__(self, client):
        super().__init__()
        self.name = "admin"
        self.description = "Admin commands for the Truman bot"
        self.default_permissions = discord.Permissions(permissions=8)
        self.guild_only = False
        self.client = client
    
    @discord.app_commands.command(name="update_webhooks", description="Update Info & Rules")
    async def update_webhooks(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id != 180511939812655117:
            embed = embeds.error("You do not have the permissions to do this command.")
            await interaction.followup.send(embed=embed)
        with open("webhooks/info.txt", "r") as info_content:
            info_blocks = info_content.read().split("<=>")
        info_message = []
        for block in info_blocks:
            info_message.append(block.split("<->"))
            
        embeds_list = embeds.info_embeds(info_message)
        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                "https://discord.com/api/webhooks/1324279187435028521/RyYqFF_01bF-tOr4IOCPHTVJHV65BQGOjjKq_PAjqpzs7pTkX8HQUXse3ita6-L1Gc-T",
                session=session,
            )
            await webhook.send(embeds = embeds_list, username="Truman Info")
        
        embed = embeds.success("Successfully updated Webhooks!")
        await interaction.followup.send(embed=embed)