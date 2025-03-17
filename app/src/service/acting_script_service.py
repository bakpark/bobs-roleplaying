from src.infra.db import get_acting_script, insert_acting_script
from agents.translator import create_translator_agent
from agents.scriptwriter.schema import ActingScriptSchema

translator_agent = create_translator_agent()


async def _translate_acting_script(
    json_string: str, src_language: str, dist_language: str
) -> ActingScriptSchema:
    result = await translator_agent.ainvoke(
        {
            "original": json_string,
            "output_schema": ActingScriptSchema,
            "src_language": src_language,
            "dist_language": dist_language,
        },
    )
    return result["output"]


async def get_or_translate_acting_script(
    scenario_id: str, language: str = "kr"
) -> ActingScriptSchema:
    json_string = await get_acting_script(scenario_id, language)
    if not json_string is None:
        return ActingScriptSchema.from_json_string(json_string)

    origin_language = "en"
    if origin_language == language:
        return None

    json_string = await get_acting_script(scenario_id, origin_language)
    if json_string is None:
        return None

    translated = await _translate_acting_script(json_string, origin_language, language)

    # Save translated script to db
    await insert_acting_script(scenario_id, translated.model_dump_json(), language)

    return translated
