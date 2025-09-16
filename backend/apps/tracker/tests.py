from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Organization, Membership, Project, Issue
from django.urls import reverse

class TeamIssueTrackerTests(TestCase):
    """
    Comprehensive test suite for the Team Issue Tracker API.
    """

    def setUp(self):
        """
        Set up the test environment, including API clients and users with different roles.
        """
        self.client = APIClient()
        self.user_owner = User.objects.create_user(username="owner_user", password="password123", email="owner@example.com")
        self.user_manager = User.objects.create_user(username="manager_user", password="password123", email="manager@example.com")
        self.user_member = User.objects.create_user(username="member_user", password="password123", email="member@example.com")
        self.user_unrelated = User.objects.create_user(username="unrelated_user", password="password123", email="unrelated@example.com")

        # Create an organization and assign roles
        self.org = Organization.objects.create(name="Test Org")
        Membership.objects.create(user=self.user_owner, organization=self.org, role=Membership.ROLE_OWNER)
        Membership.objects.create(user=self.user_manager, organization=self.org, role=Membership.ROLE_MANAGER)
        Membership.objects.create(user=self.user_member, organization=self.org, role=Membership.ROLE_MEMBER)
        
        # Create a project within the organization
        self.project = Project.objects.create(organization=self.org, name="Test Project", description="A project for testing")
        
        # Create an issue within the project
        self.issue = Issue.objects.create(
            project=self.project,
            title="Test Issue",
            description="This is a test issue",
            assigned_to=self.user_member,
            created_by=self.user_owner,
            status="open",
            priority="medium"
        )
        
    def _login_user(self, user):
        """Helper to log in a user with the APIClient."""
        self.client.force_authenticate(user=user)

    ##
    # Organization and Membership Tests
    ##
    def test_organization_creation_assigns_owner_role(self):
        """Test that creating an organization automatically makes the user an owner."""
        self._login_user(self.user_unrelated)
        response = self.client.post(reverse("organization-list"), {"name": "New Org"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_org_id = response.data["id"]
        
        # Verify ownership
        self.assertTrue(Membership.objects.filter(user=self.user_unrelated, organization_id=new_org_id, role=Membership.ROLE_OWNER).exists())
    
    def test_get_memberships_for_user(self):
        """Test that a user can only see their own memberships."""
        self._login_user(self.user_owner)
        response = self.client.get(reverse("membership-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["organization"], self.org.id)
        self.assertEqual(response.data[0]["role"], Membership.ROLE_OWNER)

    ##
    # Project Tests
    ##
    def test_owner_can_create_project(self):
        """Test that an owner can create a project within their organization."""
        self._login_user(self.user_owner)
        data = {"organization": self.org.id, "name": "New Project by Owner", "description": "desc"}
        response = self.client.post(reverse("project-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Project by Owner")
    
    def test_manager_can_create_project(self):
        """Test that a manager can create a project within their organization."""
        self._login_user(self.user_manager)
        data = {"organization": self.org.id, "name": "New Project by Manager", "description": "desc"}
        response = self.client.post(reverse("project-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Project by Manager")
        
    def test_member_cannot_create_project(self):
        """Test that a regular member cannot create a project."""
        self._login_user(self.user_member)
        data = {"organization": self.org.id, "name": "Project by Member", "description": "desc"}
        response = self.client.post(reverse("project-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_get_project_list_filters_by_membership(self):
        """Test that a user only sees projects for organizations they are a member of."""
        self._login_user(self.user_member)
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.project.id)
        
        # Test unrelated user sees no projects
        self._login_user(self.user_unrelated)
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    ##
    # Issue Tests
    ##
    def test_create_issue(self):
        """Test the creation of a new issue."""
        self._login_user(self.user_owner)
        data = {"project": self.project.id, "title": "New Issue by Owner", "description": "A new issue"}
        response = self.client.post(reverse("issue-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Issue by Owner")
        self.assertEqual(response.data["created_by"], self.user_owner.id)
    
    def test_list_issues_with_filters_and_search(self):
        """Test filtering and searching issues."""
        self._login_user(self.user_owner)
        
        # Create a few more issues for testing
        Issue.objects.create(project=self.project, title="Another Bug", status="in_progress")
        Issue.objects.create(project=self.project, title="Low Priority Task", priority="low")
        
        # Test filtering by status
        response = self.client.get(reverse("issue-list"), {"status": "in_progress"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Another Bug")
        
        # Test searching by title
        response = self.client.get(reverse("issue-list"), {"search": "Test Issue"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Issue")

    def test_unrelated_user_cannot_access_issues(self):
        """Test that a user from a different organization cannot access issues."""
        self._login_user(self.user_unrelated)
        response = self.client.get(reverse("issue-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # Should be an empty list due to `IsOrgMember` permission
        
        response = self.client.get(reverse("issue-detail", kwargs={"pk": self.issue.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # Object not found due to filtering in queryset
        
    def test_issue_update(self):
        """Test updating an issue."""
        self._login_user(self.user_member)
        data = {"title": "Updated Title", "status": "done"}
        response = self.client.patch(reverse("issue-detail", kwargs={"pk": self.issue.id}), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.title, "Updated Title")
        self.assertEqual(self.issue.status, "done")
        
    def test_issue_delete(self):
        """Test deleting an issue."""
        self._login_user(self.user_owner)
        response = self.client.delete(reverse("issue-detail", kwargs={"pk": self.issue.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Issue.objects.filter(id=self.issue.id).exists())

    def test_issue_attachment_upload(self):
        """Test uploading a file attachment to an issue."""
        self._login_user(self.user_member)
        
        # Use a dummy file for testing
        from django.core.files.uploadedfile import SimpleUploadedFile
        dummy_file = SimpleUploadedFile("test_file.txt", b"file content", content_type="text/plain")
        
        url = reverse("issue-upload", kwargs={"pk": self.issue.id})
        response = self.client.post(url, {"file": dummy_file}, format="multipart")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("file", response.data)
        self.assertIn("uploaded_by", response.data)
        self.assertEqual(response.data["uploaded_by"]["username"], self.user_member.username)
        
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.attachments.count(), 1)