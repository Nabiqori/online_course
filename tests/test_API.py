from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from main.models import Course

User = get_user_model()

class CourseAPITest(APITestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor1',
            password='testpassword',
            is_instructor=True
        )

        refresh = RefreshToken.for_user(self.instructor)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_create_course(self):
        data = {
            "title": "Django",
            "description": "Django",
            "price": 150000,
            "instructor": self.instructor.id
        }

        response = self.client.post("/api/courses/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.first().instructor, self.instructor)

    def test_create_course_without_auth(self):
        self.client.credentials()
        data = {
            "title": "Unauthorized Course",
            "description": "Bu foydalanuvchi ruxsatsiz",
            "price": 100000
        }
        response = self.client.post("/api/courses/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
