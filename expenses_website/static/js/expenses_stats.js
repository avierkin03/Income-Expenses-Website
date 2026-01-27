let currentChart = null;
let lastData = null;
let lastLabels = null;
let currentPeriod = '6m';
let customFrom = null;
let customTo = null;
let currency = '₴';  

// Функція оновлення / створення чарту
function renderOrUpdateChart(data, labels) {
    lastData = data;
    lastLabels = labels;

    const ctx = document.getElementById('myChart').getContext('2d');
    const chartType = document.getElementById('chartType').value;

    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }

    currentChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: 'Expenses',
                data: data,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#E7E9ED', '#C9CBCF', '#7BC225', '#F7464A',
                    '#FFCD56', '#C9CBCF', '#36A2EB'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Expenses by source',
                    font: { size: 18 }
                }
            },
            cutout: chartType === 'doughnut' ? '70%' : undefined,
        }
    });
}

// Оновлення карток з метриками
function updateMetrics(stats) {
    const row = document.getElementById('metrics-row');
    row.innerHTML = '';

    const metrics = [
        { title: "Total expenses", value: stats.total.toLocaleString('uk-UA', {style: 'currency', currency: currency}) },
        { title: "Daily average", value: stats.avg_per_day.toLocaleString('uk-UA', {style: 'currency', currency: currency}) },
        { title: "Monthly average", value: stats.avg_per_month.toLocaleString('uk-UA', {style: 'currency', currency: currency})},
        { title: "Transactions", value: stats.transaction_count },
        { title: "Top expense category", value: `${stats.top_category} (${stats.top_percent}%)` }
    ];

    metrics.forEach(m => {
        const col = document.createElement('div');
        col.className = 'col-md-3 col-6 mb-4';
        col.innerHTML = `
            <div class="card h-100 shadow-sm border-0">
                <div class="card-body text-center">
                    <h6 class="card-subtitle mb-2 text-muted">${m.title}</h6>
                    <h4 class="card-title fw-bold">${m.value}</h4>
                </div>
            </div>
        `;
        row.appendChild(col);
    });
}

// Завантаження даних з сервера
function loadChartData() {
    let url = `/expense-category-summary?period=${currentPeriod}`;

    if (currentPeriod === 'custom' && customFrom && customTo) {
        url += `&from=${customFrom}&to=${customTo}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(results => {
            const source_data = results.expenses_source_data;
            const labels = Object.keys(source_data);
            const data = Object.values(source_data);
            // Оновлюємо валюту з бекенду
            currency = results.currency || '₴';

            updateMetrics(results.stats);
            renderOrUpdateChart(data, labels);
        })
        .catch(err => console.error('Data loading error:', err));
}

// Обробники подій
document.addEventListener('DOMContentLoaded', () => {
    // Кнопки вибору періоду
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentPeriod = btn.dataset.period;
            document.getElementById('custom-period').classList.toggle('d-none', currentPeriod !== 'custom');

            if (currentPeriod !== 'custom') {
                loadChartData();
            }
        });
    });

    // Застосувати кастомний період
    document.getElementById('apply-custom')?.addEventListener('click', () => {
        customFrom = document.getElementById('date-from').value;
        customTo = document.getElementById('date-to').value;

        if (customFrom && customTo && customFrom <= customTo) {
            currentPeriod = 'custom';
            loadChartData();
        } else {
            alert('Please select a valid date range');
        }
    });

    // Зміна типу діаграми
    document.getElementById('chartType')?.addEventListener('change', () => {
        if (lastData && lastLabels) {
            renderOrUpdateChart(lastData, lastLabels);
        }
    });

    // Початкове завантаження
    loadChartData();
});