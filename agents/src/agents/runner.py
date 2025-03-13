from agents.director import graph

while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit", "q"]:
        print("Good Bye")
        break
    for event in graph.stream({'messages':("user", user_input)}, config={"configurable": {"thread_id": "1", "temperature": 1}}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# from agents.player import graph
# from agents.player.prompt import get_player_system_prompt
# from agents.player.sample import params

# system_prompt = get_player_system_prompt(params)

# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["exit", "quit", "q"]:
#         print("Good Bye")
#         break
#     for event in graph.stream(
#         input={'messages':("user", user_input)}, 
#         config={"configurable": {"thread_id": "1", "model": "openai/gpt-4o-mini", "temperature": 0.2, "system_prompt": system_prompt}}
#         ):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)