from django.shortcuts import render
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.generic import TemplateView

from .models import ICSProfile, CalculationLog, DataSource
from .serializers import (
    ICSFormDataSerializer, ICSResultSerializer, 
    ICSProfileSerializer, DashboardStatsSerializer
)
from .services import ICSCalculationService, ExternalAPIService
from django.conf import settings


class HomeView(TemplateView):
    """
    View principal com formulário do ICS
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_sources'] = DataSource.objects.filter(is_active=True)
        return context


class DashboardView(TemplateView):
    """
    Dashboard com estatísticas do ICS
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas básicas
        profiles = ICSProfile.objects.filter(ics_score__isnull=False)
        context['total_profiles'] = profiles.count()
        context['avg_score'] = profiles.aggregate(avg=Avg('ics_score'))['avg'] or 0
        
        # Distribuição de scores
        score_ranges = {
            'baixo': profiles.filter(ics_score__lt=0.4).count(),
            'medio': profiles.filter(ics_score__gte=0.4, ics_score__lt=0.7).count(),
            'alto': profiles.filter(ics_score__gte=0.7).count(),
        }
        context['score_distribution'] = score_ranges
        
        # Últimos cálculos
        context['recent_profiles'] = profiles.order_by('-created_at')[:10]
        
        return context


@api_view(['GET'])
def health_check(request):
    """
    Endpoint de health check
    """
    return Response({
        'status': 'ok',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })


class ICSCalculationAPIView(APIView):
    """
    API para cálculo do ICS
    """
    
    def post(self, request):
        """
        Processa formulário e calcula ICS
        """
        serializer = ICSFormDataSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Dados inválidos',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = serializer.validated_data
            
            # Enriquecer dados com APIs externas se solicitado
            enriched_data = self._enrich_data_from_apis(data)
            
            # Calcular ICS
            calc_service = ICSCalculationService()
            result = calc_service.calculate_ics(enriched_data)
            
            # Salvar perfil
            profile = self._save_profile(enriched_data, result)
            
            # Adicionar dados estatísticos
            result['profile_id'] = profile.id
            result['avg_score'] = self._get_average_score()
            result['percentile'] = self._calculate_percentile(result['ics_score'])
            
            # Log do cálculo
            self._log_calculation(profile, enriched_data, result)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Erro interno no cálculo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _enrich_data_from_apis(self, data):
        """
        Enriquece dados usando APIs externas baseado nos checkboxes
        """
        enriched_data = data.copy()
        api_service = ExternalAPIService()
        
        # Buscar dados de nascimento se solicitado
        if data.get('fetch_birth_data') and data.get('birth_place'):
            birth_data = api_service.get_municipality_data(
                data['birth_place'], 
                data.get('birth_state')
            )
            if birth_data:
                enriched_data['birth_pib_per_capita'] = birth_data.get('pib_per_capita', 0)
        
        # Buscar dados salariais do pai se solicitado
        if data.get('fetch_father_job') and data.get('father_job'):
            job_data = api_service.get_job_salary_data(data['father_job'])
            if job_data and not data.get('father_salary'):
                enriched_data['father_salary'] = job_data.get('average_salary', 0)
        
        # Buscar dados salariais da mãe se solicitado
        if data.get('fetch_mother_job') and data.get('mother_job'):
            job_data = api_service.get_job_salary_data(data['mother_job'])
            if job_data and not data.get('mother_salary'):
                enriched_data['mother_salary'] = job_data.get('average_salary', 0)
        
        return enriched_data
    
    def _save_profile(self, data, result):
        """
        Salva perfil no banco de dados
        """
        profile = ICSProfile.objects.create(
            birth_place=data.get('birth_place'),
            birth_pib_per_capita=data.get('birth_pib_per_capita'),
            father_job=data.get('father_job'),
            father_salary=data.get('father_salary'),
            mother_job=data.get('mother_job'),
            mother_salary=data.get('mother_salary'),
            family_property_value=data.get('family_property_value'),
            family_financial_value=data.get('family_financial_value'),
            inheritance_status=data.get('inheritance_status'),
            benefits_value=data.get('benefits_value'),
            tax_paid=data.get('tax_paid'),
            ics_score=result.get('ics_score'),
            ics_explanation=result.get('explanation'),
            ics_confidence=result.get('confidence'),
            raw_data=data
        )
        return profile
    
    def _get_average_score(self):
        """
        Calcula score médio dos perfis existentes
        """
        avg = ICSProfile.objects.filter(
            ics_score__isnull=False
        ).aggregate(avg=Avg('ics_score'))['avg']
        return avg or 0
    
    def _calculate_percentile(self, score):
        """
        Calcula percentil do score
        """
        lower_scores = ICSProfile.objects.filter(
            ics_score__lt=score,
            ics_score__isnull=False
        ).count()
        
        total_scores = ICSProfile.objects.filter(
            ics_score__isnull=False
        ).count()
        
        if total_scores == 0:
            return 50  # Percentil neutro se não há dados
        
        return (lower_scores / total_scores) * 100
    
    def _log_calculation(self, profile, input_data, result):
        """
        Registra log do cálculo
        """
        CalculationLog.objects.create(
            profile=profile,
            calculation_data=input_data,
            weights_used=settings.ICS_CONFIG['DEFAULT_WEIGHTS'],
            result=result.get('ics_score', 0)
        )


