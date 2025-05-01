from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import *
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import *
from .serializers import *
from rest_framework import generics, permissions
from .serializers import UserSerializer

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class MyAccountView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = []
    search_fields = ['instructor__username','title']
    ordering_fields = ['price', 'rating']
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsInstructor()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseDetailSerializer
        return CourseBaseSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_instructor:
            raise PermissionDenied("Faqat instruktorlar kurs yaratishi mumkin.")
        serializer.save(instructor=self.request.user)

    def perform_update(self, serializer):
        if self.request.user != self.get_object().instructor:
            raise PermissionDenied("Faqat kurs egasi yangilashi mumkin.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.instructor:
            raise PermissionDenied("Faqat kurs egasi o‘chira oladi.")
        instance.delete()

    def get_queryset(self):
        queryset = Course.objects.all()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

class LessonListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsLessonParticipant]

    @swagger_auto_schema(request_body=LessonSerializer)
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if request.user != course.instructor:
            raise PermissionDenied("Faqat instruktorga ruxsat.")
        serializer = LessonSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request, course_id):
        lessons = Lesson.objects.filter(course__id=course_id)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

class LessonDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsLessonParticipant]

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class PayCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = Course.objects.get(id=course_id)

        Payment.objects.create(
                user=request.user,
                course=course,
                status='pending'
            )


        Payment.objects.create(
            user=request.user,
            course=course,
            status='completed'
        )

        if not hasattr(request.user, 'student_profile'):
            Student.objects.create(user=request.user)

        request.user.student_profile.courses.add(course)

        return Response({'detail': 'To‘lov muvaffaqiyatli amalga oshirildi.'}, status=201)


class MyPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

class EnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        payment = Payment.objects.filter(user=request.user, course_id=course_id, status='completed').first()

        if not payment:
            raise PermissionDenied("Siz kurs uchun to‘lovni amalga oshirmadingiz.")

        course = Course.objects.get(id=course_id)
        student_profile = request.user.student_profile
        student_profile.courses.add(course)

        return Response({'detail': 'Kursga muvaffaqiyatli yozildingiz!'}, status=200)

class CourseStudentsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        if request.user != course.instructor:
            raise PermissionDenied("Faqat instruktorga ruxsat.")
        students = User.objects.filter(student_profile__courses=course)
        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)

class CourseReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        reviews = Review.objects.filter(course_id=course_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ReviewSerializer)
    def post(self, request, course_id):
        course = Course.objects.get(id=course_id)

        if not Student.objects.filter(user=self.request.user, courses__id=course_id).exists():
            raise PermissionDenied("Siz bu kursga yozilmaganligingiz sababli sharh qoldira olmaysiz.")

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user, course=course)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class BecomeStudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'student'):
            return Response({"detail": "Siz allaqachon student sifatida ro'yxatdan o'tgansiz."},
                            status=status.HTTP_400_BAD_REQUEST)

        profile = Student.objects.create(user=request.user)
        serializer = StudentSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)