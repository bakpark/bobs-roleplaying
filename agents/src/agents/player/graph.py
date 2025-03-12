from langgraph.graph import StateGraph, START, END
from .state import State, InputState
from .configuration import Configuration
from .util import load_chat_model, logger
from .dto import PlayerLlmResponse
from typing import Dict, List, cast
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

    
def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the model with the given state and configuration."""
    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model).with_structured_output(PlayerLlmResponse)
    
    response = cast(PlayerLlmResponse, model.invoke([configuration.system_prompt] + state.messages, config))
    logger.info(f">> call_model > response: {response}")
    return {"messages": [AIMessage(content=response.output)]}

builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node(call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

graph = builder.compile(
    interrupt_before=[],
    interrupt_after=[]
)