@api_view(['GET'])
def dashboard_stats_api(request):
    """
    API para estatísticas do dashboard
    """
    try:
        profiles = ICSProfile.objects.filter(ics_score__isnull=False)
        
        # Estatísticas básicas
        total_profiles = profiles.count()
        avg_score = profiles.aggregate(avg=Avg('ics_score'))['avg'] or 0
        
        # Calcular mediana (aproximação simples)
        scores_ordered = profiles.order_by('ics_score').values_list('ics_score', flat=True)
        median_score = 0
        if scores_ordered:
            middle = len(scores_ordered) // 2
            if len(scores_ordered) % 2 == 0:
                median_score = (scores_ordered[middle-1] + scores_ordered[middle]) / 2
            else:
                median_score = scores_ordered[middle]
        
        # Distribuição de scores
        score_distribution = {
            'baixo (0-0.4)': profiles.filter(ics_score__lt=0.4).count(),
            'médio (0.4-0.7)': profiles.filter(ics_score__gte=0.4, ics_score__lt=0.7).count(),
            'alto (0.7-1.0)': profiles.filter(ics_score__gte=0.7).count(),
        }
        
        # Cálculos recentes
        recent_profiles = profiles.order_by('-created_at')[:5]
        recent_calculations = []
        
        for profile in recent_profiles:
            recent_calculations.append({
                'ics_score': profile.ics_score,
                'explanation': profile.ics_explanation,
                'confidence': profile.ics_confidence,
                'components': {},  # Seria necessário recalcular ou armazenar
                'profile_id': profile.id
            })
        
        data = {
            'total_profiles': total_profiles,
            'avg_ics_score': round(avg_score, 3),
            'median_ics_score': round(median_score, 3),
            'score_distribution': score_distribution,
            'recent_calculations': recent_calculations
        }
        
        return Response(data)
        
    except Exception as e:
        return Response({
            'error': f'Erro ao buscar estatísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def profile_list_api(request):
    """
    Lista de perfis ICS
    """
    profiles = ICSProfile.objects.filter(ics_score__isnull=False).order_by('-created_at')
    serializer = ICSProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def profile_detail_api(request, profile_id):
    """
    Detalhes de um perfil específico
    """
    try:
        profile = ICSProfile.objects.get(id=profile_id)
        serializer = ICSProfileSerializer(profile)
        return Response(serializer.data)
    except ICSProfile.DoesNotExist:
        return Response({
            'error': 'Perfil não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
