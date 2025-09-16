from rest_framework import permissions
from .models import Membership, Project

class IsOrgMember(permissions.BasePermission):
    """
    Verify that user is member of the organization related to the object or request.
    """

    def has_permission(self, request, view):
        # For list/create views, allow and filter later in viewset by organization
        return True

    def has_object_permission(self, request, view, obj):
        # If object is Project
        if isinstance(obj, Project):
            return Membership.objects.filter(user=request.user, organization=obj.organization).exists()
        # If object has project attribute (Issue, etc.)
        org = getattr(obj, "project").organization if hasattr(obj, "project") else None
        if org:
            return Membership.objects.filter(user=request.user, organization=org).exists()
        return False

class RolePermission(permissions.BasePermission):
    """
    Check that user's role in organization is one of allowed roles.
    Usage: set view.allowed_roles = ["owner","manager"]
    """

    def has_permission(self, request, view):
        allowed = getattr(view, "allowed_roles", None)
        if not allowed:
            return True
        # prefer organization id from data or query params
        org_id = request.data.get("organization") or request.query_params.get("organization")
        if not org_id:
            return True
        return Membership.objects.filter(user=request.user, organization_id=org_id, role__in=allowed).exists()
