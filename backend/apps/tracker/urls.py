from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, ProjectViewSet, IssueViewSet, MembershipViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename="organization")
router.register(r'projects', ProjectViewSet, basename="project")
router.register(r'issues', IssueViewSet, basename="issue")
router.register(r'memberships', MembershipViewSet, basename="membership")

urlpatterns = router.urls
