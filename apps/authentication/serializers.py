from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer para exibição segura dos dados do usuário."""

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'role', 'created_at', 'updated_at']

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para criação de nova conta de estudante (AC 1, AC 2, AC 3)."""

    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Este e-mail já está cadastrado.',
                lookup='iexact',
            )
        ],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']
        read_only_fields = ['id', 'role']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError('O nome é obrigatório.')
        return name

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError('O e-mail é obrigatório.')
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Este e-mail já está cadastrado.')
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role='user',
        )
        return user

class LoginSerializer(serializers.Serializer):
    """Serializer para autenticação defensiva contra enumeração de usuários (AC 4)."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password', '')

        user = User.objects.filter(email__iexact=email).first()

        if not user or not user.check_password(password) or not user.is_active:
            raise exceptions.AuthenticationFailed('Credenciais inválidas.')

        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer para consulta e atualização de nome e e-mail pelo próprio usuário (AC 7)."""

    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']
        extra_kwargs = {
            'email': {'validators': []},
        }

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError('O nome não pode ser vazio.')
        return name

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError('O e-mail não pode ser vazio.')

        instance = getattr(self, 'instance', None)
        query = User.objects.filter(email__iexact=email)
        if instance:
            query = query.exclude(id=instance.id)

        if query.exists():
            raise serializers.ValidationError('Este e-mail já está em uso.')
        return email

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para alteração de senha exigindo validação da senha atual (AC 8)."""

    current_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('A senha atual está incorreta.')
        return value

    def validate_new_password(self, value):
        user = self.context['request'].user
        validate_password(value, user=user)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save(update_fields=['password', 'updated_at'])

        # Emite novos tokens para que a sessão móvel continue ativa sem necessidade de relogar
        refresh = RefreshToken.for_user(user)
        return {
            'detail': 'Senha alterada com sucesso.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
