from rest_framework.permissions import BasePermission

from main.models import Course


class IsInstructor(BasePermission):


    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_instructor
class IsCourseParticipant(BasePermission):

    def has_permission(self, request, view):
        course_id = view.kwargs.get('course_id')
        if not course_id:
            return False

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return False

        return (
            request.user == course.instructor or
            course.enrolled_students.filter(id=request.user.id).exists()
        )


class IsLessonParticipant(BasePermission):


    def has_object_permission(self, request, view, obj):
        user = request.user
        course = obj.course
        return user == course.instructor or course.enrolled_students.filter(id=user.id).exists()
