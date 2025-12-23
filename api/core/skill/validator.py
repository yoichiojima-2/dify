"""
Validator for Anthropic Agent Skills.
"""

import re

from core.skill.entities import SkillMetadata


class SkillValidationError(Exception):
    """Error validating skill."""

    pass


class SkillValidator:
    """Validator for skill metadata and content."""

    # Name must be lowercase alphanumeric and hyphens, no leading/trailing/consecutive hyphens
    NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

    @classmethod
    def validate_metadata(cls, metadata: SkillMetadata) -> list[str]:
        """
        Validate skill metadata according to the specification.

        Args:
            metadata: SkillMetadata to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate name format
        if not cls.NAME_PATTERN.match(metadata.name):
            errors.append(
                f"Invalid name '{metadata.name}': must be lowercase alphanumeric with hyphens, "
                "no leading/trailing/consecutive hyphens"
            )

        # Validate name length
        if len(metadata.name) > 64:
            errors.append(f"Name too long: {len(metadata.name)} > 64 characters")

        # Validate description
        if len(metadata.description) > 1024:
            errors.append(f"Description too long: {len(metadata.description)} > 1024 characters")

        # Validate compatibility length
        if metadata.compatibility and len(metadata.compatibility) > 500:
            errors.append(f"Compatibility too long: {len(metadata.compatibility)} > 500 characters")

        return errors

    @classmethod
    def validate(cls, metadata: SkillMetadata) -> None:
        """
        Validate skill metadata and raise if invalid.

        Args:
            metadata: SkillMetadata to validate

        Raises:
            SkillValidationError: If validation fails
        """
        errors = cls.validate_metadata(metadata)
        if errors:
            raise SkillValidationError("; ".join(errors))
