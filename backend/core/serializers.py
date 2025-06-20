from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Campaign, Beneficiary, Task

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo electrónico.')
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        if not username:
            username = email.split('@')[0]
            # Si ya existe ese username, agregar sufijo numérico
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password']
        )
        return user

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Añadir claims personalizados
        token['email'] = user.email
        token['role'] = user.role.role if hasattr(user, 'role') else 'beneficiary'
        token['username'] = user.username
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError('No existe un usuario con este correo electrónico.')
            if not user_obj.is_active:
                raise serializers.ValidationError('Tu cuenta aún no está activada. Por favor, contacta al administrador.')
            if not user_obj.has_usable_password():
                raise serializers.ValidationError('Tu cuenta no tiene contraseña válida. Contacta al administrador.')
            if not user_obj.check_password(password):
                raise serializers.ValidationError('Correo o contraseña incorrectos.')
            role = user_obj.role.role if hasattr(user_obj, 'role') else 'beneficiary'
            data = self.get_token(user_obj)
            return {
                'refresh': str(data),
                'access': str(data.access_token),
                'user_id': user_obj.id,
                'email': user_obj.email,
                'username': user_obj.username,
                'role': role,
            }
        else:
            raise serializers.ValidationError('Debe incluir "email" y "password".')
