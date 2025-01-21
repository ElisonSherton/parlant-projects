from collections.abc import Sequence
from typing import Literal, Optional
import httpx
from lagom import Container

from parlant.core.agents import Agent, AgentStore
from parlant.core.common import DefaultBaseModel
from parlant.core.contextual_correlator import ContextualCorrelator
from parlant.core.emissions import EmittedEvent, EventEmitter
from parlant.core.engines.alpha.hooks import LifecycleHookResult, LifecycleHooks
from parlant.core.engines.alpha.prompt_builder import PromptBuilder
from parlant.core.engines.types import Context
from parlant.core.guidelines import Guideline
from parlant.core.logging import Logger
from parlant.core.nlp.generation import SchematicGenerator
from parlant.core.nlp.service import NLPService
from parlant.core.sessions import Event, SessionStore, ToolResult


class FallbackClassification(DefaultBaseModel):
    """This is a schema that defines guided generation rules for a generative model,
    to do a proper classification of the conversation state and consequently
    for what would be the best strategy to fall back to in continuing it."""

    customer_inquiry: str
    evaluation_of_whether_customer_wants_general_information: str
    customer_wants_general_information: bool
    evaluation_of_whether_customer_wants_agent_to_help_with_a_particular_action: str
    customer_wants_agent_to_help_with_a_particular_action: bool
    which_is_it_more: Literal["information", "action", "indeterminate"]


logger: Logger
correlator: ContextualCorrelator
classifier: SchematicGenerator[FallbackClassification]
agent_store: AgentStore
session_store: SessionStore


async def classify_context(
    agent: Agent,
    interaction_history: Sequence[Event],
) -> FallbackClassification:
    classification_section = """\
You must seek to understand and classify the current state of the interaction, into one of 2 classes:
1) The customer wants an informative answer about some topic
2) The customer wants to agent to perform or help with some action, which is not just providing general FAQ-like information

Output a JSON object with the following structure:
{
  "customer_inquiry": "<fill this out - what is the customer's inquiry?>",
  "evaluation_of_whether_customer_wants_general_information": "<your evaluation here>",
  "customer_wants_general_information": <BOOL>,
  "evaluation_of_whether_customer_wants_agent_to_help_with_a_particular_action": "<your evaluation here>",
  "customer_wants_agent_to_help_with_a_particular_action": <BOOL>,
  "which_is_it_more": <either "information", "action", or "indeterminate" if you're really unsure>
}
"""

    prompt = (
        PromptBuilder()
        .add_agent_identity(agent)
        .add_section(classification_section)
        .add_interaction_history(interaction_history)
    ).build()

    generation_result = await classifier.generate(
        prompt,
        hints={"temperature": 0.2},
    )

    return generation_result.content


async def ask_qna(query: str) -> Optional[str]:
    async with httpx.AsyncClient(
        base_url="http://localhost:8807", timeout=30, follow_redirects=True
    ) as client:
        response = await client.post("/answers", json={"query": query})

        if not response.is_success:
            return None

        if answer := response.json()["answer"]:
            return str(answer)

    logger.warning(f"[CornerCasesModule] Failed to find an answer to '{query}'")

    return None


async def catch_corner_cases_before_generating_a_message(
    context: Context,
    event_emitter: EventEmitter,
    emitted_events: list[EmittedEvent],
    matched_guidelines: Sequence[Guideline],
) -> LifecycleHookResult:
    if matched_guidelines:
        return LifecycleHookResult.CALL_NEXT

    logger.warning("[CornerCasesModule] Caught a corner case")

    with logger.operation("[CornerCasesModule] Classifying interaction"):
        # Load the agent
        agent = await agent_store.read_agent(context.agent_id)

        # Load the interaction events, to use them for classification
        interaction_history = await session_store.list_events(
            session_id=context.session_id,
            kinds=[
                # We only need message and tool events for classification purposes
                "message",
                "tool",
            ],
        )

        classification = await classify_context(agent, interaction_history)

    match classification.which_is_it_more:
        case "action" | "indeterminate":
            logger.warning("[CornerCasesModule] Caught an unsupported action")

            await event_emitter.emit_message_event(
                correlation_id=correlator.correlation_id,
                data={
                    "message": "Sorry, I can't help you with this action. You may want to try phone support.",
                    "participant": {"display_name": agent.name},
                },
            )

            return LifecycleHookResult.BAIL

        case "information":
            answer = await ask_qna(classification.customer_inquiry)

            emitted_events.append(
                await event_emitter.emit_tool_event(
                    correlation_id=correlator.correlation_id,
                    data={
                        "tool_calls": [
                            {
                                "tool_id": "corner-case-qna",
                                "arguments": {"query": classification.customer_inquiry},
                                "result": {
                                    "data": answer or "No answer found",
                                    "metadata": {},
                                    "control": {},
                                },
                            }
                        ]
                    },
                )
            )

    return LifecycleHookResult.CALL_NEXT


async def initialize_module(container: Container) -> None:
    global logger, correlator, classifier, session_store, agent_store

    # Get and use the same logger and correlator as the server's
    logger = container[Logger]
    correlator = container[ContextualCorrelator]

    # Get some stores we'll need to access data
    agent_store = container[AgentStore]
    session_store = container[SessionStore]

    # Get an NLP schematic generator for our fallback classification schema
    classifier = await container[NLPService].get_schematic_generator(FallbackClassification)

    # Add custom logic to run just before the engine is about to try generating messages
    container[LifecycleHooks].on_generating_messages.append(
        catch_corner_cases_before_generating_a_message
    )


async def shutdown_module() -> None:
    pass
