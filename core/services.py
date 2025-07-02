import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import APICache, CalculationLog, ICSProfile


class ICSCalculationService:
    """
    Serviço responsável pelo cálculo do ICS baseado nos dados do perfil
    """
    
    def __init__(self):
        self.weights = settings.ICS_CONFIG['DEFAULT_WEIGHTS']
    
    def calculate_ics(self, profile_data):
        """
        Calcula o ICS baseado nos dados do perfil
        """
        try:
            # Normalização dos dados
            fiscal = self._normalize_fiscal(profile_data.get('tax_paid', 0))
            job = self._normalize_job_income(
                profile_data.get('father_salary', 0),
                profile_data.get('mother_salary', 0)
            )
            patrimony = self._normalize_patrimony(
                profile_data.get('family_property_value', 0),
                profile_data.get('family_financial_value', 0)
            )
            transfers = self._normalize_transfers(
                profile_data.get('inheritance_status', 'sem')
            )
            benefits = self._normalize_benefits(
                profile_data.get('benefits_value', 0)
            )
            
            # Cálculo do ICS
            ics = (
                self.weights['fiscal'] * fiscal +
                self.weights['job'] * job +
                self.weights['patrimony'] * patrimony +
                self.weights['transfers'] * transfers +
                self.weights['benefits'] * benefits
            )
            
            # Garantir que o ICS esteja entre 0 e 1
            ics = max(0, min(1, ics))
            
            explanation = self._generate_explanation(
                fiscal, job, patrimony, transfers, benefits, ics
            )
            
            confidence = self._calculate_confidence(profile_data)
            
            return {
                'ics_score': ics,
                'explanation': explanation,
                'confidence': confidence,
                'components': {
                    'fiscal': fiscal,
                    'job': job,
                    'patrimony': patrimony,
                    'transfers': transfers,
                    'benefits': benefits
                }
            }
            
        except Exception as e:
            return {
                'error': f'Erro no cálculo do ICS: {str(e)}',
                'ics_score': 0,
                'explanation': 'Não foi possível calcular o ICS',
                'confidence': 0
            }
    
    def _normalize_fiscal(self, tax_paid):
        """Normaliza valores de impostos pagos"""
        return min(tax_paid / 10000, 1.0) if tax_paid else 0
    
    def _normalize_job_income(self, father_salary, mother_salary):
        """Normaliza renda familiar dos pais"""
        total_income = (father_salary or 0) + (mother_salary or 0)
        return min(total_income / 20000, 1.0)
    
    def _normalize_patrimony(self, property_value, financial_value):
        """Normaliza patrimônio familiar"""
        total_patrimony = (property_value or 0) + (financial_value or 0)
        return min(total_patrimony / 500000, 1.0)
    
    def _normalize_transfers(self, inheritance_status):
        """Normaliza status de herança"""
        return 1.0 if inheritance_status == 'sem' else 0.0
    
    def _normalize_benefits(self, benefits_value):
        """Normaliza benefícios sociais"""
        return min((benefits_value or 0) / 10000, 1.0)
    
    def _generate_explanation(self, fiscal, job, patrimony, transfers, benefits, ics):
        """Gera explicação do cálculo em linguagem natural"""
        components = []
        
        if fiscal > 0.5:
            components.append("alta contribuição fiscal")
        elif fiscal > 0.2:
            components.append("contribuição fiscal moderada")
        else:
            components.append("baixa contribuição fiscal")
            
        if job > 0.5:
            components.append("renda familiar elevada")
        elif job > 0.2:
            components.append("renda familiar moderada")
        else:
            components.append("renda familiar baixa")
            
        if patrimony > 0.5:
            components.append("patrimônio significativo")
        elif patrimony > 0.2:
            components.append("patrimônio moderado")
        else:
            components.append("patrimônio limitado")
            
        if transfers > 0.5:
            components.append("sem herança recebida")
        
        if benefits > 0.3:
            components.append("alto uso de benefícios sociais")
        elif benefits > 0.1:
            components.append("uso moderado de benefícios")
        
        score_text = "alto" if ics > 0.7 else "médio" if ics > 0.4 else "baixo"
        
        return f"ICS {score_text} ({ics:.2f}) baseado em: {', '.join(components)}."
    
    def _calculate_confidence(self, profile_data):
        """Calcula nível de confiança baseado na completude dos dados"""
        total_fields = 8  # número de campos principais
        filled_fields = sum(1 for key in [
            'tax_paid', 'father_salary', 'mother_salary',
            'family_property_value', 'family_financial_value',
            'inheritance_status', 'benefits_value', 'birth_pib_per_capita'
        ] if profile_data.get(key) is not None)
        
        return filled_fields / total_fields


