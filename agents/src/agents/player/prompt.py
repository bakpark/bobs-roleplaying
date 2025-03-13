"""Prompts for the player agent."""

from agents.player.schema import PlayerAgentSystemPromptParams
from langchain_core.prompts import PromptTemplate

system_prompt_template = PromptTemplate.from_template("""
    Situation: {{situation}}
    
    Role: {{role}}
    
    Information: {{information}}
    
    User Missions: {{missions}}
    
    Scenario: {{scenario}}
    
    Behavioral Guidelines: {{guidelines}}
    
    Instructions:
    1. Encourage the user to perform their missions without directly prompting responses that can be answered briefly or simply. For example, "Would you like less ice?" encourage special requests more naturally by saying, "Would you like anything else?" 
    2. If the user's response is not clear, ask for clarification.
    3. Generate three candidate responses as your character, then select the best one through a sampling vote
    4. Generate three plausible responses from the perspective of the counterpart role.
    5. Do colloquial speech, like a real conversation
    """, 
    template_format="mustache"
    )

def get_player_system_prompt(params: PlayerAgentSystemPromptParams) -> str:
    return system_prompt_template.format(
        situation=params.situation,
        role=params.role,
        information=params.information,
        missions=params.missions,
        scenario=params.scenario,
    )