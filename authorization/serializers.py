from rest_framework import serializers
from django. contrib.auth import get_user_model
from rest_framework_simplejwt. tokens import RefreshToken

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'], required=False)
    birth_date = serializers.DateField(required=False)
    height = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "gender", "birth_date", "height", "weight")

    def create(self, validated_data):
        gender = validated_data.pop("gender", None)
        birth_date = validated_data.pop("birth_date", None)
        height = validated_data.pop("height", None)
        weight = validated_data.pop("weight", None)

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        # Member profili güncelle
        member = user.member_profile
        if gender:
            member.gender = gender
        if birth_date:
            member.birth_date = birth_date
        if height is not None:
            member.height = height
        if weight is not None:
            member.weight = weight
        member.save()

        return user


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