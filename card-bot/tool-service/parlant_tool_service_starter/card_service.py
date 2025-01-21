from datetime import datetime
from random import random
from typing import Any, Optional, List
from lagom import Container
from uuid import uuid4
from enum import Enum
from parlant.core.background_tasks import BackgroundTaskService
from parlant.core.services.tools.plugins import PluginServer, tool
from parlant.core.services.tools.service_registry import ServiceRegistry
from parlant.core.tools import ToolContext, ToolResult
import asyncio

server_instance: PluginServer | None = None

USER_ACCOUNTS = ["ACC234", "ACC123"]
CHECKING_ACCOUNT_ID = f"CHECKING_{USER_ACCOUNTS[0]}"
CC_ACCOUNT_ID = f"CC_{USER_ACCOUNTS[0]}"
CARD_TRANSACTION_LIMIT = 5000
TRANSACTION_SCHEDULE_LIMIT = 30

CHECKINGS_ACCOUNT_BALANCE: dict[str, float] = {
    f"CHECKING_{USER_ACCOUNTS[0]}": 3000.00,
    f"CHECKING_{USER_ACCOUNTS[1]}": 1700.00,
}

CARD_INFO: dict[str, Any] = {
    f"CC_{USER_ACCOUNTS[0]}": [
        {"id": "1", "type": "Visa", "last4": "5432", "balance": 2500.00},
        {"id": "2", "type": "Amex", "last4": "9876", "balance": 3500.00},
    ],
    f"CC_{USER_ACCOUNTS[1]}": [
        {"id": "3", "type": "Visa", "last4": "1234", "balance": 1500.00},
        {"id": "4", "type": "Mastercard", "last4": "5678", "balance": 2300.00},
    ],
}

BENEFICIARIES = [
    {"beneficiary_id": "s12d", "name": "yam marcovitz"},
    {"beneficiary_id": "e4l2", "name": "vishal ahuja"},
    {"beneficiary_id": "d3k4", "name": "vidhya duthaluru"},
    {"beneficiary_id": "s12d", "name": "kristine ma"},
]

CHECKING_TRANSACTION_HISTORY: dict[str, Any] = {
    f"CHECKING_{USER_ACCOUNTS[0]}": [
        {
            "beneficiary": "yam marcovitz",
            "transaction_amount": 361.85,
            "transaction_id": "QFGN",
            "transaction_date": "22-01-2024",
        },
        {
            "beneficiary": "vishal ahuja",
            "transaction_amount": 204.9,
            "transaction_id": "TEUX",
            "transaction_date": "27-07-2024",
        },
        {
            "beneficiary": "vidhya duthaluru",
            "transaction_amount": 210.63,
            "transaction_id": "0BOZ",
            "transaction_date": "04-05-2024",
        },
        {
            "beneficiary": "vidhya duthaluru",
            "transaction_amount": 475.14,
            "transaction_id": "5G7O",
            "transaction_date": "10-12-2024",
        },
        {
            "beneficiary": "vidhya duthaluru",
            "transaction_amount": 415.4,
            "transaction_id": "T0OM",
            "transaction_date": "25-02-2024",
        },
        {
            "beneficiary": "vidhya duthaluru",
            "transaction_amount": 451.58,
            "transaction_id": "TAVI",
            "transaction_date": "08-10-2024",
        },
        {
            "beneficiary": "vidhya duthaluru",
            "transaction_amount": 212.96,
            "transaction_id": "32SP",
            "transaction_date": "11-03-2024",
        },
        {
            "beneficiary": "yam marcovitz",
            "transaction_amount": 226.17,
            "transaction_id": "MRSU",
            "transaction_date": "23-06-2024",
        },
        {
            "beneficiary": "vishal ahuja",
            "transaction_amount": 251.7,
            "transaction_id": "07MV",
            "transaction_date": "12-07-2024",
        },
        {
            "beneficiary": "vishal ahuja",
            "transaction_amount": 223.67,
            "transaction_id": "2NXW",
            "transaction_date": "24-06-2024",
        },
    ],
    f"CHECKING_{USER_ACCOUNTS[1]}": [
        {
            "beneficiary": "vidhya duthaluru",
            "transaction_amount": 435.05,
            "transaction_id": "67RX",
            "transaction_date": "08-02-2024",
        },
        {
            "beneficiary": "yam marcovitz",
            "transaction_amount": 271.73,
            "transaction_id": "WEKJ",
            "transaction_date": "06-10-2024",
        },
        {
            "beneficiary": "yam marcovitz",
            "transaction_amount": 326.99,
            "transaction_id": "CU59",
            "transaction_date": "20-03-2024",
        },
        {
            "beneficiary": "yam marcovitz",
            "transaction_amount": 224.46,
            "transaction_id": "TFH2",
            "transaction_date": "12-10-2024",
        },
        {
            "beneficiary": "kristine ma",
            "transaction_amount": 313.02,
            "transaction_id": "N14P",
            "transaction_date": "16-02-2024",
        },
        {
            "beneficiary": "kristine ma",
            "transaction_amount": 405.15,
            "transaction_id": "N17I",
            "transaction_date": "06-03-2024",
        },
        {
            "beneficiary": "vishal ahuja",
            "transaction_amount": 422.03,
            "transaction_id": "Y0KG",
            "transaction_date": "11-07-2024",
        },
        {
            "beneficiary": "vishal ahuja",
            "transaction_amount": 366.55,
            "transaction_id": "4CJ7",
            "transaction_date": "28-02-2024",
        },
        {
            "beneficiary": "yam marcovitz",
            "transaction_amount": 217.1,
            "transaction_id": "D02H",
            "transaction_date": "24-10-2024",
        },
        {
            "beneficiary": "vidhya duthaluru",
            "transaction_amount": 224.07,
            "transaction_id": "BR0M",
            "transaction_date": "18-12-2024",
        },
    ],
}


