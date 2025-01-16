from datetime import datetime
from random import random
from typing import Any, Optional, List
from lagom import Container

from parlant.core.background_tasks import BackgroundTaskService
from parlant.core.services.tools.plugins import PluginServer, tool
from parlant.core.services.tools.service_registry import ServiceRegistry
from parlant.core.tools import ToolContext, ToolResult
import asyncio

server_instance: PluginServer | None = None

ACCOUNT_ID = "ACC234"

CARD_INFO: dict[str, Any] = {
    "ACC234":[
        {"id": "1", "type": "Visa", "last4": "5432", "balance": 2500.00},
        {"id": "2", "type": "Amex", "last4": "9876", "balance": 3500.00}
    ],
    "ACC123":[
        {"id": "3", "type": "Visa", "last4": "1234", "balance": 1500.00},
        {"id": "4", "type": "Mastercard", "last4": "5678", "balance": 2300.00}
    ]
}

@tool
def list_cards(context: ToolContext, account_id: str = ACCOUNT_ID) -> ToolResult:
    """Get the list of cards linked to the given account_id, default account id is ACC234"""
    print(f"Got this account id: {account_id}")
    # if account_id == "guest":
    #     account_id = ACCOUNT_ID
    #     print(f"Set the account id by default to {ACCOUNT_ID}")
        
    try:
        if not account_id in CARD_INFO.keys():
            print("Not found account id in card info")
            return ToolResult({"error": "provided account id not found"})
        print("Found account id and set global variable")
        ACCOUNT_ID = account_id
    except Exception as e:
        return ToolResult({"error": f"failed to set the account id\n"})

    try:
        print("Before fetching")
        cards = CARD_INFO[ACCOUNT_ID]
        print("After fetching")
        return ToolResult({"success": f"Here is the list of cards for this account\n{cards}"})
    except Exception as e:
        return ToolResult({"error": f"failed to get the list of cards\n{str(e)}"})

TOOLS = [
    list_cards
]

async def main() -> None:
    async with PluginServer(tools=TOOLS, port=8089):
        pass
        
if __name__ == "__main__":
    asyncio.run(main())
