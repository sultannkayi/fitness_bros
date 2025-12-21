from rest_framework import serializers
from django. contrib.auth import get_user_model
from rest_framework_simplejwt. tokens import RefreshToken

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name")

    def create(self, validated_data):
        user = User. objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )

        return user

    def to_representation(self, instance):
        token = RefreshToken.for_user(instance)
        return {
            "token": str(token. access_token),
            "user": {
                "email": instance.email,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "is_instructor": instance.is_instructor,
            }
        }


class LoginSerializer(serializers. Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            token = RefreshToken.for_user(user)
            return {"access": str(token.access_token)}

        raise serializers.ValidationError("Invalid credentials")