class ExternalAPIService:
    """
    Serviço para integração com APIs externas (IBGE, RAIS, etc.)
    """
    
    def __init__(self):
        self.ibge_base = settings.ICS_CONFIG['IBGE_API_BASE']
        self.cache_timeout = settings.ICS_CONFIG['CACHE_TIMEOUT']
    
    def get_municipality_data(self, municipality_name, state_code=None):
        """
        Busca dados do município via API do IBGE
        """
        cache_key = f"ibge_municipality_{municipality_name}_{state_code}"
        
        # Verificar cache
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Buscar município
            url = f"{self.ibge_base}/localidades/municipios"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                municipalities = response.json()
                for muni in municipalities:
                    if municipality_name.lower() in muni['nome'].lower():
                        if not state_code or muni['microrregiao']['mesorregiao']['UF']['sigla'] == state_code:
                            # Buscar PIB do município
                            pib_data = self._get_municipality_pib(muni['id'])
                            
                            result = {
                                'municipality_id': muni['id'],
                                'name': muni['nome'],
                                'state': muni['microrregiao']['mesorregiao']['UF']['sigla'],
                                'pib_per_capita': pib_data.get('pib_per_capita', 0)
                            }
                            
                            # Cachear resultado
                            self._cache_data(cache_key, result)
                            return result
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar dados do município: {e}")
            return None
    
    def _get_municipality_pib(self, municipality_id):
        """
        Busca dados de PIB do município
        """
        try:
            # Esta seria a chamada real para a API do IBGE PIB
            # Por enquanto, retornamos um valor mockado
            return {'pib_per_capita': 25000}  # Valor exemplo
        except:
            return {'pib_per_capita': 0}
    
    def get_job_salary_data(self, job_title):
        """
        Busca dados salariais de uma profissão (mock para o MVP)
        """
        cache_key = f"job_salary_{job_title}"
        
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Mock de dados salariais por profissão
        job_salaries = {
            'médico': 15000,
            'enfermeiro': 4500,
            'professor': 3500,
            'engenheiro': 8000,
            'advogado': 7000,
            'técnico': 3000,
            'vendedor': 2500,
            'auxiliar': 1800,
            'gerente': 6000,
            'analista': 5000
        }
        
        # Busca aproximada
        for job, salary in job_salaries.items():
            if job.lower() in job_title.lower():
                result = {'average_salary': salary}
                self._cache_data(cache_key, result)
                return result
        
        # Salário padrão se não encontrar
        result = {'average_salary': 2500}
        self._cache_data(cache_key, result)
        return result
    
    def _get_cached_data(self, cache_key):
        """
        Recupera dados do cache se ainda válidos
        """
        try:
            cache_entry = APICache.objects.get(
                cache_key=cache_key,
                expires_at__gt=timezone.now()
            )
            return cache_entry.data
        except APICache.DoesNotExist:
            return None
    
    def _cache_data(self, cache_key, data):
        """
        Armazena dados no cache
        """
        expires_at = timezone.now() + timedelta(seconds=self.cache_timeout)
        
        APICache.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'data': data,
                'expires_at': expires_at
            }
        ) 