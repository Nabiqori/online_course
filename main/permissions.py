# main/permissions.py
from rest_framework.permissions import BasePermission

class IsInstructor(BasePermission):


    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_instructor
