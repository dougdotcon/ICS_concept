#!/usr/bin/env python
"""
Script para popular dados de teste no sistema ICS MVP
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ics_mvp.settings')
django.setup()

from core.models import ICSProfile, DataSource
from core.services import ICSCalculationService
import random

def create_test_profiles():
    """Cria perfis de teste para demonstração"""
    
    # Dados fictícios para teste
    test_data = [
        {
            'birth_place': 'São Paulo',
            'father_job': 'Médico',
            'father_salary': 15000,
            'mother_job': 'Enfermeira',
            'mother_salary': 4500,
            'family_property_value': 800000,
            'family_financial_value': 200000,
            'inheritance_status': 'sem',
            'benefits_value': 0,
            'tax_paid': 25000,
        },
        {
            'birth_place': 'Rio de Janeiro',
            'father_job': 'Professor',
            'father_salary': 3500,
            'mother_job': 'Auxiliar',
            'mother_salary': 1800,
            'family_property_value': 200000,
            'family_financial_value': 50000,
            'inheritance_status': 'recebeu',
            'benefits_value': 500,
            'tax_paid': 3000,
        },
        {
            'birth_place': 'Belo Horizonte',
            'father_job': 'Engenheiro',
            'father_salary': 8000,
            'mother_job': 'Analista',
            'mother_salary': 5000,
            'family_property_value': 500000,
            'family_financial_value': 150000,
            'inheritance_status': 'sem',
            'benefits_value': 0,
            'tax_paid': 15000,
        },
        {
            'birth_place': 'Salvador',
            'father_job': 'Vendedor',
            'father_salary': 2500,
            'mother_job': 'Técnico',
            'mother_salary': 3000,
            'family_property_value': 150000,
            'family_financial_value': 30000,
            'inheritance_status': 'sem',
            'benefits_value': 800,
            'tax_paid': 2000,
        },
        {
            'birth_place': 'Porto Alegre',
            'father_job': 'Advogado',
            'father_salary': 7000,
            'mother_job': 'Gerente',
            'mother_salary': 6000,
            'family_property_value': 600000,
            'family_financial_value': 180000,
            'inheritance_status': 'aguardando',
            'benefits_value': 0,
            'tax_paid': 18000,
        }
    ]
    
    calc_service = ICSCalculationService()
    created_profiles = []
    
    for data in test_data:
        # Calcular ICS
        result = calc_service.calculate_ics(data)
        
        # Criar perfil
        profile = ICSProfile.objects.create(
            birth_place=data['birth_place'],
            birth_pib_per_capita=random.randint(20000, 40000),  # PIB fictício
            father_job=data['father_job'],
            father_salary=data['father_salary'],
            mother_job=data['mother_job'],
            mother_salary=data['mother_salary'],
            family_property_value=data['family_property_value'],
            family_financial_value=data['family_financial_value'],
            inheritance_status=data['inheritance_status'],
            benefits_value=data['benefits_value'],
            tax_paid=data['tax_paid'],
            ics_score=result['ics_score'],
            ics_explanation=result['explanation'],
            ics_confidence=result['confidence'],
            raw_data=data
        )
        
        created_profiles.append(profile)
        print(f"✓ Criado perfil {profile.id}: {profile.birth_place} - ICS: {profile.ics_score:.3f}")
    
    return created_profiles

def create_data_sources():
    """Cria fontes de dados de exemplo"""
    
    sources = [
        {
            'name': 'API IBGE PIB Municipal',
            'api_url': 'https://servicodados.ibge.gov.br/api/v1/sidra/table/5938',
            'is_active': True
        },
        {
            'name': 'RAIS Microdados',
            'api_url': 'https://basedosdados.org/dataset/rais',
            'is_active': True
        },
        {
            'name': 'CAGED',
            'api_url': 'https://api.gov.br/caged',
            'is_active': False
        }
    ]
    
    created_sources = []
    for source_data in sources:
        source, created = DataSource.objects.get_or_create(
            name=source_data['name'],
            defaults=source_data
        )
        if created:
            print(f"✓ Criada fonte de dados: {source.name}")
        else:
            print(f"• Fonte de dados já existe: {source.name}")
        created_sources.append(source)
    
    return created_sources

def main():
    """Função principal"""
    print("🚀 Populando dados de teste do ICS MVP...")
    print()
    
    # Limpar dados existentes (opcional)
    if '--clear' in sys.argv:
        print("🗑️  Removendo dados existentes...")
        ICSProfile.objects.all().delete()
        DataSource.objects.all().delete()
        print()
    
    # Criar fontes de dados
    print("📊 Criando fontes de dados...")
    sources = create_data_sources()
    print(f"Total de fontes: {len(sources)}")
    print()
    
    # Criar perfis de teste
    print("👥 Criando perfis de teste...")
    profiles = create_test_profiles()
    print(f"Total de perfis: {len(profiles)}")
    print()
    
    # Estatísticas
    print("📈 Estatísticas:")
    avg_score = sum(p.ics_score for p in profiles) / len(profiles)
    max_score = max(p.ics_score for p in profiles)
    min_score = min(p.ics_score for p in profiles)
    
    print(f"  • ICS médio: {avg_score:.3f}")
    print(f"  • ICS máximo: {max_score:.3f}")
    print(f"  • ICS mínimo: {min_score:.3f}")
    print()
    
    print("✅ Dados de teste criados com sucesso!")
    print("🌐 Acesse http://localhost:8000/ para testar o sistema")
    print("📊 Dashboard: http://localhost:8000/dashboard/")
    print("⚙️  Admin: http://localhost:8000/admin/ (admin/123)")

if __name__ == '__main__':
    main() 