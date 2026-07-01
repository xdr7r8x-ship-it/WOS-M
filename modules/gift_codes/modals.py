"""
WOS-M Gift Codes Modals
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from discord import ui
from typing import Optional, Dict, Any

from core.i18n import i18n


class AddGiftCodeModal(ui.Modal):
    """Modal for adding a gift code."""
    
    def __init__(self):
        super().__init__(
            title=i18n.get("gift_codes.add_code"),
            custom_id="add_gift_code_modal"
        )
        
        self.code_input = ui.TextInput(
            label=i18n.get("gift_codes.code"),
            placeholder="Enter gift code",
            required=True,
            max_length=50
        )
        
        self.add_item(self.code_input)


class RedeemGiftCodeModal(ui.Modal):
    """Modal for redeeming a gift code."""
    
    def __init__(self):
        super().__init__(
            title=i18n.get("gift_codes.manual_redeem"),
            custom_id="redeem_gift_code_modal"
        )
        
        self.code_input = ui.TextInput(
            label=i18n.get("gift_codes.code"),
            placeholder="Enter gift code",
            required=True,
            max_length=50
        )
        
        self.fid_input = ui.TextInput(
            label=i18n.get("players.fid"),
            placeholder="Enter player FID",
            required=True,
            max_length=50
        )
        
        self.add_item(self.code_input)
        self.add_item(self.fid_input)


class BatchRedeemModal(ui.Modal):
    """Modal for batch redemption."""
    
    def __init__(self):
        super().__init__(
            title=i18n.get("gift_codes.batch_redeem"),
            custom_id="batch_redeem_modal"
        )
        
        self.code_input = ui.TextInput(
            label=i18n.get("gift_codes.code"),
            placeholder="Enter gift code",
            required=True,
            max_length=50
        )
        
        self.add_item(self.code_input)
