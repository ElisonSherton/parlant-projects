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

    # Get all the guidelines attached to a particular tool
    client = ParlantClient(base_url=config["server_address"])
    guidelines_client = client.guidelines.list(agent_id=agent_id)

    for guideline in guidelines_client:
        tool_name = fetch_tool_for_guideline(guideline, guidelines_json)
        if tool_name:
            print(f"Tool fetched: {tool_name}\n\n")
            client.guidelines.update(
                agent_id=agent_id,
                guideline_id=guideline.id,
                tool_associations=GuidelineToolAssociationUpdateParams(
                    add=[
                        ToolId(
                            service_name=config["service_name"],
                            tool_name=tool_name,
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
