"""Define the configurable parameters for the agent."""

from dataclasses import dataclass, field, fields
from typing import Optional

from langchain_core.runnables import RunnableConfig, ensure_config
from typing_extensions import Annotated


@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""

    system_prompt: str = (
        field(
            default="You are a role-playing player.",
            metadata={"description": "The system prompt to use for the player agent."},
        ),
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

    temperature: float = field(
        default=0.2,
        metadata={
            "description": "The temperature to use for the player agent's model."
        },
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig object."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
