from rest_framework import serializers
from api.models import MyUser, Rol
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    rol = serializers.SlugRelatedField(
        slug_field="user_type", queryset=Rol.objects.all()
    )

    class Meta:
        model = MyUser
        fields = ("name", "last_name", "email", "phone_number", "password", "rol")

    def validate_email(self, value):
        if MyUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Correo ya registrado")
        return value

    def create(self, validated_data):
        rol_data = validated_data.pop("rol")
        rol_instance = Rol.objects.get(user_type=rol_data)
        user = MyUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", ""),
            rol=rol_instance,
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        credentials = {"email": attrs.get("email"), "password": attrs.get("password")}

        try:
            user = MyUser.objects.get(email=credentials["email"])
        except MyUser.DoesNotExist:
            raise serializers.ValidationError("El correo proporcionado es incorrecto")

        if not user.check_password(credentials["password"]):
            raise serializers.ValidationError(
                "La contraseña proporcionada es incorrecta"
            )

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            'role': user.rol.user_type
        }
        
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.rol.user_type
        token['email'] = user.email

        return token
