from django.contrib import admin
from django.urls import path
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from main.views import *

schema_view = get_schema_view(
   openapi.Info(
      title="Online course API",
      default_version='v1',
      description="",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('accounts/token/', TokenObtainPairView.as_view()),
    path('accounts/token/refresh/', TokenRefreshView.as_view()),
    path('api/register/', RegisterView.as_view()),
    path('api/users/', UserListView.as_view()),
    path('api/users/<int:pk>/', UserDetailView.as_view()),
    path('api/users/my-account/', MyAccountView.as_view()),
    path('api/courses/', CourseViewSet.as_view({'get': 'list', 'post': 'create'}), name='course-list'),
    path('api/courses/<int:id>/', CourseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='course-detail'),
    path('api/courses/<int:course_id>/lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('api/courses/<int:course_id>/lessons/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('api/courses/<int:course_id>/pay/', PayCourseView.as_view(), name='pay-course'),
    path('api/payments/', MyPaymentsView.as_view(), name='my-payments'),
    path('api/courses/<int:course_id>/enroll/', EnrollView.as_view(), name='enroll-course'),
    path('api/courses/<int:course_id>/students/', CourseStudentsView.as_view(), name='course-students'),
    path('api/courses/<int:course_id>/reviews/', CourseReviewView.as_view(), name='course-reviews'),
]
