from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.companies.models import Company

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'company', 'company_name',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'company_id'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        company_id = validated_data.pop('company_id', None)

        user = User.objects.create_user(**validated_data)

        if company_id:
            try:
                company = Company.objects.get(id=company_id, is_active=True)
                user.company = company
                user.save()
            except Company.DoesNotExist:
                pass

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'company', 'company_name', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'role', 'company', 'date_joined']