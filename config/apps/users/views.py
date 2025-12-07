from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer
)

User = get_user_model()

# Pagination class for Users
class MaxLimitPagination(PageNumberPagination):
    page_size = 10               # default page size
    page_size_query_param = 'limit'
    max_page_size = 50           # maximum allowed

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related('company').filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MaxLimitPagination  # ← add this

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return User.objects.filter(
                company=user.company,
                is_active=True
            ).select_related('company')
        return User.objects.none()

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)

        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Generate tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)
