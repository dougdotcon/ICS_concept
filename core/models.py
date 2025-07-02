from django.db import models
import json


class ICSProfile(models.Model):
    """
    Armazena os dados de perfil e cálculos do ICS
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dados de nascimento
    birth_place = models.CharField(max_length=200, blank=True, null=True)
    birth_pib_per_capita = models.FloatField(blank=True, null=True)
    
    # Dados familiares
    father_job = models.CharField(max_length=200, blank=True, null=True)
    father_salary = models.FloatField(blank=True, null=True)
    mother_job = models.CharField(max_length=200, blank=True, null=True)
    mother_salary = models.FloatField(blank=True, null=True)
    
    # Patrimônio
    family_property_value = models.FloatField(blank=True, null=True)
    family_financial_value = models.FloatField(blank=True, null=True)
    
    # Herança e benefícios
    inheritance_status = models.CharField(
        max_length=50, 
        choices=[
            ('recebeu', 'Recebeu herança'),
            ('sem', 'Não recebeu/deserdado'),
            ('aguardando', 'Aguardando herança')
        ],
        blank=True, null=True
    )
    benefits_value = models.FloatField(blank=True, null=True)
    tax_paid = models.FloatField(blank=True, null=True)
    
    # Resultado do ICS
    ics_score = models.FloatField(blank=True, null=True)
    ics_explanation = models.TextField(blank=True, null=True)
    ics_confidence = models.FloatField(blank=True, null=True)
    
    # Dados brutos para auditoria
    raw_data = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "Perfil ICS"
        verbose_name_plural = "Perfis ICS"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"ICS Profile {self.id} - Score: {self.ics_score}"


class DataSource(models.Model):
    """
    Registra as fontes de dados utilizadas
    """
    name = models.CharField(max_length=100)
    api_url = models.URLField()
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class CalculationLog(models.Model):
    """
    Log de cálculos para auditoria e debugging
    """
    profile = models.ForeignKey(ICSProfile, on_delete=models.CASCADE)
    calculation_data = models.JSONField()
    weights_used = models.JSONField()
    result = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Cálculo {self.id} - Perfil {self.profile.id}"


class APICache(models.Model):
    """
    Cache simples para chamadas de API externas
    """
    cache_key = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Cache: {self.cache_key}"
