from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Organization, Membership, Project, Issue, IssueAttachment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","email","first_name","last_name")

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id","name","created_at")

class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Membership
        fields = ("id","user","role","organization","created_at")
        read_only_fields = ("user","created_at")

class ProjectSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    class Meta:
        model = Project
        fields = ("id","organization","name","description","created_at")
        read_only_fields = ("created_at",)

class IssueAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    class Meta:
        model = IssueAttachment
        fields = ("id","file","uploaded_by","uploaded_at")

class IssueSerializer(serializers.ModelSerializer):
    attachments = IssueAttachmentSerializer(many=True, read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(source='assigned_to', queryset=User.objects.all(), write_only=True, required=False, allow_null=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Issue
        fields = ("id","project","title","description","status","priority","due_date","assigned_to","assigned_to_id","attachments","created_by","created_at","updated_at")
        read_only_fields = ("created_by","created_at","updated_at")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and validated_data.get("project"):
            validated_data["created_by"] = request.user
        return super().create(validated_data)
