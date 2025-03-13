from agents.player.configuration import Configuration
from agents.player.schema import PlayerLlmResponseSchema
from util.langchain import load_chat_model
from typing import Dict, List, TypedDict, cast
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import AnyMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from util.langchain import add_messages_with_logging, AgentState

def call_model(
    state: AgentState, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the model with the given state and configuration."""
    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model).with_structured_output(PlayerLlmResponseSchema)
    
    response = cast(PlayerLlmResponseSchema, model.invoke([SystemMessage(content=state.system_prompt)] + state.messages, config))
    return {
        "messages": [AIMessage(content=response.content)], 
        "system_prompt": state.system_prompt
    }

def create_player_agent(checkpointer: MemorySaver):
    builder = StateGraph(state_schema=AgentState, config_schema=Configuration)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)

    return builder.compile(checkpointer=checkpointer, name="player")