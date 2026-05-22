import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .models import Usuario
from .serializers import UsuarioSerializer
from clinix.models import Doctor, Paciente;



@extend_schema(tags=['Autenticación - Registro'])
class RegisterDoctorView(APIView): 

    @extend_schema(
        summary="Registrar un nuevo doctor",
        description="Registra un nuevo doctor en la base de datos y devuelve sus tokens de acceso y refresco.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email", "example": "doctor@ejemplo.com"},
                    "password": {"type": "string", "example": "contraseña_segura123"},
                    "especialidad": {"type": "string", "example": "Cardiología"},
                    "colegiado": {"type": "string", "example": "COL-123456"}
                },
                "required": ["email", "password", "especialidad", "colegiado"]
            }
        },
        responses={
            201: OpenApiResponse(description="Doctor creado exitosamente"),
            400: OpenApiResponse(description="Errores de validación"),
            500: OpenApiResponse(description="Error interno del servidor")
        }
    )
    def post(self, request): 

        data = request.data; 

        try: 
            with transaction.atomic(): 

                user = Usuario.objects.create_user(
                    email = data['email'], 
                    password = data['password'],
                    is_doctor = True,
                    is_paciente = False,
                ); 

                doctor = Doctor.objects.create(
                    user = user, 
                    especialidad = data['especialidad'],
                    colegiado = data['colegiado'],
                )

                refresh = RefreshToken.for_user(user);

                return Response({
                    'message': 'Doctor creado exitosamente',
                    'user_id': user.id,
                    'doctor_id': {
                        'id': doctor.id,
                        'especialidad': doctor.especialidad,
                        'colegiado': doctor.colegiado,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED);

        except Exception as e: 
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);

@extend_schema(tags=['Autenticación - Registro'])
class RegisterPacienteView(APIView): 

    @extend_schema(
        summary="Registrar un nuevo paciente",
        description="Registra un nuevo paciente en la base de datos y devuelve sus tokens de acceso y refresco.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email", "example": "paciente@ejemplo.com"},
                    "password": {"type": "string", "example": "contraseña_segura123"},
                    "fecha_nac": {"type": "string", "format": "date", "example": "1990-05-15"},
                    "descripcion": {"type": "string", "example": "Paciente con hipertensión leve"},
                    "telefono": {"type": "string", "example": "+502 12345678"}
                },
                "required": ["email", "password", "fecha_nac", "descripcion", "telefono"]
            }
        },
        responses={
            201: OpenApiResponse(description="Paciente creado exitosamente"),
            400: OpenApiResponse(description="Errores de validación"),
            500: OpenApiResponse(description="Error interno del servidor")
        }
    )

    def post(self, request): 

        data = request.data; 
        
        try: 

            with transaction.atomic():

                user = Usuario.objects.create_user(
                    email = data['email'], 
                    password = data['password'],
                    is_doctor = False,
                    is_paciente = True,
                ); 

                paciente = Paciente.objects.create(
                    user = user, 
                    fecha_nac = data['fecha_nac'],
                    descripcion = data['descripcion'],
                    telefono = data['telefono'],
                )

                refresh = RefreshToken.for_user(user);

                return Response({
                    'message': 'Paciente creado exitosamente',
                    'user_id': user.id,
                    'paciente_id': paciente.id,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED);

        except Exception as e: 
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);


@extend_schema(tags=['Autenticación - Registro'])
class RegisterView(APIView):

    #permite que cualquera acceda a este endpoint sin estar logeado (por el momento)

    permission_classes = [AllowAny]; 

    @extend_schema(
        summary="Registrar un nuevo usuario",
        description="Registra un nuevo usuario en la base de datos y devuelve sus tokens de acceso y refresco.",
        request=UsuarioSerializer,
        responses={
            201: OpenApiResponse(description="Usuario creado exitosamente"),
            400: OpenApiResponse(description="Errores de validación"),
        }
    )

    def post(self, request) : 
        serializer = UsuarioSerializer(data=request.data); 

        if(serializer.is_valid()):
            user = serializer.save(); 

            refresh = RefreshToken.for_user(user); 

            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Autenticación - Sesión'])
