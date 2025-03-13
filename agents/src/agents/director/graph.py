from typing import Annotated, TypedDict
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage
from langgraph.checkpoint.memory import MemorySaver

from agents.director.prompt import v2
from agents.director.schema import ScriptWriterLlmResponseSchema
from util.langchain import add_messages_with_logging

model = ChatAnthropic(model="claude-3-7-sonnet-latest", temperature=1.0)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages_with_logging]
    
script_writer_agent = create_react_agent(
    tools=[],
    model=model,
    name="script_writer_agent",
    prompt=v2["script_writer_prompt"],
    response_format=ScriptWriterLlmResponseSchema
)


memory = MemorySaver()

workflow = StateGraph(State)

workflow.add_node("script_writer_agent", script_writer_agent)

workflow.add_edge(START, "script_writer_agent")
workflow.add_edge("script_writer_agent", END)

graph = workflow.compile(checkpointer=memory)

graph.name = "director"