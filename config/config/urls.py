from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.notes.views import NoteViewSet, TagViewSet
from apps.workspaces.views import WorkspaceViewSet
from apps.companies.views import CompanyViewSet
from apps.users.views import UserViewSet, register

# Create router
router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', register, name='register'),

    # API routes
    path('api/', include(router.urls)),
]