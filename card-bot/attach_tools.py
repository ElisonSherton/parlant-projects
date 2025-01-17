from parlant.client import (
    ParlantClient,
    GuidelineToolAssociationUpdateParams,
    Guideline,
    ToolId,
)
from utils import *
from typing import List
import argparse


def fetch_tool_for_guideline(guideline: Guideline, guidelines: List) -> str:
    """Given a guideline which is already added to a parlant agent, see if there is any tool that needs to be added to that guideline using the guidelines list and return the name of that tool

    Args:
        guideline (Guideline): A guideline attached to an agent in parlant
        guidelines (List): A list of guidelines containing the tool information which are fetched from a json file

    Returns:
        str: Name of the tool to be attached to the fetched Guideline object
    """
    condition = guideline.condition
    action = guideline.action

    selected_guideline = [
        x
        for x in guidelines
        if ((x["condition"] == condition) and (x["action"] == action))
    ]
    print(selected_guideline)

    if selected_guideline:
        return selected_guideline[0]["tool"]
    return ""


def attach_tools(agent_id: str):
    # Get the config
    config = get_config()

    # Get all the guidelines
    guidelines_json = get_guidelines()[config["bot"]]

    # Get all the guidelines attached to a particular agent
    client = ParlantClient(base_url=config["server_address"])
    guidelines_client = client.guidelines.list(agent_id=agent_id)
    
    for guideline in guidelines_client:       
        # Fetch the tool name to be associated with this given guideline from the json list 
        retrieved_tool_name = fetch_tool_for_guideline(guideline, guidelines_json)

        if retrieved_tool_name:
            print(f"Tool fetched: {retrieved_tool_name}")
            
            # Check the existing tool associations and do not add the tool multiple times if it has already been added
            guideline_with_associations = client.guidelines.retrieve(agent_id = agent_id, guideline_id = guideline.id)

            associated_tools = guideline_with_associations.tool_associations
            associated_tool_names = set([tool.tool_id.tool_name for tool in associated_tools])

            if retrieved_tool_name in associated_tool_names:
                print(f"Tool {retrieved_tool_name} is already associated with the guideline {guideline.id}")
                continue

            client.guidelines.update(
                agent_id=agent_id,
                guideline_id=guideline.id,
                tool_associations=GuidelineToolAssociationUpdateParams(
                    add=[
                        ToolId(
                            service_name=config["service_name"],
                            tool_name=retrieved_tool_name,
                        ),
                    ],
                ),
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Attach tools to guidelines")
    parser.add_argument(
        "--agent-id",
        type=str,
        help="The ID of the agent to which the tools for respective guidelines will be added.",
    )
    args = parser.parse_args()
    attach_tools(args.agent_id)
    print("Attached tools")
