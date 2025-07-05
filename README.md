<div align="center">
  <img src="logo.png" alt="ICS - Índice de Contribuição Social" width="200">
  <h1>ICS - Índice de Contribuição Social</h1>
  <p>Sistema para cálculo do Índice de Contribuição Social baseado em dados objetivos e APIs públicas</p>
  <hr>
</div>

## Sobre o Projeto

O ICS (Índice de Contribuição Social) é um sistema que calcula um índice de contribuição social baseado em dados objetivos como renda familiar, patrimônio, impostos pagos e outros fatores socioeconômicos. Este MVP (Minimum Viable Product) foi desenvolvido para validar rapidamente o conceito do ICS através de um sistema funcional.

### Objetivos

- Calcular o ICS com base em dados fornecidos pelo usuário
- Integrar com APIs públicas (IBGE, RAIS) para enriquecer os dados
- Fornecer explicações claras sobre o cálculo do índice
- Apresentar estatísticas e visualizações em um dashboard interativo
- Disponibilizar uma API REST para integração com outros sistemas

## Funcionalidades

### Interface Web

- **Formulário Intuitivo**: Campos organizados por categoria com validação em tempo real
- **Checkboxes de Integração**: Controle para busca automática de dados em APIs externas
- **Resultado Visual**: Score ICS, explicação detalhada e gráfico de componentes
- **Dashboard Completo**: Estatísticas agregadas, distribuição e histórico de cálculos

### API REST

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/calculate/` | POST | Calcular ICS com base nos dados fornecidos |
| `/api/dashboard/stats/` | GET | Obter estatísticas para o dashboard |
| `/api/profiles/` | GET | Listar todos os perfis calculados |
| `/api/profiles/{id}/` | GET | Obter detalhes de um perfil específico |
| `/api/health/` | GET | Verificar status do sistema |

### Algoritmo ICS v0

O cálculo do ICS é baseado em cinco componentes principais, cada um com seu peso específico:

| Componente | Peso | Cálculo |
|------------|------|---------|
| Fiscal | 30% | Impostos pagos / 10.000 |
| Trabalho | 25% | (Salário pai + mãe) / 20.000 |
| Patrimônio | 20% | (Imóveis + Financeiro) / 500.000 |
| Transferências | 15% | 1 se sem herança, 0 caso contrário |
| Benefícios | -10% | Benefícios recebidos / 10.000 |

**Fórmula:**
```
ICS = 0.30 * fiscal + 0.25 * trabalho + 0.20 * patrimônio + 0.15 * transferências - 0.10 * benefícios
```

**Classificação:**
- **Alto**: ≥ 0.7
- **Médio**: 0.4 - 0.7
- **Baixo**: < 0.4

## Tecnologias Utilizadas

### Stack Tecnológica
- **Backend**: Django 5.2.3 + Django REST Framework
- **Frontend**: HTML5 + Bootstrap 5 + JavaScript (Vanilla)
- **Banco de Dados**: SQLite (para MVP)
- **Gráficos**: Chart.js
- **APIs Externas**: IBGE, RAIS (mock)

### Estrutura do Projeto
```
ics/
├── core/                  # App principal
│   ├── models.py          # Modelos do banco
│   ├── views.py           # Views web e API
│   ├── services.py        # Lógica de negócio
│   ├── serializers.py     # Serializadores DRF
│   └── admin.py           # Configuração admin
├── templates/             # Templates HTML
├── static/                # Arquivos estáticos
├── ics_mvp/               # Configurações Django
└── requirements.txt       # Dependências
```

## Instalação e Execução

### Pré-requisitos
- Python 3.10+
- pip

### Passos

1. **Clone o repositório**
   ```bash
   git clone <repo-url>
   cd ics
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o banco de dados**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Crie um superusuário**
   ```bash
   python manage.py createsuperuser
   ```

5. **Execute o servidor**
   ```bash
   python manage.py runserver
   ```

6. **Popular dados de teste (opcional)**
   ```bash
   python populate_test_data.py
   ```

7. **Acesse o sistema**
   - Interface principal: http://localhost:8000/
   - Dashboard: http://localhost:8000/dashboard/
   - Admin: http://localhost:8000/admin/ (usuário: admin, senha: 123)

## Dados de Teste

O sistema já inclui 5 perfis de teste com dados realistas:

1. **São Paulo** - ICS: 0.894 (Alto)
   - Médico + Enfermeira, alto patrimônio
   
2. **Rio de Janeiro** - ICS: 0.251 (Baixo)
   - Professor + Auxiliar, patrimônio moderado
   
3. **Belo Horizonte** - ICS: 0.813 (Alto)
   - Engenheiro + Analista, bom patrimônio
   
4. **Salvador** - ICS: 0.343 (Baixo)
   - Vendedor + Técnico, patrimônio baixo
   
5. **Porto Alegre** - ICS: 0.663 (Médio)
   - Advogado + Gerente, patrimônio médio

Para testar a API, você pode usar o seguinte comando:

```bash
curl -X POST http://localhost:8000/api/calculate/ \
  -H "Content-Type: application/json" \
  -d '{
    "birth_place": "São Paulo",
    "father_job": "Médico",
    "father_salary": 15000,
    "mother_salary": 4500,
    "family_property_value": 800000,
    "inheritance_status": "sem",
    "tax_paid": 25000
  }'
```

## Métricas e Status

### Métricas de Sucesso
- **Meta de Correlação**: ≥ 0,6 entre ICS e percepção qualitativa
- **Amostra Mínima**: ≥ 50 perfis para validação estatística
- **Performance**: Tempo de resposta < 2s para cálculo do ICS

### Status Atual
- **Total de Perfis**: 5 perfis de teste
- **ICS Médio**: 0.593
- **Distribuição**: 2 baixo, 1 médio, 2 alto
- **Confiança Média**: 87.5%
- **Tempo de Resposta**: < 500ms

## Próximos Passos

### Melhorias Planejadas
1. **Integração LLM**: OpenAI para explicações mais detalhadas
2. **Deploy**: Configuração para Fly.io ou Railway
3. **Autenticação**: Sistema de usuários
4. **Exportação**: CSV/Excel dos dados
5. **Métricas**: Google Analytics integrado

### Evolução do Algoritmo
1. **Pesos Adaptativos**: Baseados em dados reais
2. **Normalização Dinâmica**: Percentis da base de dados
3. **Componentes Adicionais**: Educação, região, idade
4. **Machine Learning**: Predição de ICS

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto é um MVP para validação de conceito.

## Suporte

Para dúvidas sobre o projeto, entre em contato com a equipe de desenvolvimento. 