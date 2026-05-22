
from django.urls import path, include
from .api import MedicamentoView, TratamientoView, PacienteTratamientoView, TratamientoMedicamentoView, DashboardPacienteView, TratamientosActivosPacienteView, TratamientosPacienteView, HistorialMedicacionView, EstadisticaAdherenciaView, DashboardDoctorView, PacientesDoctorView, ReportePacienteDoctorView, TratamientosDoctorView, RendimientoPorTratamientoView, TodayMedicationsView, TodayMetricsView, WeeklyAdherenceView, GlobalProgressView, TreatmentDetailView, MedicationRecordView, TreatmentMedicationDetailView, PatientTreatmentsView
urlpatterns = [

    path('medicamentos/', MedicamentoView.as_view(), name='medicamentos'),
    path('medicamentos/<int:id>/', MedicamentoView.as_view(), name='medicamento_detalle'),    

    path('tratamientos/', TratamientoView.as_view(), name='tratamientos'), 
    path('tratamientos/<uuid:id>/', TratamientoView.as_view(), name='tratamiento_detalle'), 

    path('paciente-tratamiento/', PacienteTratamientoView.as_view(), name='paciente_tratamiento'), 
    path('paciente-tratamiento/<int:id>/', PacienteTratamientoView.as_view(), name='paciente_tratamiento_detalle'), 

    path('tratamiento-medicamento/', TratamientoMedicamentoView.as_view(), name='tratamiento_medicamento'), 
    path('tratamiento-medicamento/<int:id>/', TratamientoMedicamentoView.as_view(), name='tratamiento_medicamento_detalle'), 
    path('dashboard-paciente/<int:id>/', DashboardPacienteView.as_view(), name='dashboard_paciente'),

    path('tratamientos-activos-paciente/<int:id>/', TratamientosActivosPacienteView.as_view(), name='tratamientos_activos_paciente'),
    path('pacientes/tratamiento/<int:id>/', TratamientosPacienteView.as_view(), name='tratamientos_paciente'),
    path('medication-history/', HistorialMedicacionView.as_view(), name='medication_history'),
    path('pacientes/<int:id>/adherence/', EstadisticaAdherenciaView.as_view(), name='adherence'),
    path('doctors/me/dashboard/', DashboardDoctorView.as_view(), name='dashboard_doctor'),
    path('doctors/pacientes/', PacientesDoctorView.as_view(), name='doctor_pacientes'),
    path('doctors/me/patients/<int:id>/report/', ReportePacienteDoctorView.as_view(), name='doctor_paciente_reporte'),
    path('doctors/me/treatments/', TratamientosDoctorView.as_view(), name='doctor_tratamientos'),
    path('doctors/me/treatments/<uuid:id>/stats/', RendimientoPorTratamientoView.as_view(), name='doctor_tratamiento_stats'),
    path('patients/<int:patientId>/today-medications/', TodayMedicationsView.as_view(), name='today_medications'),
    path('patients/<int:patientId>/today-metrics/', TodayMetricsView.as_view(), name='today_metrics'),
    path('patients/<int:patientId>/weekly-adherence/', WeeklyAdherenceView.as_view(), name='weekly_adherence'),
    path('patients/<int:patientId>/global-progress/', GlobalProgressView.as_view(), name='global_progress'),
    path('treatments/<uuid:treatmentId>/', TreatmentDetailView.as_view(), name='treatment_detail'),
    path('medication-records/', MedicationRecordView.as_view(), name='medication_records'),
    path('treatment-medications/<int:tmId>/detail/', TreatmentMedicationDetailView.as_view(), name='treatment_medication_detail'),
    path('patient-treatments/', PatientTreatmentsView.as_view(), name='patient_treatments'),

]