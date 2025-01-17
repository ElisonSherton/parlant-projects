from datetime import datetime
from random import random
from typing import Any, Optional, List
from lagom import Container
from uuid import uuid4

from parlant.core.background_tasks import BackgroundTaskService
from parlant.core.services.tools.plugins import PluginServer, tool
from parlant.core.services.tools.service_registry import ServiceRegistry
from parlant.core.tools import ToolContext, ToolResult
import asyncio

server_instance: PluginServer | None = None

ACCOUNT_ID = "ACC234"
TRANSACTION_LIMIT = 5000
TRANSACTION_SCHEDULE_LIMIT = 30

CARD_INFO: dict[str, Any] = {
    "ACC234": [
        {"id": "1", "type": "Visa", "last4": "5432", "balance": 2500.00},
        {"id": "2", "type": "Amex", "last4": "9876", "balance": 3500.00},
    ],
    "ACC123": [
        {"id": "3", "type": "Visa", "last4": "1234", "balance": 1500.00},
        {"id": "4", "type": "Mastercard", "last4": "5678", "balance": 2300.00},
    ],
}


@tool
def list_cards(
    context: ToolContext, account_id: Optional[str] = ACCOUNT_ID
) -> ToolResult:
    """A tool to retrieve the list of cards belonging to a particular account ID.

    Args:
        context (ToolContext): Available context from the conversation
        account_id (Optional[str], optional): Account ID for which the cards need to be fetched. Defaults to the global ACCOUNT_ID.

    Returns:
        ToolResult: A list of cards belonging to the provided account id if everything goes as planned. Otherwise a helpful message telling the user what went wrong and where
    """
    print(f"Got this account id: {account_id}")

    try:
        if not account_id in CARD_INFO.keys():
            print("Not found account id in card info")
            return ToolResult({"error": "provided account id not found"})
        print("Found account id and set global variable")
        ACCOUNT_ID = account_id
    except Exception as e:
        return ToolResult({"error": f"Failed to set the account id\n"})

    try:
        print("Before fetching")
        cards = CARD_INFO[ACCOUNT_ID]
        print("After fetching")
        return ToolResult(
            {"success": f"Here is the list of cards for this account\n{cards}"}
        )
    except Exception as e:
        return ToolResult({"error": f"Failed to get the list of cards\n{str(e)}"})


@tool
def make_payment(
    context: ToolContext,
    card_id: str,
    payment_amount: float,
    payment_source: str,
    payment_date: str,
) -> ToolResult:
    """Given the necessary arguments, make payment to card

    Args:
        context (ToolContext): Available context from the conversation
        payment_amount (float): Amount to be paid to the card in dollars
        payment_source (str): Source of the payment i.e. checking account, external bank etc.
        payment_date (str): When to make the payment, this date is in format DD-MM-YYYY

    Returns:
        ToolResult: Payment acknowledgement and success message if everything goes well, otherwise a helpful error message
    """

    # Validate the card id
    try:
        available_cards = CARD_INFO[ACCOUNT_ID]
        valid_card_ids = [x["id"] for x in available_cards]
        if card_id not in valid_card_ids:
            return ToolResult(
                {"error": "The selected card does not belong to the current user"}
            )
    except Exception as e:
        return ToolResult(
            {
                "error": f"Something went wrong while validating your card. Error: {str(e)}"
            }
        )

    print("Successfully validated the card id")
    # Validate the payment amount
    try:
        assert payment_amount > 0, "Payment amount cannot be negative"
        assert (
            payment_amount < TRANSACTION_LIMIT
        ), f"You have set your transaction limit to {TRANSACTION_LIMIT}. Please modify the limit to make the payment"
    except Exception as e:
        return ToolResult(
            {
                "error": f"Something went wrong while validating your payment amount. Error: {str(e)}"
            }
        )

    print("Successfully validated the payment amount")
    # Validate the payment date
    try:
        payment_date = datetime.strptime(payment_date, "%d-%m-%Y")
        assert payment_date > datetime.now(), "Payment date must be in the future"
        assert (
            payment_date - datetime.now()
        ).days <= TRANSACTION_SCHEDULE_LIMIT, (
            "Payment date cannot be more than a month from today"
        )
    except Exception as e:
        return ToolResult(
            {
                "error": f"Something went wrong while validating your payment date. Error: {str(e)}"
            }
        )

    print("Successfully validated the payment date")

    # Perform the transaction
    try:
        transaction_id = str(uuid4())
        print("Successfully made the payment")
        return ToolResult(
            {
                "success": f"You have successfully made payment to your card! The transaction id is {transaction_id}. Keep this handy for future reference"
            }
        )
    except Exception as e:
        return ToolResult(
            {
                "error": f"Something went wrong while making the transaction. Error: {str(e)}"
            }
        )


TOOLS = [list_cards, make_payment]


async def main() -> None:
    async with PluginServer(tools=TOOLS, port=8089):
        pass


if __name__ == "__main__":
    asyncio.run(main())
