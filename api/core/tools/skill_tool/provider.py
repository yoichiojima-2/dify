"""
Skill tool provider controller.
"""

from typing import Any, Self

from core.skill.entities import SkillScript
from core.tools.__base.tool_provider import ToolProviderController
from core.tools.__base.tool_runtime import ToolRuntime
from core.tools.entities.common_entities import I18nObject
from core.tools.entities.tool_entities import (
    ToolDescription,
    ToolEntity,
    ToolIdentity,
    ToolParameter,
    ToolProviderEntityWithPlugin,
    ToolProviderIdentity,
    ToolProviderType,
)
from core.tools.skill_tool.tool import SkillTool
from models.tools import SkillToolProvider


class SkillToolProviderController(ToolProviderController):
    """Controller for skill-based tool providers."""

    def __init__(
        self,
        entity: ToolProviderEntityWithPlugin,
        provider_id: str,
        tenant_id: str,
        skill_identifier: str,
        full_content: str,
        scripts: list[SkillScript],
    ):
        super().__init__(entity)
        self.entity: ToolProviderEntityWithPlugin = entity
        self.provider_id = provider_id
        self.tenant_id = tenant_id
        self.skill_identifier = skill_identifier
        self.full_content = full_content
        self.scripts = scripts

    @property
    def provider_type(self) -> ToolProviderType:
        return ToolProviderType.SKILL

    @classmethod
    def from_db(cls, db_provider: SkillToolProvider) -> Self:
        """Create controller from database model."""
        # Parse scripts from manifest
        scripts = [SkillScript.model_validate(s) for s in db_provider.scripts]

        # Build tool entities from scripts
        tools = []
        for script in scripts:
            tool_entity = ToolEntity(
                identity=ToolIdentity(
                    author=db_provider.author or "Anonymous",
                    name=script.name,
                    label=I18nObject(en_US=script.name, zh_Hans=script.name),
                    provider=db_provider.skill_identifier,
                    icon=db_provider.icon,
                ),
                parameters=[
                    ToolParameter(
                        name="input",
                        label=I18nObject(en_US="Input", zh_Hans="输入"),
                        type=ToolParameter.ToolParameterType.STRING,
                        form=ToolParameter.ToolParameterForm.LLM,
                        llm_description="Input data for the script",
                        required=False,
                    )
                ],
                description=ToolDescription(
                    human=I18nObject(
                        en_US=script.description or f"Execute {script.name}",
                        zh_Hans=script.description or f"执行 {script.name}",
                    ),
                    llm=script.description or f"Execute the {script.name} script from skill {db_provider.name}",
                ),
            )
            tools.append(tool_entity)

        provider_entity = ToolProviderEntityWithPlugin(
            identity=ToolProviderIdentity(
                author=db_provider.author or "Anonymous",
                name=db_provider.name,
                label=I18nObject(en_US=db_provider.name, zh_Hans=db_provider.name),
                description=I18nObject(en_US=db_provider.description, zh_Hans=db_provider.description),
                icon=db_provider.icon or "",
            ),
            plugin_id=None,
            credentials_schema=[],
            tools=tools,
        )

        return cls(
            entity=provider_entity,
            provider_id=db_provider.id,
            tenant_id=db_provider.tenant_id,
            skill_identifier=db_provider.skill_identifier,
            full_content=db_provider.full_content,
            scripts=scripts,
        )

    def _validate_credentials(self, user_id: str, credentials: dict[str, Any]):
        """Validate credentials - skills don't require credentials."""
        pass

    def get_tool(self, tool_name: str) -> SkillTool:
        """Get tool by name (script name)."""
        tool_entity = next(
            (t for t in self.entity.tools if t.identity.name == tool_name),
            None,
        )
        if not tool_entity:
            raise ValueError(f"Tool with name {tool_name} not found")

        script = next((s for s in self.scripts if s.name == tool_name), None)
        if not script:
            raise ValueError(f"Script with name {tool_name} not found")

        return SkillTool(
            entity=tool_entity,
            runtime=ToolRuntime(tenant_id=self.tenant_id),
            tenant_id=self.tenant_id,
            provider_id=self.provider_id,
            skill_identifier=self.skill_identifier,
            script=script,
        )

    def get_tools(self) -> list[SkillTool]:
        """Get all tools (scripts) from skill."""
        return [self.get_tool(script.name) for script in self.scripts]

    def get_context_injection(self, level: int = 1) -> str:
        """
        Get skill content for agent context injection.

        Level 1: Metadata only (name, description)
        Level 2: Full SKILL.md content
        """
        if level == 1:
            return f"Skill: {self.entity.identity.name}\nDescription: {self.entity.identity.description.en_US}"
        return self.full_content
