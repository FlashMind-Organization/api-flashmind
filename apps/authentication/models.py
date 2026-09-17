import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """Manager customizado para o modelo de usuário baseado em e-mail."""

    def create_user(self, email, name, password=None, role='user', **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        if not name or not name.strip():
            raise ValueError('O nome é obrigatório.')

        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, name=name.strip(), role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(
            email=email,
            name=name,
            password=password,
            role='admin',
            **extra_fields,
        )

class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuário customizado utilizando UUID e autenticação por e-mail."""

    ROLE_CHOICES = (
        ('user', 'Estudante'),
        ('admin', 'Administrador'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} <{self.email}> ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
