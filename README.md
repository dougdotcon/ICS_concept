# ICS MVP - Índice de Contribuição Social

Sistema MVP para cálculo do Índice de Contribuição Social (ICS) baseado em dados objetivos e APIs públicas.

## 🎯 Objetivo

Validar rapidamente o conceito do ICS através de um sistema simplificado que:
- Coleta dados através de formulário web
- Integra com APIs públicas (IBGE, RAIS)
- Calcula ICS usando algoritmo com pesos fixos
- Fornece explicação em linguagem natural
- Apresenta dashboard com estatísticas

## 🏗️ Arquitetura

### Stack Tecnológica
- **Backend**: Django 5.2.3 + Django REST Framework
- **Frontend**: HTML5 + Bootstrap 5 + JavaScript (Vanilla)
- **Banco de Dados**: SQLite (para MVP)
- **Gráficos**: Chart.js
- **APIs Externas**: IBGE, RAIS (mock)

### Estrutura do Projeto
```
ics/
├── core/                   # App principal
│   ├── models.py          # Modelos do banco
│   ├── views.py           # Views web e API
│   ├── services.py        # Lógica de negócio
│   ├── serializers.py     # Serializadores DRF
│   └── admin.py           # Configuração admin
├── templates/             # Templates HTML
├── static/               # Arquivos estáticos
├── ics_mvp/              # Configurações Django
└── requirements.txt      # Dependências
```

## 🧮 Algoritmo ICS v0

### Componentes e Pesos
- **Fiscal** (30%): Impostos pagos / 10.000
- **Trabalho** (25%): (Salário pai + mãe) / 20.000
- **Patrimônio** (20%): (Imóveis + Financeiro) / 500.000
- **Transferências** (15%): 1 se sem herança, 0 caso contrário
- **Benefícios** (-10%): Benefícios recebidos / 10.000

### Fórmula
```python
ICS = 0.30 * fiscal + 0.25 * trabalho + 0.20 * patrimônio + 
      0.15 * transferências - 0.10 * benefícios
```

## 📊 Funcionalidades

### Interface Web
- **Formulário Intuitivo**: Checkboxes para controlar busca de dados
- **Validação em Tempo Real**: Campos com validação automática
- **Resultado Visual**: Score, explicação e gráfico de componentes
- **Dashboard**: Estatísticas agregadas e histórico

### API REST
- `POST /api/calculate/` - Calcular ICS
- `GET /api/dashboard/stats/` - Estatísticas do dashboard
- `GET /api/profiles/` - Listar perfis
- `GET /api/profiles/{id}/` - Detalhes do perfil
- `GET /api/health/` - Health check

### Integrações
- **API IBGE**: PIB per capita municipal
- **RAIS/CAGED**: Salários médios por profissão (mock)
- **Cache**: Sistema de cache para APIs externas

## 🚀 Instalação e Execução

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

6. **Acesse o sistema**
- Interface principal: http://localhost:8000/
- Dashboard: http://localhost:8000/dashboard/
- Admin: http://localhost:8000/admin/

## 📈 Métricas de Sucesso

### Meta do Piloto
- **Correlação ≥ 0,6** entre ICS e percepção qualitativa de "contribuição social"
- **≥ 50 perfis** coletados para validação
- **Tempo de resposta < 2s** para cálculo do ICS

### KPIs
- Taxa de preenchimento completo do formulário
- Confiança média dos cálculos
- Distribuição de scores ICS
- Uso das integrações com APIs

## 🔧 Desenvolvimento

### Estrutura de Dados

#### ICSProfile
```python
{
    "birth_place": "São Paulo",
    "father_job": "Engenheiro",
    "father_salary": 8000.0,
    "mother_job": "Professora", 
    "mother_salary": 3500.0,
    "family_property_value": 500000.0,
    "inheritance_status": "sem",
    "ics_score": 0.65,
    "ics_explanation": "ICS médio (0.65) baseado em..."
}
```

#### Resposta da API
```json
{
    "ics_score": 0.654,
    "explanation": "ICS médio (0.65) baseado em: contribuição fiscal moderada, renda familiar elevada...",
    "confidence": 0.8,
    "components": {
        "fiscal": 0.3,
        "job": 0.55,
        "patrimony": 1.0,
        "transfers": 1.0,
        "benefits": 0.0
    },
    "percentile": 75.2,
    "avg_score": 0.52
}
```

### Próximas Implementações
1. **Integração LLM**: OpenAI para explicações mais detalhadas
2. **Deploy**: Configuração para Fly.io ou Railway
3. **Autenticação**: Sistema de usuários
4. **Exportação**: CSV/Excel dos dados
5. **Métricas**: Google Analytics integrado

## 🧪 Testes

### Teste Manual
1. Acesse http://localhost:8000/
2. Preencha o formulário com dados fictícios
3. Marque checkboxes para testar integrações
4. Verifique se o resultado é exibido corretamente
5. Acesse o dashboard para ver estatísticas

### Dados de Teste
```json
{
    "birth_place": "São Paulo",
    "birth_state": "SP",
    "father_job": "Médico",
    "mother_job": "Enfermeira",
    "family_property_value": 800000,
    "family_financial_value": 200000,
    "inheritance_status": "sem",
    "benefits_value": 0,
    "tax_paid": 25000,
    "fetch_birth_data": true,
    "fetch_father_job": true,
    "fetch_mother_job": true
}
```

## 📝 Licença

Este é um projeto MVP para validação de conceito.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas sobre o projeto, entre em contato com a equipe de desenvolvimento. 