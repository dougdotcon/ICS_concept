from django.contrib import admin
from django.utils.html import format_html
from .models import ICSProfile, DataSource, CalculationLog, APICache


@admin.register(ICSProfile)
class ICSProfileAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'ics_score_display', 'birth_place', 'created_at', 
        'confidence_display', 'action_links'
    ]
    list_filter = ['created_at', 'inheritance_status']
    search_fields = ['birth_place', 'father_job', 'mother_job']
    readonly_fields = ['created_at', 'updated_at', 'ics_score', 'ics_explanation', 'ics_confidence']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Dados de Nascimento', {
            'fields': ('birth_place', 'birth_pib_per_capita')
        }),
        ('Dados Familiares', {
            'fields': (
                ('father_job', 'father_salary'),
                ('mother_job', 'mother_salary')
            )
        }),
        ('Patrimônio', {
            'fields': (
                ('family_property_value', 'family_financial_value'),
            )
        }),
        ('Herança e Benefícios', {
            'fields': (
                'inheritance_status',
                ('benefits_value', 'tax_paid')
            )
        }),
        ('Resultado ICS', {
            'fields': ('ics_score', 'ics_confidence', 'ics_explanation')
        }),
        ('Dados Brutos', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        })
    )
    
    def ics_score_display(self, obj):
        if obj.ics_score is not None:
            if obj.ics_score >= 0.7:
                color = 'green'
            elif obj.ics_score >= 0.4:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.3f}</span>',
                color, obj.ics_score
            )
        return '-'
    ics_score_display.short_description = 'ICS Score'
    
    def confidence_display(self, obj):
        if obj.ics_confidence is not None:
            percentage = obj.ics_confidence * 100
            return f'{percentage:.1f}%'
        return '-'
    confidence_display.short_description = 'Confiança'
    
    def action_links(self, obj):
        return format_html(
            '<a href="/admin/core/calculationlog/?profile__id={}" class="button">Ver Logs</a>',
            obj.id
        )
    action_links.short_description = 'Ações'


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'last_checked', 'api_url']
    list_filter = ['is_active', 'last_checked']
    search_fields = ['name', 'api_url']
    ordering = ['name']
    
    fields = ['name', 'api_url', 'is_active', 'last_checked']
    readonly_fields = ['last_checked']


@admin.register(CalculationLog)
class CalculationLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'profile_link', 'result_display', 'timestamp'
    ]
    list_filter = ['timestamp']
    search_fields = ['profile__id']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    fields = [
        'profile', 'result', 'timestamp', 
        'calculation_data', 'weights_used'
    ]
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/core/icsprofile/{}/change/">Perfil #{}</a>',
            obj.profile.id, obj.profile.id
        )
    profile_link.short_description = 'Perfil'
    
    def result_display(self, obj):
        if obj.result >= 0.7:
            color = 'green'
        elif obj.result >= 0.4:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.3f}</span>',
            color, obj.result
        )
    result_display.short_description = 'Resultado'


@admin.register(APICache)
class APICacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['cache_key']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        from django.utils import timezone
        expired = obj.expires_at < timezone.now()
        if expired:
            return format_html('<span style="color: red;">Expirado</span>')
        else:
            return format_html('<span style="color: green;">Válido</span>')
    is_expired.short_description = 'Status'
    
    actions = ['clear_expired_cache']
    
    def clear_expired_cache(self, request, queryset):
        from django.utils import timezone
        expired_count = APICache.objects.filter(expires_at__lt=timezone.now()).delete()[0]
        self.message_user(request, f'{expired_count} entradas de cache expiradas foram removidas.')
    clear_expired_cache.short_description = 'Limpar cache expirado'


# Configurações do admin site
admin.site.site_header = 'ICS MVP - Administração'
admin.site.site_title = 'ICS MVP Admin'
admin.site.index_title = 'Painel de Administração do ICS'
