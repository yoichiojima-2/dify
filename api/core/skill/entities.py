"""
Skill entities for Anthropic Agent Skills specification.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SkillSourceType(StrEnum):
    """Source type for skill installation."""

    GIT = "git"
    UPLOAD = "upload"
    PATH = "path"


class SkillScript(BaseModel):
    """Script definition from scripts/ directory."""

    name: str = Field(..., description="Script filename")
    path: str = Field(..., description="Relative path from skill root")
    language: str = Field(..., description="Script language: python3, javascript, bash")
    description: str | None = Field(default=None, description="Script description")
    content: str | None = Field(default=None, description="Script content (loaded on demand)")


class SkillMetadata(BaseModel):
    """
    Metadata from SKILL.md frontmatter.
    Follows Anthropic Agent Skills specification.
    """

    name: str = Field(..., min_length=1, max_length=64, description="Skill identifier (lowercase, hyphens)")
    description: str = Field(..., min_length=1, max_length=1024, description="Skill description")
    license: str | None = Field(default=None, description="License name or reference")
    compatibility: str | None = Field(default=None, max_length=500, description="Environment requirements")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    allowed_tools: list[str] = Field(default_factory=list, description="Pre-approved tools (experimental)")


class SkillContent(BaseModel):
    """
    Complete skill content after parsing.
    """

    metadata: SkillMetadata
    body: str = Field(..., description="Markdown body after frontmatter")
    scripts: list[SkillScript] = Field(default_factory=list, description="Scripts from scripts/ directory")
    source_hash: str = Field(..., description="Hash of skill content for change detection")
