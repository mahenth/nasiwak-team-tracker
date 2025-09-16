from django.test import TestCase
from django.contrib.auth.models import User
from .models import Organization, Membership, Project, Issue
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

class BasicFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alice", password="pass123", email="alice@example.com")
        self.client.login(username="alice", password="pass123")  # used for session; API uses JWT in practice

    def test_org_project_issue_crud(self):
        # create an org via API (org creator becomes owner)
        resp = self.client.post("/api/v1/organizations/", {"name":"Acme"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        org_id = resp.data["id"]

        # user is owner; create project under org
        resp = self.client.post("/api/v1/projects/", {"organization": org_id, "name": "Website", "description":"desc"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        project_id = resp.data["id"]

        # create issue for project
        resp = self.client.post("/api/v1/issues/", {"project": project_id, "title":"Bug #1", "description":"broken"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        issue_id = resp.data["id"]

        # get issues list
        resp = self.client.get("/api/v1/issues/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(i["id"] == issue_id for i in resp.data))
