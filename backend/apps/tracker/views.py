from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Organization, Membership, Project, Issue, IssueAttachment
from .serializers import OrganizationSerializer, MembershipSerializer, ProjectSerializer, IssueSerializer, IssueAttachmentSerializer
from .permissions import IsOrgMember, RolePermission
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def perform_create(self, serializer):
        org = serializer.save()
        # create membership owner
        Membership.objects.create(user=self.request.user, organization=org, role=Membership.ROLE_OWNER)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOrgMember, RolePermission]
    allowed_roles = ["owner","manager"]

    def get_queryset(self):
        # restrict to organizations where user is a member
        qs = Project.objects.filter(organization__members__user=self.request.user).distinct()
        org_id = self.request.query_params.get("organization")
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return qs

class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "due_date", "assigned_to"]
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "priority", "created_at"]

    def get_queryset(self):
        return Issue.objects.filter(project__organization__members__user=self.request.user).distinct()

    def perform_create(self, serializer):
        issue = serializer.save(created_by=self.request.user)
        # Broadcast notification to project group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"project_{issue.project_id}",
            {"type": "issue.created", "issue_id": issue.id, "title": issue.title}
        )
        return issue

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, pk=None):
        issue = self.get_object()
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "file required"}, status=status.HTTP_400_BAD_REQUEST)
        att = IssueAttachment.objects.create(issue=issue, file=file_obj, uploaded_by=request.user)
        return Response(IssueAttachmentSerializer(att, context={"request": request}).data, status=status.HTTP_201_CREATED)

class MembershipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return Membership.objects.filter(user=self.request.user)
