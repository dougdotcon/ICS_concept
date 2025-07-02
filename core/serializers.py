from rest_framework import serializers
from .models import ICSProfile, CalculationLog


class ICSProfileSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo ICSProfile
    """
    
    class Meta:
        model = ICSProfile
        fields = [
            'id', 'created_at', 'updated_at',
            'birth_place', 'birth_pib_per_capita',
            'father_job', 'father_salary', 'mother_job', 'mother_salary',
            'family_property_value', 'family_financial_value',
            'inheritance_status', 'benefits_value', 'tax_paid',
            'ics_score', 'ics_explanation', 'ics_confidence',
            'raw_data'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ics_score', 'ics_explanation', 'ics_confidence']


class ICSFormDataSerializer(serializers.Serializer):
    """
    Serializador para dados do formulário ICS
    """
    # Checkboxes para controle de busca de dados
    fetch_birth_data = serializers.BooleanField(default=False)
    fetch_father_job = serializers.BooleanField(default=False)
    fetch_mother_job = serializers.BooleanField(default=False)
    
    # Dados de nascimento
    birth_place = serializers.CharField(max_length=200, required=False, allow_blank=True)
    birth_state = serializers.CharField(max_length=2, required=False, allow_blank=True)
    
    # Dados familiares
    father_job = serializers.CharField(max_length=200, required=False, allow_blank=True)
    father_salary = serializers.FloatField(required=False, allow_null=True)
    mother_job = serializers.CharField(max_length=200, required=False, allow_blank=True)
    mother_salary = serializers.FloatField(required=False, allow_null=True)
    
    # Patrimônio (campos livres no MVP)
    family_property_value = serializers.FloatField(required=False, allow_null=True)
    family_financial_value = serializers.FloatField(required=False, allow_null=True)
    
    # Herança e benefícios (campos livres no MVP)
    inheritance_status = serializers.ChoiceField(
        choices=[('recebeu', 'Recebeu herança'), ('sem', 'Não recebeu/deserdado'), ('aguardando', 'Aguardando herança')],
        required=False,
        allow_blank=True
    )
    benefits_value = serializers.FloatField(required=False, allow_null=True)
    tax_paid = serializers.FloatField(required=False, allow_null=True)


class ICSResultSerializer(serializers.Serializer):
    """
    Serializador para o resultado do cálculo ICS
    """
    ics_score = serializers.FloatField()
    explanation = serializers.CharField()
    confidence = serializers.FloatField()
    components = serializers.DictField()
    profile_id = serializers.IntegerField(required=False)
    
    # Dados estatísticos para comparação
    avg_score = serializers.FloatField(required=False)
    percentile = serializers.FloatField(required=False)


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializador para estatísticas do dashboard
    """
    total_profiles = serializers.IntegerField()
    avg_ics_score = serializers.FloatField()
    median_ics_score = serializers.FloatField()
    score_distribution = serializers.DictField()
    recent_calculations = ICSResultSerializer(many=True)


class CalculationLogSerializer(serializers.ModelSerializer):
    """
    Serializador para logs de cálculo
    """
    
    class Meta:
        model = CalculationLog
        fields = ['id', 'profile', 'calculation_data', 'weights_used', 'result', 'timestamp']
        read_only_fields = ['id', 'timestamp'] 