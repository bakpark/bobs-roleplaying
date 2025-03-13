"""Prompts for the player agent."""

from agents.player.schema import PlayerAgentSystemPromptParams
from langchain_core.prompts import PromptTemplate

system_prompt_template = PromptTemplate.from_template("""
    [Acting Script]
    Situation: {{situation}}
    Scenario: {{scenario}}
    Your Role: {{assistant_actor_role}}
    User Missions: 
    - main: {{main_mission}}
    - sub1: {{sub1_mission}}
    - sub2: {{sub2_mission}}
    - sub3: {{sub3_mission}}
    - hidden: {{hidden_mission}}
    
    [Instructions]
    1. Encourage the user to perform their missions without directly prompting responses that can be answered briefly or simply. For example, "Would you like less ice?" encourage special requests more naturally by saying, "Would you like anything else?" 
    2. If the user's response is not clear, ask for clarification.
    3. Generate three candidate responses as your character, then select the best one through a sampling vote
    4. Generate three plausible responses from the perspective of the counterpart role in the scenario.
    5. Do colloquial speech, like a real conversation
    """, 
    template_format="mustache"
    )

def get_player_system_prompt(params: PlayerAgentSystemPromptParams) -> str:
    return system_prompt_template.format(
        situation=params.situation,
        scenario=params.scenario,
        assistant_actor_role=params.assistant_actor_role,
        main_mission=params.user_missions["main"],
        sub1_mission=params.user_missions["sub1"],
        sub2_mission=params.user_missions["sub2"],
        sub3_mission=params.user_missions["sub3"],
        hidden_mission=params.user_missions["hidden"],
    )