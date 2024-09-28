from discord.ext import commands
import discord
from discord import app_commands

class Premium(commands.Cog, name="Premium"):
    def __init__(self, client: commands.Bot):
        self.client = client


class SupportView(discord.ui.View):
    @discord.ui.button(label="Donate (Sandbox)", style=discord.ButtonStyle.green)
    async def donate(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Modal to input custom amount
        await interaction.response.send_modal(DonationModal())

class DonationModal(discord.ui.Modal, title="Enter Donation Amount"):
    amount = discord.ui.TextInput(label="Amount (in USD)", placeholder="10", required=True, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction, sandbox: bool):
        if (amount <= 0):
            await interaction.response.send_message("Please input an amount greater than 0.")
            return
        # Use the PayPal Sandbox environment
        amount = self.amount.value
        # Replace with your sandbox business email
        if not sandbox:
            paypal_link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=kryptstep&currency_code=USD&amount={amount}"
        else:
            paypal_link = f"https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_donations&business=sb-m7r8n31339647@business.example.com&currency_code=USD&amount={amount}"

        # Create a button that links to the PayPal sandbox payment page
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Pay via PayPal (Sandbox)", url=paypal_link, style=discord.ButtonStyle.link))

        await interaction.response.send_message("Click the button below to complete your donation:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Premium(bot))
