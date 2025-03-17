from typing import Optional
from src.infra.db import get_script, update_script_info
from agents.translator import create_translator_agent
from agents.scriptwriter.schema import ScriptInfoSchema

translator_agent = create_translator_agent()


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
        translated.tags,
    )

    return translated
