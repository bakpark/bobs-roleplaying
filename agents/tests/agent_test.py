from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from agents.director.graph import create_director_agent
from agents.player.graph import create_player_agent
from agents.player.prompt import get_player_system_prompt
from agents.player.schema import sample_params

memory_saver = MemorySaver()


def test_director_agent(capsys):
    director_agent = create_director_agent(checkpointer=memory_saver)

    res = director_agent.invoke(
        input={
            "messages": [
                HumanMessage(content="I want to act in airport terminal scene.")
            ]
        },
        config={"configurable": {"thread_id": "1", "temperature": 1.0}},
    )


def test_player_agent(capsys):
    player_agent = create_player_agent(checkpointer=memory_saver)

    res = player_agent.ainvoke(
        input={
            "messages": [HumanMessage(content="Can I some order a caffe latte?")],
            "system_prompt": get_player_system_prompt(sample_params),
        },
        config={"configurable": {"thread_id": "1", "temperature": 0.2}},
    )
