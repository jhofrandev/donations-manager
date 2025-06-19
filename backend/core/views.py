from django.shortcuts import render
from rest_framework import generics, viewsets, permissions
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Campaign, Beneficiary, Task, Role
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from .serializers import RegisterSerializer, CampaignSerializer, BeneficiarySerializer, TaskSerializer

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED, headers=headers)

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role.role == 'admin'

class IsBeneficiary(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role.role == 'beneficiary'

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAdmin]

class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes = [IsAdmin]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        if self.request.user.is_authenticated and hasattr(self.request.user, 'role'):
            if self.request.user.role.role == 'admin':
                return [IsAdmin()]
            elif self.request.user.role.role == 'beneficiary':
                return [IsBeneficiary()]
        return [permissions.IsAuthenticated()]

    @transaction.atomic
    def perform_create(self, serializer):
        # Validar que la campaña esté activa
        campaign = serializer.validated_data.get('campaign')
        if not campaign.is_active:
            raise Exception('No se pueden crear tareas en campañas cerradas o canceladas.')
        task = serializer.save()
        # Enviar correo al beneficiario, si falla se revierte la transacción
        try:
            send_mail(
                subject='New Task Assigned',
                message=f'A new task has been assigned to you: {task.description}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[task.beneficiary.email],
                fail_silently=False,
            )
        except Exception as e:
            raise Exception('Error enviando correo al beneficiario. La tarea no fue creada.')

    @transaction.atomic
    def perform_update(self, serializer):
        prev_instance = self.get_object()
        prev_status = prev_instance.status
        task = serializer.save()
        # Impedir que una tarea finalizada vuelva a pendiente
        if prev_status == 'finalizada' and task.status != 'finalizada':
            raise Exception('No se puede cambiar el estado de una tarea finalizada a otro estado.')
        # Si el estado cambió, enviar correo
        if prev_status != task.status:
            # Si el cambio lo hace un beneficiario, notificar al admin
            if self.request.user.role.role == 'beneficiary':
                admin_emails = [u.user.email for u in Role.objects.filter(role='admin')]
                try:
                    send_mail(
                        subject='Task Status Updated',
                        message=f'El beneficiario {task.beneficiary.name} cambió el estado de la tarea "{task.description}" a {task.status}.',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=admin_emails,
                        fail_silently=False,
                    )
                except Exception as e:
                    raise Exception('Error enviando correo al admin. La actualización no fue guardada.')
            else:
                # Si el cambio lo hace un admin, notificar al beneficiario
                try:
                    send_mail(
                        subject='Task Status Updated',
                        message=f'The status of your task "{task.description}" has changed to {task.status}.',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[task.beneficiary.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    raise Exception('Error enviando correo al beneficiario. La actualización no fue guardada.')
