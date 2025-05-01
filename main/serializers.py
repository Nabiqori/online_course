from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
class CourseBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ['instructor']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Kurs narxi 0 dan katta bo‘lishi kerak.")
        return value
class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'course': {'read_only': True}
        }


    def validate_course(self, value):
        if value.instructor != self.context['request'].user:
            raise serializers.ValidationError("Siz bu kursning instruktori emassiz.")
        return value

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("To‘lov summasi 0 dan katta bo‘lishi kerak.")
        return value
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment']
        read_only_fields = ['user', 'course']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Reyting 1 dan 5 gacha bo‘lishi kerak.")
        return value

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


