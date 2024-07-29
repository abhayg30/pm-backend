from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, UserDetails


# Login serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={"input_type": "password "}, write_only=True
    )

    class Meta:
        model = User
        fields = ["email", "user_type", "password", "password2", "status"]

        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, clean_data):
        password = clean_data.get("password")
        password2 = clean_data.get("password2")
        if password != password2:
            raise serializers.ValidationError("Passwords do not match")
        return clean_data

    def create(self, clean_data):
        return User.objects.create_user(**clean_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = [
            "first_name",
            "last_name",
            "zip_code",
            "city",
            "working_rights",
            "gender",
            "date_of_birth",
        ]


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, clean_data):
        password = clean_data.get("password")
        password2 = clean_data.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError("Passwords do not match")
        user.set_password(password)
        user.save()
        return clean_data


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded UID", uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("Password Reset Token", token)
            link = "http://localhost:3000/api/user/reset/" + uid + "/" + token
            print("Password Reset Link", link)
            # Send EMail
            body = "Click Following Link to Reset Your Password " + link
            data = {
                "subject": "Reset Your Password",
                "body": body,
                "to_email": user.email,
            }
            # Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("You are not a Registered User")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")
            if password != password2:
                raise serializers.ValidationError(
                    "Password and Confirm Password doesn't match"
                )
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not Valid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not Valid or Expired")


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_message = {"bad_token": ("Token is expired or invalid")}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail("bad_token")


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ["zip_code", "city", "working_rights"]
