from django.db import models
from django.contrib.auth.models import User

class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLE_OWNER = "owner"
    ROLE_MANAGER = "manager"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = [(ROLE_OWNER, "Owner"), (ROLE_MANAGER, "Manager"), (ROLE_MEMBER, "Member")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name} ({self.role})"

class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} / {self.name}"

class Issue(models.Model):
    STATUS_CHOICES = [("open","Open"),("in_progress","In Progress"),("done","Done"),("blocked","Blocked")]
    PRIORITY_CHOICES = [("low","Low"),("medium","Medium"),("high","High"),("critical","Critical")]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default="medium")
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_issues")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_issues")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.project}] {self.title}"

class IssueAttachment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/%Y/%m/%d/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
