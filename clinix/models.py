from typing import Required
import uuid
from django.db import models

class Paciente(models.Model): 
    user = models.OneToOneField("autentication.Usuario", on_delete=models.CASCADE)
    fecha_nac = models.DateField()
    descripcion = models.TextField()
    telefono = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

class Doctor(models.Model): 
    user = models.OneToOneField("autentication.Usuario", on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=20)
    colegiado = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

class Medicamento(models.Model): 
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    nombre_medicamento = models.CharField(max_length=20) 
    descripcion = models.TextField() 
    is_active = models.BooleanField(default=True)
    imagen = models.URLField(null=True, blank=True);

    def __str__(self):
        return self.nombre_medicamento 

class Tratamiento(models.Model): 
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=20)
    descripcion = models.TextField()
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.titulo 

class PacienteTratamiento(models.Model): 
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

class TratamientoMedicamento(models.Model): 
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    dosis = models.CharField(max_length=20)
    frecuencia = models.CharField(max_length=30, default='Diario')
    horario = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    instrucciones = models.TextField()
    duracion_dias = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self): 
        return self.medicamento.nombre_medicamento

class RegistroMedication(models.Model): 
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    tratamiento_medicamento = models.ForeignKey(TratamientoMedicamento, on_delete=models.CASCADE)
    fecha_toma = models.DateField()
    estado = models.CharField(max_length=5, default=1) # 1 estado registrado, 2, tomado, 3, atrasado 
    hora = models.TimeField()
    foto = models.ImageField(upload_to='registro_medicacion', null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self): 
        return f"{self.paciente.user.email} - {self.tratamiento_medicamento.medicamento.nombre_medicamento}" 

class ChatMessage(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10, choices=[('user', 'Usuario'), ('assistant', 'Asistente')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']