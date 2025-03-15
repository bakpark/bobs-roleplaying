import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import (AIMessage, AnyMessage, HumanMessage,
                                     RemoveMessage, SystemMessage)
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langsmith import traceable

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

model = ChatGroq(groq_api_key=groq_key, model="llama-3.2-3b-preview")


class State(MessagesState):
    summary: str


def call_model(state: State):
    summary = state.get("summary", "")
    if summary:
        system_message = (
            f"Summary of our previous conversation that you wrote. Summary: {summary}"
        )
        response = model.invoke(
            [SystemMessage(content=system_message)] + state["messages"]
        )
    else:
        response = model.invoke(state["messages"])
    return {"messages": [AIMessage(content=response.content)]}


def summarize(state: State):
    summary = state.get("summary", "")
    # Create our summarization prompt
    if summary:
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)
    print(f">> summarize > response: {response}")
    remove_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": response.content, "messages": remove_messages}


# Determine whether to end or summarize the conversation
def should_continue(state: State):
    """Return the next node to execute."""
    # If there are more than four messages, then we summarize the conversation
    if len(state["messages"]) > 4:
        return "summarize"

    # Otherwise we can just end
    return END


workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node("summarize", summarize)

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges(
    "conversation", should_continue, {"summarize": "summarize", END: END}
)
workflow.add_edge("summarize", END)

memory = MemorySaver()
compiled = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}
while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit", "q"]:
        print("Good Bye")
        break
    for event in compiled.stream(
        {"messages": [HumanMessage(content=user_input)]}, config
    ):
        for value in event.values():
            print(value["messages"])
            print("Assistant:", value["messages"][-1].content)
