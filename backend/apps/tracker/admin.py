from django.contrib import admin
from .models import Organization, Membership, Project, Issue, IssueAttachment

admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(IssueAttachment)
