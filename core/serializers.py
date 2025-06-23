from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Job, Application

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class SignupSerializer(serializers.ModelSerializer):
    user_type = serializers.ChoiceField(choices=Profile.USER_TYPE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.filter(user=user).update(user_type=user_type)
        return user


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['recruiter'] 


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    
    class Meta:
        model = Application
        fields = ['job', 'applied_at']
