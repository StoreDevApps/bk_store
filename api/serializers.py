from tokenize import Comment
from rest_framework import serializers
from api.models import MyUser, Product, Rol
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Comentario, Product

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
        print(user.rol.user_type)
        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["role"] = user.rol.user_type
        token["email"] = user.email

        return token
    
    from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'presentation', 'category', 'detail', 'brand', 'codigo', 'duedate', 'state', 'aud_created_at', 'images', 'videos', 'price', 'average_rating', 'rating_count']

    def get_price(self, obj):
        last_history = obj.producthistory_set.order_by('-date').first()
        return last_history.unit_sales_price if last_history else None

    def get_average_rating(self, obj):
        average_rating, _ = obj.calcular_puntuacion_promedio()
        return average_rating

    def get_rating_count(self, obj):
        _, rating_count = obj.calcular_puntuacion_promedio()
        return rating_count


class ComentarioSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='usuario.name', read_only=True)
    user_email = serializers.EmailField(source='usuario.email', read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'user_name', 'user_email', 'comentario', 'puntuacion', 'fecha_creacion', 'fecha_actualizacion']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['name', 'last_name', 'email']
