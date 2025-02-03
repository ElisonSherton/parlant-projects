import argparse

from parlant.client import (
    GuidelineContent,
    GuidelinePayload,
    ParlantClient,
    Payload,
)

from pprint import pprint
from utils import *
from typing import List
from copy import deepcopy


# Function to filter the new guidelines from the set of existing guidelines added to a client
def filter_guidelines(client: ParlantClient, agent_id: str, guidelines: List) -> List:
    """Given an agent, and a list of guidelines, check which guidelines are already added to the agent and filter them out from the provided list of guidelines

    Args:
        client (ParlantClient): Parlant Client
        agent_id (str): The id of the agent for which the attached guidelines will be retrived
        guidelines (List): A list of all the guidelines to be attached to the agent with agent_id

    Returns:
        List: Filtered list of guidelines
    """
    attached_guidelines = client.guidelines.list(agent_id=agent_id)

    filtered_guidelines = deepcopy(guidelines)
    guidelines_to_remove = []

    for guideline in attached_guidelines:
        condition = guideline.condition
        action = guideline.action

        for g in guidelines:
            if (g["condition"] == condition) and (g["action"] == action):
                guidelines_to_remove.append(g)
                break

    for unnecessary_guideline in guidelines_to_remove:
        filtered_guidelines.remove(unnecessary_guideline)

    # Show the filtered guidelines
    pprint(f"Will only be attaching the following guidelines out of all the provided guidelines since the remaining ones are already added:\n")
    for guideline in filtered_guidelines:
        pprint(f"Condition: {guideline['condition']}")
        pprint(f"Action: {guideline['action']}")
        pprint(f"Tool: {guideline['tool']}")
        print()

    return filtered_guidelines


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

    # Check if any guideline from the json object are already added, if yes, do not repeat the work
    filtered_guidelines = filter_guidelines(client, agent_id, guidelines)

    for guideline in filtered_guidelines:
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
                        coherence_check=False,
                        connection_proposition=False,
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
