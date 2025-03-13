from agents.player.configuration import Configuration
from agents.player.schema import MissionItem, PlayerLlmResponseSchema
from util.langchain import load_chat_model
from typing import Annotated, Dict, List, TypedDict, cast
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, SystemMessage, AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from util.langchain import add_messages_with_logging
from util.logging import logger

class PlayerAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages_with_logging]
    missions: List[MissionItem]
    action: str
    counterpart_response: List[str]
    
    
def call_model(
    state: PlayerAgentState, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the model with the given state and configuration."""
    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model).with_structured_output(PlayerLlmResponseSchema)
    
    logger.info(f"System prompt: {configuration.system_prompt}")
    response = cast(
        PlayerLlmResponseSchema, 
        model.invoke(
            [SystemMessage(content=configuration.system_prompt)] + state["messages"], 
            config
        )
    )
    return {
        "messages": [AIMessage(content=response.content)], 
        "system_prompt": configuration.system_prompt,
        "missions": response.missions,
        "action": response.action,
        "counterpart_response": response.counterpart_response
    }

def create_player_agent(checkpointer: MemorySaver):
    builder = StateGraph(state_schema=PlayerAgentState, config_schema=Configuration)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)

    return builder.compile(checkpointer=checkpointer, name="player")