import asyncio
import uuid

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agents.director.graph import create_director_agent
from agents.director.schema.schema import DirectorState


async def call(
    input: str,
    prev_messages: list[BaseMessage] = [],
    thread_id: str = str(uuid.uuid4()),
):
    async with AsyncSqliteSaver.from_conn_string("tmp.db") as conn:
        director_agent = create_director_agent(checkpointer=conn)
        res = await director_agent.ainvoke(
            input={"messages": prev_messages + [HumanMessage(content=input)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return res


if __name__ == "__main__":
    prev_messages = DirectorState.get_initial_state()["messages"]
    thread_id = str(uuid.uuid4())
    while True:
        user_input = input("User: ")
        if user_input == "q" or user_input == "quit":
            break
        res = asyncio.run(call(user_input, prev_messages, thread_id))
        prev_messages = []  # add in first
        print("RUNNER MESSAGE: ", res)
