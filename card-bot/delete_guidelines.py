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


# Function to add the guidelines provided in the guidelines.json file
def delete_guidelines(agent_id: str):
    """
    Removes all the guidelines attached to the provided agent

    Args:
        agent_id (str): The ID of the agent from which the guidelines will be removed.

    Returns:
        None
    """
    try:
        config = get_config()
        client = ParlantClient(base_url=config["server_address"])

        attached_guidelines = client.guidelines.list(agent_id=agent_id)
        for guideline in attached_guidelines:
            client.guidelines.delete(agent_id=agent_id, guideline_id=guideline.id)
        print(
            f"Successfully deleted all the guidelines attached to the agent: {agent_id}"
        )
    except Exception as e:
        print(f"Could not delete all the guidelines; Error: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove all the guidelines from an agent."
    )
    parser.add_argument(
        "--agent-id",
        type=str,
        help="The ID of the agent to which the guidelines will be added.",
    )
    args = parser.parse_args()
    delete_guidelines(args.agent_id)
