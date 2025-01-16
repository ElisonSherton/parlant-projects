import argparse
from parlant.client import (
    GuidelineContent,
    GuidelinePayload,
    ParlantClient,
    Payload,
)
from utils import *


# Function to add the guidelines provided in the guidelines.json file
def add_guidelines(agent_id: str):
    """
    Adds all the guidelines specified in the guidelines.json file for the given agent.

    Args:
        agent_id (str): The ID of the agent to which the guidelines will be added.

    Returns:
        None
    """
    config = get_config()
    guidelines = get_guidelines()
    guidelines = guidelines[config["bot"]]

    client = ParlantClient(base_url=config["server_address"])

    for guideline in guidelines:
        condition, action = guideline["condition"], guideline["action"]
        # Start evaluating the guideline's impact
        evaluation = client.evaluations.create(
            agent_id=agent_id,
            payloads=[
                Payload(
                    kind="guideline",
                    guideline=GuidelinePayload(
                        content=GuidelineContent(
                            condition=condition,
                            action=action,
                        ),
                        operation="add",
                        coherence_check=True,
                        connection_proposition=True,
                    ),
                )
            ],
        )

        # Wait for the evaluation to complete and get the invoice
        invoices = client.evaluations.retrieve(
            evaluation.id,
            wait_for_completion=120,  # Wait up to 120 seconds
        ).invoices

        # Only continue if the guideline addition was approved
        if all(invoice.approved for invoice in invoices):
            client.guidelines.create(agent_id=agent_id, invoices=invoices)
        else:
            print("Guideline was not approved:")
            print(invoices)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add guidelines to an agent.")
    parser.add_argument(
        "--agent-id",
        type=str,
        help="The ID of the agent to which the guidelines will be added.",
    )
    args = parser.parse_args()
    add_guidelines(args.agent_id)
