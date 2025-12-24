"""
Parser for SKILL.md files following Anthropic Agent Skills specification.
"""

import hashlib
import re
from pathlib import Path

import yaml

from core.skill.entities import SkillContent, SkillMetadata, SkillScript


class SkillParseError(Exception):
    """Error parsing SKILL.md file."""

    pass


class SkillParser:
    """Parser for SKILL.md files with YAML frontmatter."""

    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

    @classmethod
    def parse(cls, content: str) -> tuple[SkillMetadata, str]:
        """
        Parse SKILL.md content into metadata and markdown body.

        Args:
            content: Raw SKILL.md file content

        Returns:
            Tuple of (SkillMetadata, markdown_body)

        Raises:
            SkillParseError: If parsing fails
        """
        match = cls.FRONTMATTER_PATTERN.match(content)
        if not match:
            raise SkillParseError("Invalid SKILL.md: Missing YAML frontmatter (must start with ---)")

        yaml_content = match.group(1)
        markdown_body = content[match.end() :].strip()

        try:
            metadata_dict = yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError as e:
            raise SkillParseError(f"Invalid YAML frontmatter: {e}") from e

        # Handle allowed-tools (hyphenated in spec, snake_case in model)
        if "allowed-tools" in metadata_dict:
            tools_str = metadata_dict.pop("allowed-tools")
            metadata_dict["allowed_tools"] = tools_str.split() if isinstance(tools_str, str) else tools_str

        try:
            metadata = SkillMetadata.model_validate(metadata_dict)
        except Exception as e:
            raise SkillParseError(f"Invalid skill metadata: {e}") from e

        return metadata, markdown_body

    @classmethod
    def parse_directory(cls, skill_path: Path) -> SkillContent:
        """
        Parse a skill directory containing SKILL.md and optional subdirectories.

        Args:
            skill_path: Path to skill directory

        Returns:
            SkillContent with metadata, body, and scripts

        Raises:
            SkillParseError: If parsing fails
        """
        skill_md_path = skill_path / "SKILL.md"
        if not skill_md_path.exists():
            raise SkillParseError(f"No SKILL.md found in {skill_path}")

        content = skill_md_path.read_text(encoding="utf-8")
        metadata, body = cls.parse(content)

        # Discover scripts
        scripts = cls._discover_scripts(skill_path)

        # Generate content hash
        source_hash = cls._compute_hash(content, scripts)

        return SkillContent(
            metadata=metadata,
            body=body,
            scripts=scripts,
            source_hash=source_hash,
        )

    @classmethod
    def _discover_scripts(cls, skill_path: Path) -> list[SkillScript]:
        """Discover scripts in the scripts/ directory."""
        scripts_dir = skill_path / "scripts"
        if not scripts_dir.is_dir():
            return []

        scripts = []
        for script_file in scripts_dir.iterdir():
            if not script_file.is_file():
                continue

            language = cls._detect_language(script_file)
            if not language:
                continue

            scripts.append(
                SkillScript(
                    name=script_file.name,
                    path=f"scripts/{script_file.name}",
                    language=language,
                    description=None,  # Could parse from docstring later
                )
            )

        return scripts

    @classmethod
    def _detect_language(cls, script_file: Path) -> str | None:
        """Detect script language from extension."""
        ext_map = {
            ".py": "python3",
            ".js": "javascript",
            ".mjs": "javascript",
            ".sh": "bash",
            ".bash": "bash",
        }
        return ext_map.get(script_file.suffix.lower())

    @classmethod
    def _compute_hash(cls, content: str, scripts: list[SkillScript]) -> str:
        """Compute hash of skill content for change detection."""
        hasher = hashlib.sha256()
        hasher.update(content.encode("utf-8"))
        for script in sorted(scripts, key=lambda s: s.name):
            hasher.update(script.name.encode("utf-8"))
        return hasher.hexdigest()[:16]
