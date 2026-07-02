"""Modal wrapper to support both on_submit and wait() patterns."""
import asyncio
import discord


class ModalWaiter(discord.ui.Modal):
    """Modal that captures inputs and supports wait()."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._done = asyncio.Event()
        self._values: dict = {}
    
    async def wait(self):
        """Wait for modal submission."""
        await self._done.wait()
        return self._values
    
    async def on_submit(self, interaction: discord.Interaction):
        for child in self.children:
            self._values[child.label] = child.value
        self._done.set()
        # Let original code handle the response
        await interaction.response.defer()
