from typing import Annotated, Any, Dict, List, TypedDict, cast

from langchain_core.messages import AIMessage, AnyMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from util.langchain import add_messages_with_logging, load_chat_model

from agents.player.configuration import Configuration
from agents.player.schema import (
    ExpectedUserResponse,
    MissionItem,
    PlayerLlmResponseSchema,
)


class PlayerAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages_with_logging]
    missions: List[MissionItem]
    action: str
    expected_response: List[ExpectedUserResponse]


async def call_model(state: PlayerAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Call the model with the given state and configuration."""
    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model).with_structured_output(
        PlayerLlmResponseSchema
    )

    response = cast(
        PlayerLlmResponseSchema,
        await model.ainvoke(
            [SystemMessage(content=configuration.system_prompt)] + state["messages"],
            config,
        ),
    )
    return {
        "messages": [AIMessage(content=response.response)],
        "system_prompt": configuration.system_prompt,
        "missions": response.missions,
        "action": response.action,
        "expected_response": response.expected_user_response,
    }


def create_player_agent(checkpointer: MemorySaver):
    builder = StateGraph(state_schema=PlayerAgentState, config_schema=Configuration)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)

    return builder.compile(checkpointer=checkpointer, name="player")
