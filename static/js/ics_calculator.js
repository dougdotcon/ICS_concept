document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('icsForm');
    const calculateBtn = document.getElementById('calculateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultCard = document.getElementById('resultCard');
    const errorAlert = document.getElementById('errorAlert');
    
    // Ativar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Event listener para o formulário
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        calculateICS();
    });
    
    // Função para calcular o ICS
    function calculateICS() {
        const formData = new FormData(form);
        const data = {};
        
        // Converter FormData para objeto JavaScript
        for (let [key, value] of formData.entries()) {
            if (value === '') {
                continue; // Pular campos vazios
            }
            
            // Converter checkboxes
            if (key.startsWith('fetch_')) {
                data[key] = value === 'on';
            }
            // Converter números
            else if (['father_salary', 'mother_salary', 'family_property_value', 
                     'family_financial_value', 'benefits_value', 'tax_paid'].includes(key)) {
                data[key] = parseFloat(value) || null;
            }
            // Outros campos como string
            else {
                data[key] = value;
            }
        }
        
        // Mostrar loading
        showLoading(true);
        hideError();
        hideResult();
        
        // Fazer requisição para a API
        axios.post('/api/calculate/', data, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            showLoading(false);
            displayResult(response.data);
        })
        .catch(error => {
            showLoading(false);
            const errorMsg = error.response?.data?.error || 'Erro interno do servidor';
            showError(errorMsg);
            console.error('Erro no cálculo:', error);
        });
    }
    
    // Função para mostrar/esconder loading
    function showLoading(show) {
        if (show) {
            calculateBtn.disabled = true;
            loadingSpinner.classList.remove('d-none');
        } else {
            calculateBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
        }
    }
    
    // Função para exibir o resultado
    function displayResult(data) {
        // Atualizar elementos do resultado
        document.getElementById('icsScore').textContent = data.ics_score.toFixed(3);
        document.getElementById('explanation').textContent = data.explanation;
        document.getElementById('confidence').textContent = (data.confidence * 100).toFixed(1) + '%';
        document.getElementById('percentile').textContent = `Percentil ${data.percentile.toFixed(0)}`;
        
        // Barra de confiança
        const confidenceBar = document.getElementById('confidenceBar');
        const confidencePercent = data.confidence * 100;
        confidenceBar.style.width = confidencePercent + '%';
        
        // Cor da barra baseada na confiança
        confidenceBar.className = 'progress-bar';
        if (confidencePercent >= 80) {
            confidenceBar.classList.add('bg-success');
        } else if (confidencePercent >= 60) {
            confidenceBar.classList.add('bg-warning');
        } else {
            confidenceBar.classList.add('bg-danger');
        }
        
        // Gráfico de componentes
        if (data.components) {
            drawComponentsChart(data.components);
        }
        
        // Mostrar card de resultado
        resultCard.classList.remove('d-none');
        resultCard.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Função para desenhar gráfico de componentes
    function drawComponentsChart(components) {
        const ctx = document.getElementById('componentsChart').getContext('2d');
        
        // Destruir gráfico anterior se existir
        if (window.icsChart) {
            window.icsChart.destroy();
        }
        
        const labels = Object.keys(components).map(key => {
            const labelMap = {
                'fiscal': 'Fiscal',
                'job': 'Trabalho',
                'patrimony': 'Patrimônio',
                'transfers': 'Transferências',
                'benefits': 'Benefícios'
            };
            return labelMap[key] || key;
        });
        
        const values = Object.values(components);
        const colors = ['#0d6efd', '#198754', '#fd7e14', '#6f42c1', '#dc3545'];
        
        window.icsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Valor Normalizado',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1.0,
                        ticks: {
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + (context.raw * 100).toFixed(1) + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Função para mostrar erro
    function showError(message) {
        errorAlert.textContent = message;
        errorAlert.classList.remove('d-none');
        errorAlert.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Função para esconder erro
    function hideError() {
        errorAlert.classList.add('d-none');
    }
    
    // Função para esconder resultado
    function hideResult() {
        resultCard.classList.add('d-none');
    }
    
    // Função para obter CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Validação em tempo real
    function setupFormValidation() {
        const numericInputs = document.querySelectorAll('input[type="number"]');
        
        numericInputs.forEach(input => {
            input.addEventListener('input', function() {
                if (this.value < 0) {
                    this.value = 0;
                }
            });
        });
        
        // Validação do estado (UF)
        const stateInput = document.getElementById('birthState');
        stateInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
            if (this.value.length > 2) {
                this.value = this.value.substring(0, 2);
            }
        });
    }
    
    // Inicializar validações
    setupFormValidation();
    
    // Auto-preenchimento de salários quando checkboxes são marcados
    document.getElementById('fetchFatherJob').addEventListener('change', function() {
        if (this.checked) {
            const jobInput = document.getElementById('fatherJob');
            const salaryInput = document.getElementById('fatherSalary');
            
            if (jobInput.value && !salaryInput.value) {
                // Simular busca de salário médio
                setTimeout(() => {
                    salaryInput.value = getAverageSalary(jobInput.value);
                    salaryInput.dispatchEvent(new Event('input'));
                }, 500);
            }
        }
    });
    
    document.getElementById('fetchMotherJob').addEventListener('change', function() {
        if (this.checked) {
            const jobInput = document.getElementById('motherJob');
            const salaryInput = document.getElementById('motherSalary');
            
            if (jobInput.value && !salaryInput.value) {
                // Simular busca de salário médio
                setTimeout(() => {
                    salaryInput.value = getAverageSalary(jobInput.value);
                    salaryInput.dispatchEvent(new Event('input'));
                }, 500);
            }
        }
    });
    
    // Função mock para buscar salário médio
    function getAverageSalary(jobTitle) {
        const salaries = {
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
        };
        
        for (const [job, salary] of Object.entries(salaries)) {
            if (jobTitle.toLowerCase().includes(job)) {
                return salary;
            }
        }
        
        return 2500; // Salário padrão
    }
}); 