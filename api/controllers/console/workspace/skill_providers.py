"""
API endpoints for skill tool providers.
"""

from flask import request
from flask_restx import Resource, reqparse
from sqlalchemy.orm import Session
from werkzeug.exceptions import NotFound

from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from core.model_runtime.utils.encoders import jsonable_encoder
from extensions.ext_database import db
from libs.login import current_account_with_tenant, login_required
from services.tools.skill_tools_manage_service import SkillToolManageError, SkillToolManageService


@console_ns.route("/workspaces/current/tool-provider/skill/list")
class SkillProviderListApi(Resource):
    """List skill providers."""

    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        """GET /workspaces/current/tool-provider/skill/list - List all skills."""
        _, tenant_id = current_account_with_tenant()

        with Session(db.engine) as session:
            service = SkillToolManageService(session=session)
            providers = service.list_providers(tenant_id)

            return jsonable_encoder(
                [
                    {
                        "id": p.id,
                        "name": p.name,
                        "skill_identifier": p.skill_identifier,
                        "description": p.description,
                        "icon": p.icon,
                        "source_type": p.source_type,
                        "version": p.version,
                        "author": p.author,
                        "has_scripts": p.has_scripts,
                        "enabled": p.enabled,
                        "created_at": p.created_at.isoformat() if p.created_at else None,
                    }
                    for p in providers
                ]
            )


parser_install = (
    reqparse.RequestParser()
    .add_argument("source_type", type=str, required=True, choices=["git", "upload", "path"], location="json")
    .add_argument("git_url", type=str, required=False, location="json")
    .add_argument("git_branch", type=str, required=False, default="main", location="json")
    .add_argument("path", type=str, required=False, location="json")
    .add_argument("name", type=str, required=False, location="json")
)


@console_ns.route("/workspaces/current/tool-provider/skill/install")
class SkillProviderInstallApi(Resource):
    """Install skill provider."""

    @console_ns.expect(parser_install)
    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        """POST /workspaces/current/tool-provider/skill/install - Install skill."""
        user, tenant_id = current_account_with_tenant()
        args = parser_install.parse_args()

        source_type = args["source_type"]

        with Session(db.engine) as session:
            service = SkillToolManageService(session=session)

            try:
                if source_type == "git":
                    if not args.get("git_url"):
                        return {"error": "git_url is required for git source"}, 400
                    provider = service.install_from_git(
                        tenant_id=tenant_id,
                        user_id=user.id,
                        git_url=args["git_url"],
                        branch=args.get("git_branch", "main"),
                        name=args.get("name"),
                    )
                elif source_type == "path":
                    if not args.get("path"):
                        return {"error": "path is required for path source"}, 400
                    provider = service.install_from_path(
                        tenant_id=tenant_id,
                        user_id=user.id,
                        path=args["path"],
                        name=args.get("name"),
                    )
                elif source_type == "upload":
                    return {"error": "Use /upload endpoint for file uploads"}, 400
                else:
                    return {"error": f"Unknown source_type: {source_type}"}, 400

                return jsonable_encoder(
                    {
                        "id": provider.id,
                        "name": provider.name,
                        "skill_identifier": provider.skill_identifier,
                        "description": provider.description,
                    }
                )
            except SkillToolManageError as e:
                return {"error": str(e)}, 400


@console_ns.route("/workspaces/current/tool-provider/skill/upload")
class SkillProviderUploadApi(Resource):
    """Upload skill provider."""

    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        """POST /workspaces/current/tool-provider/skill/upload - Upload skill zip."""
        user, tenant_id = current_account_with_tenant()

        if "file" not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files["file"]
        if not file.filename:
            return {"error": "No filename"}, 400

        name = request.form.get("name")

        with Session(db.engine) as session:
            service = SkillToolManageService(session=session)

            try:
                provider = service.install_from_upload(
                    tenant_id=tenant_id,
                    user_id=user.id,
                    file_content=file.read(),
                    filename=file.filename,
                    name=name,
                )

                return jsonable_encoder(
                    {
                        "id": provider.id,
                        "name": provider.name,
                        "skill_identifier": provider.skill_identifier,
                        "description": provider.description,
                    }
                )
            except SkillToolManageError as e:
                return {"error": str(e)}, 400


@console_ns.route("/workspaces/current/tool-provider/skill/<string:provider_id>")
class SkillProviderApi(Resource):
    """Single skill provider operations."""

    @setup_required
    @login_required
    @account_initialization_required
    def get(self, provider_id: str):
        """GET /workspaces/current/tool-provider/skill/<id> - Get skill details."""
        _, tenant_id = current_account_with_tenant()

        with Session(db.engine) as session:
            service = SkillToolManageService(session=session)
            provider = service.get_provider(provider_id, tenant_id)

            if not provider:
                raise NotFound("Skill provider not found")

            return jsonable_encoder(
                {
                    "id": provider.id,
                    "name": provider.name,
                    "skill_identifier": provider.skill_identifier,
                    "description": provider.description,
                    "icon": provider.icon,
                    "source_type": provider.source_type,
                    "source_url": provider.source_url,
                    "version": provider.version,
                    "author": provider.author,
                    "license": provider.skill_license,
                    "compatibility": provider.compatibility_dict,
                    "full_content": provider.full_content,
                    "has_scripts": provider.has_scripts,
                    "scripts": provider.scripts,
                    "enabled": provider.enabled,
                    "created_at": provider.created_at.isoformat() if provider.created_at else None,
                    "updated_at": provider.updated_at.isoformat() if provider.updated_at else None,
                }
            )

    @setup_required
    @login_required
    @account_initialization_required
    def delete(self, provider_id: str):
        """DELETE /workspaces/current/tool-provider/skill/<id> - Delete skill."""
        _, tenant_id = current_account_with_tenant()

        with Session(db.engine) as session:
            service = SkillToolManageService(session=session)
            deleted = service.delete_provider(provider_id, tenant_id)

            if not deleted:
                raise NotFound("Skill provider not found")

            return {"success": True}


parser_validate = reqparse.RequestParser().add_argument("content", type=str, required=True, location="json")


@console_ns.route("/workspaces/current/tool-provider/skill/validate")
class SkillProviderValidateApi(Resource):
    """Validate skill content."""

    @console_ns.expect(parser_validate)
    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        """POST /workspaces/current/tool-provider/skill/validate - Validate SKILL.md."""
        args = parser_validate.parse_args()

        with Session(db.engine) as session:
            service = SkillToolManageService(session=session)
            result = service.validate_skill_content(args["content"])

            return jsonable_encoder(result)
