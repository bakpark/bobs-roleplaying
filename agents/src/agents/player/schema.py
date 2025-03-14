import json
from pydantic import BaseModel
from typing import Dict, List, Literal

mission_ids = Literal["main", "sub", "hidden"]

class MissionItem(BaseModel):
    id: mission_ids
    success: bool
class ExpectedUserResponse(BaseModel):
    response: str
    difficulty: Literal["simple", "intermediate", "complex"]
    
class PlayerLlmResponseSchema(BaseModel):
    response: str
    missions: List[MissionItem]
    action: str
    expected_user_response: List[ExpectedUserResponse]

class ActingScriptSchema(BaseModel):
    situation: str
    assistant_actor_role: str
    user_role: str
    user_missions: Dict[mission_ids, str]
    def from_json_string(json_string: str) -> "ActingScriptSchema":
        return ActingScriptSchema(**json.loads(json_string))

# Sample params
sample_params = ActingScriptSchema(
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
        "sub": "Ask clearly about the ingredients of one menu item (e.g., Avocado Toast).",
        "hidden": "Attempt to get information about today's special pastry (not listed clearly on the menu)"
    }
)    