@tool
def list_transactions(
    context: ToolContext, account_id: Optional[str] = None
) -> ToolResult:
    """A tool to retrieve the list of transactions belonging to a particular account ID for a checking account.

    Args:
        account_id (Optional[str], optional): Account ID for which the transactions need to be fetched. Defaults to None.

    Returns:
        ToolResult: A list of transactions belonging to the provided account id if everything goes as planned. Otherwise a helpful message telling the user what went wrong and where
    """
    global CHECKING_ACCOUNT_ID

    if account_id is None:
        account_id = CHECKING_ACCOUNT_ID
    CHECKING_ACCOUNT_ID = account_id

    try:
        if not account_id in CHECKING_TRANSACTION_HISTORY.keys():
            print("Not found account id in transaction history")
            return ToolResult({"error": "provided account id not found"})
        print("Found account id and set global variable")
        ACCOUNT_ID = account_id
    except Exception as e:
        return ToolResult({"error": f"Failed to set the account id\n"})

    try:
        transactions = CHECKING_TRANSACTION_HISTORY[ACCOUNT_ID]
        return ToolResult(
            {
                "success": f"Here is the list of transactions for the given account\n{transactions}"
            }
        )
    except Exception as e:
        return ToolResult(
            {"error": f"Failed to get the list of transactions\n{str(e)}"}
        )


@tool
def list_cards(context: ToolContext, account_id: Optional[str] = None) -> ToolResult:
    """A tool to retrieve the list of cards belonging to a particular account ID.

    Args:
        account_id (Optional[str], optional): Account ID for which the cards need to be fetched. Defaults to None.

    Returns:
        ToolResult: A list of cards belonging to the provided account id if everything goes as planned. Otherwise a helpful message telling the user what went wrong and where
    """
    global CC_ACCOUNT_ID

    if account_id is None:
        account_id = CC_ACCOUNT_ID
    CC_ACCOUNT_ID = account_id

    try:
        if not account_id in CARD_INFO.keys():
            print("Not found account id in card info")
            return ToolResult({"error": "provided account id not found"})
        print("Found account id and set global variable")
        CC_ACCOUNT_ID = account_id
    except Exception as e:
        return ToolResult({"error": f"Failed to set the account id\n"})

    try:
        print("Before fetching")
        cards = CARD_INFO[CC_ACCOUNT_ID]
        print("After fetching")
        return ToolResult(
            {"success": f"Here is the list of cards for this account\n{cards}"}
        )
    except Exception as e:
        return ToolResult({"error": f"Failed to get the list of cards\n{str(e)}"})


class PaymentSource(Enum):
    CHECKING = "checking"
    SAVINGS = "savings"


@tool
def make_payment_to_card(
    context: ToolContext,
    card_id: str,
    payment_amount: float,
    payment_source: PaymentSource,
    payment_date_provided_by_customer: str,
) -> ToolResult:
    """Given the necessary arguments, make payment to card

    Args:
        payment_amount (float): Amount to be paid to the card in dollars
        payment_source (PaymentSource): Source of the payment i.e. checking account, external bank etc.
        payment_date_provided_by_customer (str): Customer provided date for the payment, this date is in format DD-MM-YYYY

    Returns:
        ToolResult: Payment acknowledgement and success message if everything goes well, otherwise a helpful error message
    """

    payment_date = payment_date_provided_by_customer

    if not payment_date:
        return ToolResult(
            {"error": "The customer needs to provide date for the payment"}
        )

    # Validate the card id
    try:
        available_cards = CARD_INFO[CC_ACCOUNT_ID]
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
            payment_amount < CARD_TRANSACTION_LIMIT
        ), f"You have set your transaction limit to {CARD_TRANSACTION_LIMIT}. Please modify the limit to make the payment"
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
        print("Successfully processed your request")
        return ToolResult(
            {
                "success": f"We have successfully processed your request! The transaction id is {transaction_id}. Keep this handy for future reference"
            }
        )
    except Exception as e:
        return ToolResult(
            {
                "error": f"Something went wrong while making the transaction. Error: {str(e)}"
            }
        )


