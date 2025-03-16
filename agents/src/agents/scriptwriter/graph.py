from typing import cast

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from util.langchain import AgentState

from agents.scriptwriter.prompt import scriptwriter_system_prompt
from agents.scriptwriter.schema import ActingScriptSchema

model = ChatAnthropic(
    model="claude-3-7-sonnet-latest", temperature=1.0
).with_structured_output(ActingScriptSchema)


def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    response = cast(
        ActingScriptSchema,
        model.invoke(
            input=[SystemMessage(content=scriptwriter_system_prompt["v2"])]
            + state["messages"],
            config=config,
        ),
    )

    return {
        "messages": [AIMessage(content=response.model_dump_json())],
    }


async def async_call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    response = cast(
        ActingScriptSchema,
        await model.ainvoke(
            input=[SystemMessage(content=scriptwriter_system_prompt["v2"])]
            + state["messages"],
            config=config,
        ),
    )

    return {
        "messages": [AIMessage(content=response.model_dump_json())],
    }


def create_scriptwriter_agent(checkpointer: MemorySaver):
    """
    Create a acting script for a two-person dialogue.
    """
    workflow = StateGraph(state_schema=AgentState)

    workflow.add_node("script_writer_agent", call_model)

    workflow.add_edge(START, "script_writer_agent")
    workflow.add_edge("script_writer_agent", END)

    return workflow.compile(checkpointer=checkpointer, name="scriptwriter")
