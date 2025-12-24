"""
Skill tool for executing skill scripts.
"""

import logging
from collections.abc import Generator
from typing import Any

from core.helper.code_executor.code_executor import CodeExecutionError, CodeExecutor, CodeLanguage
from core.skill.entities import SkillScript
from core.tools.__base.tool import Tool
from core.tools.__base.tool_runtime import ToolRuntime
from core.tools.entities.tool_entities import ToolEntity, ToolInvokeMessage, ToolProviderType
from core.tools.errors import ToolInvokeError

logger = logging.getLogger(__name__)


class SkillTool(Tool):
    """Tool that executes skill scripts via sandbox."""

    LANGUAGE_MAP = {
        "python3": CodeLanguage.PYTHON3,
        "python": CodeLanguage.PYTHON3,
        "javascript": CodeLanguage.JAVASCRIPT,
        "js": CodeLanguage.JAVASCRIPT,
    }

    def __init__(
        self,
        entity: ToolEntity,
        runtime: ToolRuntime,
        tenant_id: str,
        provider_id: str,
        skill_identifier: str,
        script: SkillScript,
    ):
        super().__init__(entity, runtime)
        self.tenant_id = tenant_id
        self.provider_id = provider_id
        self.skill_identifier = skill_identifier
        self.script = script

    def tool_provider_type(self) -> ToolProviderType:
        return ToolProviderType.SKILL

    def _invoke(
        self,
        user_id: str,
        tool_parameters: dict[str, Any],
        conversation_id: str | None = None,
        app_id: str | None = None,
        message_id: str | None = None,
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Execute the script in sandbox."""
        if not self.script.content:
            raise ToolInvokeError(f"Script content not loaded for {self.script.name}")

        language = self._get_code_language()
        if not language:
            raise ToolInvokeError(f"Unsupported script language: {self.script.language}")

        # Prepare script with input parameters
        code = self._prepare_script(tool_parameters)

        try:
            result = CodeExecutor.execute_code(
                language=language,
                preload="",
                code=code,
            )
            yield self.create_text_message(result)
        except CodeExecutionError as e:
            raise ToolInvokeError(f"Script execution failed: {e}") from e

    def _get_code_language(self) -> CodeLanguage | None:
        """Get CodeLanguage from script language string."""
        return self.LANGUAGE_MAP.get(self.script.language.lower())

    def _prepare_script(self, tool_parameters: dict[str, Any]) -> str:
        """Prepare script code with input parameters."""
        code = self.script.content or ""

        # Inject input as a variable if provided
        input_value = tool_parameters.get("input", "")
        if input_value and self.script.language in ("python3", "python"):
            # For Python, inject as a variable
            code = f'INPUT = """{input_value}"""\n\n{code}'
        elif input_value and self.script.language in ("javascript", "js"):
            # For JavaScript, inject as a variable
            escaped = input_value.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
            code = f"const INPUT = `{escaped}`;\n\n{code}"

        return code

    def fork_tool_runtime(self, runtime: ToolRuntime) -> "SkillTool":
        """Create a new instance with different runtime."""
        return SkillTool(
            entity=self.entity,
            runtime=runtime,
            tenant_id=self.tenant_id,
            provider_id=self.provider_id,
            skill_identifier=self.skill_identifier,
            script=self.script,
        )