@tool
def get_checking_account_balance(
    context: ToolContext, account_id: Optional[str] = None
) -> ToolResult:
    """A tool to retrieve the balance of a checking account.

    Args:
        account_id (Optional[str], optional): Account ID for which the balance needs to be fetched. Defaults to None.

    Returns:
        ToolResult: The balance of the provided account id if everything goes as planned. Otherwise a helpful message telling the user what went wrong and where
    """
    global CHECKING_ACCOUNT_ID

    if account_id is None:
        account_id = CHECKING_ACCOUNT_ID
    CHECKING_ACCOUNT_ID = account_id

    try:
        if not account_id in CHECKINGS_ACCOUNT_BALANCE.keys():
            print("Not found account id in checking account balance")
            return ToolResult({"error": "provided account id not found"})
        print("Found account id and set global variable")
        ACCOUNT_ID = account_id
    except Exception as e:
        return ToolResult({"error": f"Failed to set the account id\n"})

    try:
        balance = CHECKINGS_ACCOUNT_BALANCE[ACCOUNT_ID]
        return ToolResult(
            {"success": f"The balance for the given account is {balance}"}
        )
    except Exception as e:
        return ToolResult({"error": f"Failed to get the account balance\n{str(e)}"})


@tool
def make_payment_to_beneficiary(
    context: ToolContext,
    beneficiary: str,
    amount_to_transfer: float,
    account_id: Optional[str] = None,
) -> ToolResult:
    """Make a payment to a beneficiary.

    Args:
        beneficiary (str): The beneficiary to whom the payment is to be made.
        amount_to_transfer (float): The amount to transfer.
        account_id (Optional[str], optional): The account ID from which the payment is to be made. Defaults to None.

    Returns:
        ToolResult: Payment acknowledgement and success message if everything goes well, otherwise a helpful error message.
    """
    global ACCOUNT_BALANCE, CHECKING_ACCOUNT_BALANCE, CHECKING_ACCOUNT_ID

    if account_id is None:
        account_id = CHECKING_ACCOUNT_ID
    CHECKING_ACCOUNT_ID = account_id

    # Validate the beneficiary
    valid_beneficiaries = [b["name"] for b in BENEFICIARIES]
    if beneficiary.lower() not in valid_beneficiaries:
        return ToolResult(
            {
                "error": "The selected beneficiary is not present in your list of beneficiaries. Please add the beneficiary before making the payment"
            }
        )

    # Validate the amount
    if amount_to_transfer <= 0:
        return ToolResult({"error": "The amount to transfer must be positive"})
    if amount_to_transfer > CHECKINGS_ACCOUNT_BALANCE[CHECKING_ACCOUNT_ID]:
        return ToolResult({"error": "Insufficient balance to make the transfer"})
    if amount_to_transfer >= CHECKINGS_ACCOUNT_BALANCE[CHECKING_ACCOUNT_ID]:
        return ToolResult(
            {
                "error": f"You only have {CHECKINGS_ACCOUNT_BALANCE[CHECKING_ACCOUNT_ID]} in your account. Please transfer a smaller amount."
            }
        )

    if account_id not in CHECKINGS_ACCOUNT_BALANCE.keys():
        return ToolResult({"error": "The provided account ID is not valid"})

    # Perform the transaction
    try:
        transaction_id = str(uuid4())[:4]
        transaction_date = datetime.now().strftime("%d-%m-%Y")
        transaction = {
            "beneficiary": beneficiary,
            "transaction_amount": amount_to_transfer,
            "transaction_id": transaction_id,
            "transaction_date": transaction_date,
        }

        CHECKING_TRANSACTION_HISTORY[account_id].append(transaction)

        # Update the account balance
        initial_balance = CHECKINGS_ACCOUNT_BALANCE[account_id]
        CHECKINGS_ACCOUNT_BALANCE[account_id] -= amount_to_transfer
        final_balance = CHECKINGS_ACCOUNT_BALANCE[account_id]

        return ToolResult(
            {
                "success": f"Payment successful! Transaction ID: {transaction_id}",
                "initial_balance": initial_balance,
                "final_balance": final_balance,
                "transaction": transaction,
            }
        )
    except Exception as e:
        return ToolResult(
            {"error": f"Something went wrong while making the payment. Error: {str(e)}"}
        )


TOOLS = [
    list_cards,
    make_payment_to_card,
    make_payment_to_beneficiary,
    list_transactions,
    get_checking_account_balance,
]


async def main() -> None:
    async with PluginServer(tools=TOOLS, port=8089):
        pass


if __name__ == "__main__":
    asyncio.run(main())
