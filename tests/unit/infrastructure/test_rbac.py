from agentsphere.infrastructure.auth.rbac import ROLE_PERMISSIONS, has_permission


class TestRBAC:
    def test_superadmin_has_all_permissions(self):
        assert has_permission("superadmin", "anything:anything") is True

    def test_admin_has_defined_permissions(self):
        assert has_permission("admin", "tenants:read") is True
        assert has_permission("admin", "users:write") is True

    def test_admin_lacks_unknown_permission(self):
        assert has_permission("admin", "billing:write") is False

    def test_viewer_has_read_only(self):
        assert has_permission("viewer", "conversations:read") is True
        assert has_permission("viewer", "conversations:write") is False

    def test_unknown_role_has_no_permissions(self):
        assert has_permission("unknown_role", "conversations:read") is False

    def test_all_roles_defined(self):
        expected_roles = {"superadmin", "admin", "editor", "viewer"}
        assert set(ROLE_PERMISSIONS.keys()) == expected_roles