class LoginView(APIView): 
    
    permission_classes = [AllowAny]; 

    @extend_schema(
        summary="Iniciar sesión",
        description="Inicia sesión usando email y contraseña, o mediante google_id.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"},
                    "google_id": {"type": "string"},
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="Inicio de sesión exitoso",
                response={
                    "type": "object",
                    "properties": {
                        "user": {"type": "object"},
                        "refresh": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJ..."},
                        "access": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJ..."}
                    }
                }
            ),
            400: OpenApiResponse(description="Petición incorrecta o datos faltantes"),
            401: OpenApiResponse(description="Credenciales inválidas"),
            404: OpenApiResponse(description="Usuario no encontrado"),
        }
    )
    def post(self, request): 
        email = request.data.get('email'); 
        password = request.data.get('password'); 
        google_id = request.data.get('google_id'); 

        user = None; 

        if google_id: 
            try: 
                user = Usuario.objects.get(google_id=google_id);
            except Usuario.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                }, status=status.HTTP_404_NOT_FOUND)
        elif email and password: 
            user = authenticate(request, email=email, password=password); 
            if not user: 
                return Response({
                    'error': 'Credenciales inválidas',
                }, status=status.HTTP_401_UNAUTHORIZED);
        
        else: 
            return Response({
                'error': 'Debes proveer email/password o google_id',
            }, status=status.HTTP_400_BAD_REQUEST);
        
        if user: 
            refresh = RefreshToken.for_user(user)
            serializer = UsuarioSerializer(user)
            
            doctor = Doctor.objects.filter(user=user).first()
            if doctor: 
                return Response({
                    'user': serializer.data,
                    'doctor_id': {
                        'id': doctor.id,
                        'especialidad': doctor.especialidad,
                        'colegiado': doctor.colegiado,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            
            paciente = Paciente.objects.filter(user=user).first()
            if paciente: 
                return Response({
                    'user': serializer.data,
                    'paciente_id': {
                        'id': paciente.id,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

@extend_schema(tags=['Autenticación - Sesión'])
class MockLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Mock login - devuelve tokens para el primer usuario",
        description="Endpoint de prueba que devuelve tokens JWT para el primer usuario en la BD sin requerir credenciales. Acepta los mismos argumentos que Google pero son ignorados.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id_token": {"type": "string", "description": "Ignorado en mock"}
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Tokens del primer usuario"),
            404: OpenApiResponse(description="No hay usuarios en la base de datos"),
        }
    )
    def post(self, request):
        try:
            user = Usuario.objects.first()
            if not user:
                return Response({
                    'error': 'No hay usuarios en la base de datos',
                }, status=status.HTTP_404_NOT_FOUND)

            refresh = RefreshToken.for_user(user)
            serializer = UsuarioSerializer(user)

            try:
                doctor = Doctor.objects.get(user=user)
            except Doctor.DoesNotExist:
                doctor = None

            try:
                paciente = Paciente.objects.get(user=user)
            except Paciente.DoesNotExist:
                paciente = None

            if doctor:
                return Response({
                    'user': serializer.data,
                    'doctor_id': {
                        'id': doctor.id,
                        'especialidad': doctor.especialidad,
                        'colegiado': doctor.colegiado,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)

            if paciente:
                return Response({
                    'user': serializer.data,
                    'paciente_id': {
                        'id': paciente.id,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)

            return Response({
                'message': 'Mock login exitoso',
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f'[MockLogin] Error: {e}')
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Autenticación - Sesión'])
class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Refrescar token de acceso",
        description="Recibe un token de refresco y devuelve un nuevo token de acceso.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "Token de refresco", "example": "eyJ0eXAiOiJKV1QiLCJ..."}
                },
                "required": ["refresh"]
            }
        },
        responses={
            200: OpenApiResponse(description="Nuevo token de acceso generado"),
            400: OpenApiResponse(description="Token no proporcionado"),
            401: OpenApiResponse(description="Token de refresco inválido o expirado"),
        }
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({
                'error': 'El token de refresco es requerido',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            user = token.user
            access = str(token.access_token)
            token.blacklist()
            serializer = UsuarioSerializer(user)
            return Response({
                'message': 'Token refrescado exitosamente',
                'user': serializer.data,
                'refresh': str(token),
                'access': access,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f'[TokenRefresh] Error: {e}')
            return Response({
                'error': f'Token de refresco inválido o expirado: {str(e)}',
            }, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(tags=['Autenticación - Sesión'])
class LogoutView(APIView): 
    permission_classes = [IsAuthenticated]; 

    @extend_schema(
        summary="Cerrar sesión",
        description="Cierra la sesión del usuario invalidando el token de refresco (blacklist). Requiere autenticación con JWT.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "Token de refresco a invalidar"}
                },
                "required": ["refresh"]
            }
        },
        responses={
            200: OpenApiResponse(description="Logout exitoso"),
            400: OpenApiResponse(description="Token de refresco no proveído"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def post(self, request): 
        try: 
            refresh_token = request.data.get('refresh');
            if not refresh_token: 
                return Response({
                    'error': 'Token no proveido',
                }, status=status.HTTP_400_BAD_REQUEST);
            
            token = RefreshToken(refresh_token)
            token.blacklist();
            return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
        except Exception as e: 
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);


@extend_schema(tags=['Autenticación - Google'])
class GoogleAuthView(APIView):

    permission_classes = [AllowAny];

    @extend_schema(
        summary="Autenticación con Google",
        description=(
            "Recibe el `id_token` que el frontend/app obtiene tras el flujo de Google Sign-In. "
            "El backend verifica el token con Google, y si es válido:\n"
            "- Si el usuario ya existe → inicia sesión\n"
            "- Si el usuario no existe → lo crea automáticamente\n\n"
            "Retorna tokens JWT (access + refresh) para usar en los demás endpoints."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id_token": {
                        "type": "string",
                        "description": "Token de ID obtenido del flujo de Google Sign-In",
                        "example": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
                    },
                    "is_doctor": {
                        "type": "boolean",
                        "description": "Indica si el usuario es doctor",
                        "example": False
                    }
                },
                "required": ["id_token", "is_doctor"]
            }
        },
        responses={
            200: OpenApiResponse(
                description="Inicio de sesión exitoso (usuario existente)",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Inicio de sesión con Google exitoso"},
                        "is_new_user": {"type": "boolean", "example": False},
                        "user": {"type": "object"},
                        "refresh": {"type": "string"},
                        "access": {"type": "string"}
                    }
                }
            ),
            201: OpenApiResponse(description="Usuario creado exitosamente con Google"),
            400: OpenApiResponse(description="Token no proporcionado"),
            401: OpenApiResponse(description="Token de Google inválido o expirado"),
            500: OpenApiResponse(description="Error interno del servidor"),
        }
    )
    def post(self, request):
        token = request.data.get('id_token');
        is_doctor = request.data.get('is_doctor', False)
        is_paciente = not is_doctor
        
        if not token:
            return Response({
                'error': 'El id_token de Google es requerido',
            }, status=status.HTTP_400_BAD_REQUEST);

        try:
            # Verificar el token con Google
            google_client_id_web = os.environ.get('GOOGLE_CLIENT_ID')
            google_client_id_android = os.environ.get('GOOGLE_CLIENT_ID_ANDROID')
            
            # Lista de IDs permitidos (puedes añadir más como iOS si fuera necesario)
            valid_audiences = [id for id in [google_client_id_web, google_client_id_android] if id]
            
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                valid_audiences
            )

            # Extraer información del usuario de Google
            google_id = idinfo['sub']  # ID único de Google
            email = idinfo.get('email')
            
            if not email:
                return Response({
                    'error': 'El token de Google no contiene un email',
                }, status=status.HTTP_400_BAD_REQUEST);

            # Buscar si el usuario ya existe (por google_id o por email)
            user = None
            doctor = None
            paciente = None
            is_new_user = False

            try:
                # Primero buscar por google_id
                user = Usuario.objects.get(google_id=google_id)
                
            except Usuario.DoesNotExist:
                try:
                    # Si no tiene google_id, buscar por email y vincular
                    user = Usuario.objects.get(email=email)
                    user.google_id = google_id
                    user.save()
                except Usuario.DoesNotExist:
                    # El usuario no existe, crearlo
                    with transaction.atomic():
                        user = Usuario.objects.create_user(
                            email=email,
                            password=None,  # Sin contraseña, se autentica con Google
                            google_id=google_id,
                            is_doctor=is_doctor,
                            is_paciente=is_paciente,
                        )

                        if is_doctor:
                            doctor = Doctor.objects.create(
                                user=user,
                                especialidad="Medicina General",
                                colegiado="-",
                            )
                        else:
                            paciente = Paciente.objects.create(
                                user=user, 
                                fecha_nac="1900-01-01", # Valor por defecto requerido
                                descripcion="-",
                                telefono="-" # Valor por defecto requerido
                            )
                        
                        is_new_user = True

            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            serializer = UsuarioSerializer(user)

            try:
                doctor = Doctor.objects.get(user=user)
            except Doctor.DoesNotExist:
                doctor = None
            
            try:
                paciente = Paciente.objects.get(user=user)
            except Paciente.DoesNotExist:
                paciente = None

            if doctor: 
                return Response({
                    'user': serializer.data,
                    'doctor_id': {
                        'id': doctor.id,
                        'especialidad': doctor.especialidad,
                        'colegiado': doctor.colegiado,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK);
            
            if paciente: 
                return Response({
                    'user': serializer.data,
                    'paciente_id': {
                        'id': paciente.id,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK);
                
            return Response({
                'message': 'Usuario creado con Google exitosamente' if is_new_user else 'Inicio de sesión con Google exitoso',
                'is_new_user': is_new_user,
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED if is_new_user else status.HTTP_200_OK)

        except ValueError:
            # Token inválido
            return Response({
                'error': 'Token de Google inválido o expirado',
            }, status=status.HTTP_401_UNAUTHORIZED);

        except Exception as e:
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR);