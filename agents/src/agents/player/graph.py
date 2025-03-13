from agents.player.state import State, InputState
from agents.player.configuration import Configuration
from agents.player.schema import PlayerLlmResponseSchema
from util.langchain import load_chat_model
from util.logging import logger
from typing import Dict, List, cast
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

    
def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the model with the given state and configuration."""
    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model).with_structured_output(PlayerLlmResponseSchema)
    
    response = cast(PlayerLlmResponseSchema, model.invoke([configuration.system_prompt] + state.messages, config))
    logger.info(f">> call_model > response: {response}")
    return {"messages": [AIMessage(content=response.content)]}

builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node(call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

graph = builder.compile(
    interrupt_before=[],
    interrupt_after=[]
)

graph.name = "player"