from typing import Optional
from pydantic import BaseModel, Field
from src.infra.db import (
    delete_script_by_email_and_script_id,
    get_script,
    get_script_list,
    update_script_info,
)
from agents.translator import create_translator_agent
from agents.scriptwriter.schema import ActingScriptSchema

translator_agent = create_translator_agent()


class ScriptInfoSchema(BaseModel):
    script: ActingScriptSchema = Field(
        ...,
        description="The script of the scenario, translated",
    )
    title: str = Field(
        ...,
        description="The title of the scenario, translated. It should be 8 words or less.",
    )
    description: str = Field(
        ...,
        description="The captivating overview of the scenario, which has been translated. It should be presented in two sentences.",
    )
    tags: list[str] = Field(
        ...,
        description="A list of 3 key descriptors that define the scenario. It must include one conversation format (e.g., casual talk), one mood (e.g., ordinary), translated.",
    )

    def to_script_message(self) -> str:
        return f"""{self.title}
- {self.description}

[Situation]
{self.script.situation}

[Your Role]
{self.script.user_role}

[Counterpart Role]
{self.script.assistant_actor_role}

[Your Missions]
main: {self.script.user_missions.main}
sub: {self.script.user_missions.sub}
hidden: {self.script.user_missions.hidden}
"""


class BriefScriptInfoSchema(BaseModel):
    script_id: int
    title: str
    description: str
    tags: list[str]


async def _translate_script_info(
    json_string: str, src_language: str, dist_language: str
) -> ScriptInfoSchema:
    result = await translator_agent.ainvoke(
        {
            "original": json_string,
            "output_schema": ScriptInfoSchema,
            "src_language": src_language,
            "dist_language": dist_language,
        },
    )
    return result["output"]


async def get_or_translate_script_info(
    script_id: str, language: str = "kr"
) -> Optional[ScriptInfoSchema]:
    script_info = await get_script(script_id)
    if script_info is None:
        return None

    # 번역 필요 없으면 그냥 반환
    if script_info["translated_language"] == language:
        return ScriptInfoSchema.model_validate_json(script_info["translated_json"])

    origin_language = "en"
    translated = await _translate_script_info(
        script_info["script_json"], origin_language, language
    )

    # Save translated script to db
    await update_script_info(
        script_id,
        translated.model_dump_json(),
        language,
        translated.description,
        ",".join(translated.tags),
    )

    return translated


async def get_user_scripts(
    email: str, language: str = "kr"
) -> list[BriefScriptInfoSchema]:
    script_list = await get_script_list(email)
    scripts = []
    for script_id in script_list:
        script_info = await get_or_translate_script_info(script_id, language)
        scripts.append(
            BriefScriptInfoSchema(
                script_id=script_id,
                title=script_info.title,
                description=script_info.description,
                tags=script_info.tags,
            )
        )
    return scripts


async def delete_script(email: str, script_id: int):
    await delete_script_by_email_and_script_id(email, script_id)
