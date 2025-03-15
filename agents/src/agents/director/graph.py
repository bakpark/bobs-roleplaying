from typing import Any, Type

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from agents.director.prompt import v2
from util.langchain import LoggableState


def create_director_agent(
    state_schema: Type[Any] = LoggableState, checkpointer: MemorySaver = None
):
    model = ChatAnthropic(model="claude-3-7-sonnet-latest", temperature=1.0)
    script_writer_agent = create_react_agent(
        tools=[],
        model=model,
        name="script_writer_agent",
        prompt=v2["script_writer_prompt"],
    )

    workflow = StateGraph(state_schema=state_schema)

    workflow.add_node("script_writer_agent", script_writer_agent)

    workflow.add_edge(START, "script_writer_agent")
    workflow.add_edge("script_writer_agent", END)

    return workflow.compile(checkpointer=checkpointer, name="director")
