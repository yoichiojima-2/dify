"""
Service for managing skill tool providers.
"""

import json
import tempfile
import zipfile
from pathlib import Path

from sqlalchemy.orm import Session

from core.skill.entities import SkillSourceType
from core.skill.parser import SkillParseError, SkillParser
from core.skill.validator import SkillValidationError, SkillValidator
from models.tools import SkillToolProvider


class SkillToolManageError(Exception):
    """Error managing skill tools."""

    pass


class SkillToolManageService:
    """Service for managing skill tool providers."""

    def __init__(self, session: Session):
        self.session = session

    def install_from_path(
        self,
        tenant_id: str,
        user_id: str,
        path: str,
        name: str | None = None,
    ) -> SkillToolProvider:
        """
        Install skill from local directory path.

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            path: Path to skill directory
            name: Optional display name (defaults to skill name)

        Returns:
            Created SkillToolProvider
        """
        skill_path = Path(path)
        if not skill_path.is_dir():
            raise SkillToolManageError(f"Path is not a directory: {path}")

        skill_content = SkillParser.parse_directory(skill_path)
        SkillValidator.validate(skill_content.metadata)

        return self._create_provider(
            tenant_id=tenant_id,
            user_id=user_id,
            skill_content=skill_content,
            source_type=SkillSourceType.PATH,
            source_url=path,
            name=name,
            skill_path=skill_path,
        )

    def install_from_upload(
        self,
        tenant_id: str,
        user_id: str,
        file_content: bytes,
        filename: str,
        name: str | None = None,
    ) -> SkillToolProvider:
        """
        Install skill from uploaded zip file.

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            file_content: Zip file content
            filename: Original filename
            name: Optional display name

        Returns:
            Created SkillToolProvider
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / filename

            # Write uploaded file
            zip_path.write_bytes(file_content)

            # Extract zip
            extract_path = temp_path / "extracted"
            extract_path.mkdir()

            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_path)
            except zipfile.BadZipFile as e:
                raise SkillToolManageError(f"Invalid zip file: {e}") from e

            # Find skill directory (may be nested)
            skill_path = self._find_skill_dir(extract_path)
            if not skill_path:
                raise SkillToolManageError("No SKILL.md found in uploaded archive")

            skill_content = SkillParser.parse_directory(skill_path)
            SkillValidator.validate(skill_content.metadata)

            return self._create_provider(
                tenant_id=tenant_id,
                user_id=user_id,
                skill_content=skill_content,
                source_type=SkillSourceType.UPLOAD,
                source_url=None,
                name=name,
                skill_path=skill_path,
            )

    def install_from_git(
        self,
        tenant_id: str,
        user_id: str,
        git_url: str,
        branch: str = "main",
        name: str | None = None,
    ) -> SkillToolProvider:
        """
        Install skill from Git repository.

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            git_url: Git repository URL
            branch: Branch to clone
            name: Optional display name

        Returns:
            Created SkillToolProvider
        """
        try:
            from git import Repo
        except ImportError as e:
            raise SkillToolManageError("GitPython not installed. Run: pip install GitPython") from e

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                Repo.clone_from(git_url, temp_path, branch=branch, depth=1)
            except Exception as e:
                raise SkillToolManageError(f"Failed to clone repository: {e}") from e

            # Find skill directory
            skill_path = self._find_skill_dir(temp_path)
            if not skill_path:
                raise SkillToolManageError("No SKILL.md found in repository")

            skill_content = SkillParser.parse_directory(skill_path)
            SkillValidator.validate(skill_content.metadata)

            return self._create_provider(
                tenant_id=tenant_id,
                user_id=user_id,
                skill_content=skill_content,
                source_type=SkillSourceType.GIT,
                source_url=git_url,
                name=name,
                skill_path=skill_path,
            )

    def _find_skill_dir(self, root: Path) -> Path | None:
        """Find directory containing SKILL.md."""
        if (root / "SKILL.md").exists():
            return root
        for child in root.iterdir():
            if child.is_dir():
                result = self._find_skill_dir(child)
                if result:
                    return result
        return None

    def _create_provider(
        self,
        tenant_id: str,
        user_id: str,
        skill_content,
        source_type: SkillSourceType,
        source_url: str | None,
        name: str | None,
        skill_path: Path,
    ) -> SkillToolProvider:
        """Create SkillToolProvider from parsed skill content."""
        metadata = skill_content.metadata

        # Load script contents
        scripts_data = []
        for script in skill_content.scripts:
            script_file = skill_path / script.path
            if script_file.exists():
                script_dict = script.model_dump()
                script_dict["content"] = script_file.read_text(encoding="utf-8")
                scripts_data.append(script_dict)

        provider = SkillToolProvider(
            name=name or metadata.name,
            skill_identifier=metadata.name,
            tenant_id=tenant_id,
            user_id=user_id,
            source_type=source_type.value,
            source_url=source_url,
            source_hash=skill_content.source_hash,
            version=metadata.metadata.get("version", "1.0.0"),
            author=metadata.metadata.get("author"),
            skill_license=metadata.license,
            description=metadata.description,
            compatibility=json.dumps({"text": metadata.compatibility}) if metadata.compatibility else None,
            allowed_tools=json.dumps(metadata.allowed_tools) if metadata.allowed_tools else None,
            metadata_extra=json.dumps(metadata.metadata) if metadata.metadata else None,
            full_content=skill_content.body,
            has_scripts=len(scripts_data) > 0,
            scripts_manifest=json.dumps(scripts_data) if scripts_data else None,
        )

        self.session.add(provider)
        self.session.commit()
        self.session.refresh(provider)

        return provider

    def get_provider(self, provider_id: str, tenant_id: str) -> SkillToolProvider | None:
        """Get skill provider by ID."""
        return (
            self.session.query(SkillToolProvider)
            .filter(
                SkillToolProvider.id == provider_id,
                SkillToolProvider.tenant_id == tenant_id,
            )
            .first()
        )

    def list_providers(self, tenant_id: str) -> list[SkillToolProvider]:
        """List all skill providers for tenant."""
        return (
            self.session.query(SkillToolProvider)
            .filter(SkillToolProvider.tenant_id == tenant_id)
            .order_by(SkillToolProvider.created_at.desc())
            .all()
        )

    def list_providers_for_api(self, tenant_id: str, for_list: bool = False):
        """List all skill providers for tenant as API entities."""
        from models.account import Account
        from services.tools.tools_transform_service import ToolTransformService

        providers = self.list_providers(tenant_id)
        if not providers:
            return []

        # Batch query all users to avoid N+1 problem
        user_ids = {provider.user_id for provider in providers}
        users = self.session.query(Account).where(Account.id.in_(user_ids)).all()
        user_name_map = {user.id: user.name for user in users}

        return [
            ToolTransformService.skill_provider_to_user_provider(
                provider,
                for_list=for_list,
                user_name=user_name_map.get(provider.user_id),
            )
            for provider in providers
        ]

    def delete_provider(self, provider_id: str, tenant_id: str) -> bool:
        """Delete skill provider."""
        provider = self.get_provider(provider_id, tenant_id)
        if not provider:
            return False
        self.session.delete(provider)
        self.session.commit()
        return True

    def validate_skill_content(self, content: str) -> dict:
        """
        Validate SKILL.md content.

        Returns dict with validation result.
        """
        try:
            metadata, _ = SkillParser.parse(content)
            SkillValidator.validate(metadata)
            return {
                "valid": True,
                "name": metadata.name,
                "description": metadata.description,
            }
        except (SkillParseError, SkillValidationError) as e:
            return {
                "valid": False,
                "error": str(e),
            }
