"""
Unit tests for skill parser and validator.
"""

from pathlib import Path

import pytest

from core.skill.entities import SkillMetadata
from core.skill.parser import SkillParseError, SkillParser
from core.skill.validator import SkillValidationError, SkillValidator


class TestSkillParser:
    """Tests for SkillParser."""

    def test_parse_valid_skill(self):
        """Test parsing a valid SKILL.md with all fields."""
        content = """---
name: pdf-processing
description: Extract text and tables from PDF files.
license: Apache-2.0
compatibility: Requires python3
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Bash(git:*) Read
---

# PDF Processing

This skill helps with PDF operations.
"""
        metadata, body = SkillParser.parse(content)

        assert metadata.name == "pdf-processing"
        assert metadata.description == "Extract text and tables from PDF files."
        assert metadata.license == "Apache-2.0"
        assert metadata.compatibility == "Requires python3"
        assert metadata.metadata == {"author": "example-org", "version": "1.0"}
        assert metadata.allowed_tools == ["Bash(git:*)", "Read"]
        assert "# PDF Processing" in body

    def test_parse_minimal_skill(self):
        """Test parsing a minimal SKILL.md with only required fields."""
        content = """---
name: simple-skill
description: A simple skill.
---

Instructions here.
"""
        metadata, body = SkillParser.parse(content)

        assert metadata.name == "simple-skill"
        assert metadata.description == "A simple skill."
        assert metadata.license is None
        assert metadata.compatibility is None
        assert metadata.metadata == {}
        assert metadata.allowed_tools == []
        assert body == "Instructions here."

    def test_parse_missing_frontmatter(self):
        """Test that missing frontmatter raises error."""
        content = """# No frontmatter

Just markdown content.
"""
        with pytest.raises(SkillParseError, match="Missing YAML frontmatter"):
            SkillParser.parse(content)

    def test_parse_invalid_yaml(self):
        """Test that invalid YAML raises error."""
        content = """---
name: test
description: [invalid yaml
---
"""
        with pytest.raises(SkillParseError, match="Invalid YAML"):
            SkillParser.parse(content)

    def test_parse_missing_required_field(self):
        """Test that missing required fields raise error."""
        content = """---
name: test-skill
---

Missing description.
"""
        with pytest.raises(SkillParseError, match="Invalid skill metadata"):
            SkillParser.parse(content)

    def test_parse_directory(self, tmp_path: Path):
        """Test parsing a skill directory."""
        # Create skill directory structure
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: Test skill description.
---

Test instructions.
""")

        # Create scripts directory
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "process.py").write_text("# Python script")
        (scripts_dir / "helper.js").write_text("// JS script")

        skill_content = SkillParser.parse_directory(tmp_path)

        assert skill_content.metadata.name == "test-skill"
        assert skill_content.body == "Test instructions."
        assert len(skill_content.scripts) == 2

        script_names = {s.name for s in skill_content.scripts}
        assert "process.py" in script_names
        assert "helper.js" in script_names

        # Check languages detected
        py_script = next(s for s in skill_content.scripts if s.name == "process.py")
        assert py_script.language == "python3"

        js_script = next(s for s in skill_content.scripts if s.name == "helper.js")
        assert js_script.language == "javascript"

    def test_parse_directory_no_skill_md(self, tmp_path: Path):
        """Test that missing SKILL.md raises error."""
        with pytest.raises(SkillParseError, match="No SKILL.md found"):
            SkillParser.parse_directory(tmp_path)

    def test_compute_hash_consistency(self):
        """Test that hash is consistent for same content."""
        content = """---
name: test
description: Test.
---

Content.
"""
        metadata1, body1 = SkillParser.parse(content)
        metadata2, body2 = SkillParser.parse(content)

        hash1 = SkillParser._compute_hash(content, [])
        hash2 = SkillParser._compute_hash(content, [])

        assert hash1 == hash2


class TestSkillValidator:
    """Tests for SkillValidator."""

    def test_validate_valid_name(self):
        """Test that valid names pass validation."""
        valid_names = [
            "pdf",
            "pdf-processing",
            "my-skill-v1",
            "a1b2c3",
            "skill123",
        ]
        for name in valid_names:
            metadata = SkillMetadata(name=name, description="Valid skill.")
            errors = SkillValidator.validate_metadata(metadata)
            assert errors == [], f"Name '{name}' should be valid"

    def test_validate_invalid_name(self):
        """Test that invalid names fail validation."""
        invalid_names = [
            "PDF-Processing",  # uppercase
            "-pdf",  # leading hyphen
            "pdf-",  # trailing hyphen
            "pdf--processing",  # consecutive hyphens
            "pdf_processing",  # underscore
            "pdf.processing",  # dot
        ]
        for name in invalid_names:
            metadata = SkillMetadata(name=name, description="Invalid skill.")
            errors = SkillValidator.validate_metadata(metadata)
            assert len(errors) > 0, f"Name '{name}' should be invalid"

    def test_validate_name_too_long(self):
        """Test that name over 64 chars fails at Pydantic level."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="at most 64 characters"):
            SkillMetadata(name="a" * 65, description="Test.")

    def test_validate_description_too_long(self):
        """Test that description over 1024 chars fails at Pydantic level."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="at most 1024 characters"):
            SkillMetadata(name="test", description="a" * 1025)

    def test_validate_compatibility_too_long(self):
        """Test that compatibility over 500 chars fails at Pydantic level."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="at most 500 characters"):
            SkillMetadata(name="test", description="Test.", compatibility="a" * 501)

    def test_validate_raises_on_error(self):
        """Test that validate() raises SkillValidationError."""
        metadata = SkillMetadata(name="INVALID", description="Test.")
        with pytest.raises(SkillValidationError):
            SkillValidator.validate(metadata)

    def test_validate_passes_for_valid(self):
        """Test that validate() passes for valid metadata."""
        metadata = SkillMetadata(name="valid-skill", description="A valid skill.")
        SkillValidator.validate(metadata)  # Should not raise
