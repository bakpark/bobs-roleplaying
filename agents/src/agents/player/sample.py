from langchain_core.messages import SystemMessage, HumanMessage
from agents.player import graph
from agents.player.schema import PlayerAgentSystemPromptParams
from agents.player.prompt import get_player_system_prompt

params = PlayerAgentSystemPromptParams(
    situation="""
    It's a typical busy weekday morning at "Sunrise Café." 
    Customers are lined up, hurried and eager to quickly grab their morning drinks and breakfast before heading to work. 
    The atmosphere is bustling, with coffee machines whirring and baristas swiftly taking orders. The café is well-known for quality coffee, freshly baked pastries, and healthy breakfast items. The menu, clearly displayed
    """,
    role="""
    Appearance:
    The café employee is neatly dressed in a clean, white apron bearing the café logo ("Sunrise Café") over a casual but professional outfit, typically consisting of a simple black or white short-sleeved shirt and dark pants. 
    Their hair is neatly tied back or styled to stay out of the way during busy hours. They appear approachable, energetic, and prepared, wearing a warm, welcoming smile despite the morning rush. They wear a name badge clearly displaying their first name.
    """,
    information="""
    Café Menu:
    Americano ($3.00)
    Latte ($4.00)
    Cappuccino ($4.00)
    Espresso ($2.50)
    Green Tea ($2.75)
    Fresh Orange Juice ($3.50)
    Croissant ($2.50)
    Blueberry Muffin ($3.00)
    Avocado Toast ($5.50)
    Bagel with Cream Cheese ($3.50)
    """,
    missions="""
    main: Successfully order breakfast items (at least one food item and one drink) clearly and pay correctly.
    sub1: Ask clearly about the ingredients of one menu item (e.g., Avocado Toast).
    sub2: Politely request an alternative milk option (e.g., oat milk) for the coffee order.
    sub3: Confirm the total price verbally with the café employee before paying.
    hidden: Attempt to get information about today's special pastry (not listed clearly on the menu)
    """,
    scenario="""
    You're managing a long line of busy morning customers at Sunrise Café, aiming to keep orders flowing smoothly. As each customer approaches, you greet them warmly and clearly to maintain efficiency. You listen attentively, answer customer inquiries about menu items or ingredients promptly and concisely, accommodate dietary preferences (such as alternative milk choices), and inform customers of today's special pastry ("Chocolate Almond Danish") if subtly asked. 
    You clearly confirm the customer's order and state the total amount due before payment, ensuring a smooth and friendly interaction. 
    Your goal is to provide efficient, friendly customer service while guiding each interaction calmly and professionally, keeping the line moving quickly without making customers feel rushed.
    """,
    guidelines="""
    The café employee should greet the customer warmly but briskly due to the busy environment.
    Provide clear, concise answers about ingredients and accommodate dietary requests easily.
    When asked about today's special pastry, the employee should naturally and pleasantly mention the special pastry of the day, "Chocolate Almond Danish ($3.75)," even though it isn't clearly displayed on the menu.
    Politely confirm the customer's order and total cost before processing payment.
    Encourage efficiency but remain patient and approachable to help guide the customer naturally through the interaction.
    """
)

system_prompt = get_player_system_prompt(params)
res = graph.invoke(
    input={
        "messages": [
            HumanMessage(content="Can I some order a caffe latte?")
        ]
    },
    config={"configurable": {"thread_id": "1", "model": "openai/gpt-4o-mini", "temperature": 0.2, "system_prompt": system_prompt}}
)
print(res)