import json
from pydantic import BaseModel
from typing import Dict, List, Literal, TypedDict

class MissionItem(BaseModel):
    id: Literal["main", "sub1", "sub2", "sub3"]
    success: bool
    
class PlayerLlmResponseSchema(BaseModel):
    content: str
    missions: List[MissionItem]
    action: str
    counterpart_response: List[str]

class PlayerAgentSystemPromptParams(BaseModel):
    situation: str
    assistant_actor_role: str
    user_role: str
    user_missions: Dict[str, str]
    scenario: str
    def from_json_string(json_string: str) -> "PlayerAgentSystemPromptParams":
        return PlayerAgentSystemPromptParams(**json.loads(json_string))

# Sample params
sample_params = PlayerAgentSystemPromptParams(
    situation="""It's a typical busy weekday morning at `Sunrise Café.`
    Customers are lined up, hurried and eager to quickly grab their morning drinks and breakfast before heading to work. 
    The atmosphere is bustling, with coffee machines whirring and baristas swiftly taking orders. The café is well-known for quality coffee, freshly baked pastries, and healthy breakfast items. The menu, clearly displayed
    """,
    assistant_actor_role="""
    The café employee should greet the customer warmly but briskly due to the busy environment.
    Provide clear, concise answers about ingredients and accommodate dietary requests easily.
    When asked about today's special pastry, the employee should naturally and pleasantly mention the special pastry of the day, "Chocolate Almond Danish ($3.75)," even though it isn't clearly displayed on the menu.
    Politely confirm the customer's order and total cost before processing payment.
    Encourage efficiency but remain patient and approachable to help guide the customer naturally through the interaction.
    """,
    user_role="""
    You are a customer at `Sunrise Café`.
    """,
    user_missions={
        "main": "Successfully order breakfast items (at least one food item and one drink) clearly and pay correctly.",
        "sub1": "Ask clearly about the ingredients of one menu item (e.g., Avocado Toast).",
        "sub2": "Politely request an alternative milk option (e.g., oat milk) for the coffee order.",
        "sub3": "Confirm the total price verbally with the café employee before paying.",
        "hidden": "Attempt to get information about today's special pastry (not listed clearly on the menu)"
    },
    scenario="""
    You're managing a long line of busy morning customers at Sunrise Café, aiming to keep orders flowing smoothly. As each customer approaches, you greet them warmly and clearly to maintain efficiency. You listen attentively, answer customer inquiries about menu items or ingredients promptly and concisely, accommodate dietary preferences (such as alternative milk choices), and inform customers of today's special pastry ("Chocolate Almond Danish") if subtly asked. 
    You clearly confirm the customer's order and state the total amount due before payment, ensuring a smooth and friendly interaction. 
    Your goal is to provide efficient, friendly customer service while guiding each interaction calmly and professionally, keeping the line moving quickly without making customers feel rushed.
    """
)    