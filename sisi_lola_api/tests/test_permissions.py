import pytest
from app.auth import has_permission, ROLES

def test_super_admin_has_all_permissions():
    assert has_permission(["SUPER_ADMIN"], "any:permission")
    assert has_permission(["SUPER_ADMIN"], "content:write")
    assert has_permission(["SUPER_ADMIN"], "ml:execute")

def test_content_director_permissions():
    roles = ["CONTENT_DIRECTOR"]
    assert has_permission(roles, "content:read")
    assert has_permission(roles, "content:approve")
    assert not has_permission(roles, "ml:execute")

def test_technical_operator_permissions():
    roles = ["TECHNICAL_OPERATOR"]
    assert has_permission(roles, "ml:execute")
    assert has_permission(roles, "assets:write")
    assert not has_permission(roles, "content:approve")

def test_multiple_roles():
    roles = ["CONTENT_DIRECTOR", "CREATIVE_PRODUCER"]
    assert has_permission(roles, "content:approve")
    assert has_permission(roles, "assets:write")

def test_viewer_limited_permissions():
    roles = ["VIEWER"]
    assert has_permission(roles, "content:read")
    assert not has_permission(roles, "content:write")
    assert not has_permission(roles, "ml:execute")

def test_role_definitions():
    assert "SUPER_ADMIN" in ROLES
    assert "CONTENT_DIRECTOR" in ROLES
    assert "TECHNICAL_OPERATOR" in ROLES
    assert len(ROLES) == 7
