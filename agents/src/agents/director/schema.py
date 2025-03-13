from pydantic import BaseModel,Field

class FinalOutput(BaseModel):
    situation: str
    assistant_actor_role: str
    user_role: str
    user_missions: dict[str, str]
    scenario: str
    
class ScriptWriterLlmResponseSchema(BaseModel):
    done: bool
    content: str
    final_output: FinalOutput = Field(default=None)
