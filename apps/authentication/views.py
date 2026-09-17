from rest_framework import status, permissions, generics, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdminRole

class RegisterView(generics.CreateAPIView):
    """Cria uma nova conta de usuário estudante."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )

class LoginView(views.APIView):
    """Autentica o usuário e retorna os tokens JWT de forma resiliente contra enumeração."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        access = serializer.validated_data['access']
        refresh = serializer.validated_data['refresh']

        return Response(
            {
                'access': access,
                'refresh': refresh,
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

class ProfileView(generics.RetrieveUpdateAPIView):
    """Permite ao usuário autenticado visualizar e editar o próprio perfil (nome e e-mail)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(views.APIView):
    """Permite a alteração da senha mediante validação da senha atual e emite novos tokens."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)

class LogoutView(views.APIView):
    """Invalida o refresh token enviado via blacklist."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Ignora se o token já estiver expirado ou inválido

        return Response(
            {'detail': 'Sessão encerrada com sucesso.'},
            status=status.HTTP_200_OK,
        )

class AdminStatusView(views.APIView):
    """Endpoint protegido para verificar privilégios do administrador na API."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(
            {
                'detail': 'Acesso administrativo confirmado.',
                'user': UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )
