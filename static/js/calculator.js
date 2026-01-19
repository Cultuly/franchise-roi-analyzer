document.addEventListener('DOMContentLoaded', function() {
    const regionsData = {};
    document.querySelectorAll('#region-select option').forEach(option => {
        if (option.value) {
            regionsData[option.value] = {
                rent: parseFloat(option.getAttribute('data-rent')),
                salaryCoeff: parseFloat(option.getAttribute('data-salary-coeff'))
            };
        }
    });

    document.getElementById('region-select').addEventListener('change', function() {
        updateCalculations();
    });

    ['premises-area', 'staff-count', 'avg-check'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateCalculations);
    });

    function updateCalculations() {
        const regionId = document.getElementById('region-select').value;
        if (!regionId) return;

        const region = regionsData[regionId];
        const premisesArea = parseFloat(document.getElementById('premises-area').value) || 50;

        const staffCount = parseFloat(document.getElementById('staff-count').value) || 4;

        const monthlyRent = region.rent * premisesArea;
        document.getElementById('rent-display').value = monthlyRent.toLocaleString('ru-RU');

        const baseSalary = 45000;
        const avgSalary = baseSalary * region.salaryCoeff;
        const totalSalary = avgSalary * staffCount;
        document.getElementById('salary-display').value = totalSalary.toLocaleString('ru-RU');
    }

    document.getElementById('calculate-btn').addEventListener('click', function() {
        const regionId = document.getElementById('region-select').value;
        if (!regionId) {
            alert('Пожалуйста, выберите регион');
            return;
        }

        const data = {
            region_id: regionId,
            establishment_type: document.getElementById('establishment-type').value,
            premises_area: parseFloat(document.getElementById('premises-area').value),
            staff_count: parseFloat(document.getElementById('staff-count').value),
            initial_fee: parseFloat(document.getElementById('initial-fee').value),
            royalty_percent: parseFloat(document.getElementById('royalty-percent').value),
            avg_check: parseFloat(document.getElementById('avg-check').value)
        };

        document.getElementById('error-message').style.display = 'none';
        document.getElementById('unprofitable-alert').style.display = 'none';
        document.getElementById('export-pdf-btn').style.display = 'none';

        fetch("/analytics/api/calculate/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                displayResults(result.results, result.chart_data, result.monthly_chart_data);
                document.getElementById('export-pdf-btn').style.display = 'block';
            } else {
                const errorMessage = document.getElementById('error-message');
                errorMessage.textContent = 'Ошибка: ' + result.error;
                errorMessage.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            const errorMessage = document.getElementById('error-message');
            errorMessage.textContent = 'Произошла ошибка при расчете. Попробуйте позже.';
            errorMessage.style.display = 'block';
        });
    });

    document.getElementById('export-pdf-btn').addEventListener('click', function() {
        exportToPDF();
    });

    function displayResults(results, chartData, monthlyChartData) {
        document.getElementById('results-section').style.display = 'block';
        document.getElementById('chart-section').style.display = 'block';
        document.getElementById('revenue-chart-section').style.display = 'block';

        document.getElementById('results-section').scrollIntoView({behavior: 'smooth'});

        if (results.payback_period === null) {
            document.getElementById('unprofitable-alert').style.display = 'block';
            document.getElementById('unprofitable-alert').textContent = 'Проект нерентабельный: ежемесячные расходы превышают выручку.';
            document.getElementById('payback-period').textContent = 'Нерентабельно';
            document.getElementById('monthly-profit').textContent = results.monthly_profit.toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('roi-display').textContent = '0.0';
        } else {
            document.getElementById('payback-period').textContent =
                results.payback_period < 36 ? results.payback_period.toFixed(1) : '>36';
            document.getElementById('monthly-profit').textContent =
                results.monthly_profit.toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('roi-display').textContent = results.roi_annual.toFixed(1);
        }

        generatePaybackChart(chartData);
        generateRevenueChart(monthlyChartData);
    }

    function formatCurrency(value) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }

    function generatePaybackChart(chartData) {
        const months = chartData.data.map(item => item.month);
        const cumulativeProfit = chartData.data.map(item => item.cumulative_profit);
        const cumulativeRevenue = chartData.data.map(item => item.cumulative_revenue);
        const cumulativeExpenses = chartData.data.map(item => item.cumulative_expenses);
        const breakEvenMonth = chartData.break_even_month;

        const traceProfit = {
            x: months,
            y: cumulativeProfit,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Накопленная прибыль',
            line: {color: '#2ecc71', width: 3},
            marker: {size: 8}
        };

        const traceRevenue = {
            x: months,
            y: cumulativeRevenue,
            type: 'scatter',
            mode: 'lines',
            name: 'Выручка',
            line: {color: '#3498db', width: 2, dash: 'dot'},
            yaxis: 'y2'
        };

        const traceExpenses = {
            x: months,
            y: cumulativeExpenses,
            type: 'scatter',
            mode: 'lines',
            name: 'Расходы',
            line: {color: '#e74c3c', width: 2, dash: 'dot'},
            yaxis: 'y2'
        };

        const layout = {
            title: 'Прогноз окупаемости проекта',
            xaxis: {
                title: 'Месяцы',
                range: [0, Math.max(12, breakEvenMonth ? breakEvenMonth + 3 : 12)],
                autorange: false
            },
            yaxis: {
                title: 'Накопленная прибыль (₽)',
                zeroline: true,
                zerolinecolor: '#969696',
                zerolinewidth: 1,
                tickformat: ',.0f'
            },
            yaxis2: {
                title: 'Выручка / Расходы (₽)',
                overlaying: 'y',
                side: 'right',
                showgrid: false,
                tickformat: ',.0f'
            },
            hovermode: 'x unified',
            margin: {l: 50, r: 100, t: 30, b: 40},
            showlegend: false,
            shapes: breakEvenMonth ? [{
                type: 'line',
                x0: breakEvenMonth,
                y0: 0,
                x1: breakEvenMonth,
                y1: 1,
                yref: 'paper',
                line: {
                    color: '#e74c3c',
                    width: 2,
                    dash: 'dash'
                }
            }] : [],
            annotations: breakEvenMonth ? [{
                x: breakEvenMonth,
                y: 0,
                xref: 'x',
                yref: 'y',
                text: `Точка безубыточности: ${breakEvenMonth.toFixed(1)} мес`,
                showarrow: true,
                arrowhead: 7,
                ax: 0,
                ay: -40,
                bgcolor: 'rgba(231, 76, 60, 0.8)',
                font: {color: 'white'}
            }] : []
        };

        Plotly.newPlot('payback-chart', [traceProfit, traceRevenue, traceExpenses], layout, {
            responsive: true,
            displayModeBar: false,
            scrollZoom: true
        });

        Plotly.newPlot('pdf-payback-chart', [traceProfit, traceRevenue, traceExpenses], {
            ...layout,
            width: 1100,
            height: 400,
            margin: {l: 60, r: 120, t: 40, b: 50}
        }, {
            staticPlot: true
        });
    }

    function generateRevenueChart(chartData) {
        const months = chartData.months;
        const revenue = chartData.revenue;
        const expenses = chartData.expenses;
        const profit = chartData.profit;

        const traceRevenue = {
            x: months,
            y: revenue,
            type: 'bar',
            name: 'Выручка',
            marker: {color: '#2ecc71'},
            hovertemplate: 'Выручка: %{y:.2f} ₽<extra></extra>'
        };

        const traceExpenses = {
            x: months,
            y: expenses,
            type: 'bar',
            name: 'Расходы',
            marker: {color: '#e74c3c'},
            hovertemplate: 'Расходы: %{y:.2f} ₽<extra></extra>'
        };

        const traceProfit = {
            x: months,
            y: profit,
            type: 'bar',
            name: 'Прибыль',
            marker: {color: '#3498db'},
            hovertemplate: 'Прибыль: %{y:.2f} ₽<extra></extra>'
        };

        const layout = {
            title: 'Ежемесячные показатели',
            barmode: 'group',
            xaxis: {
                title: 'Месяцы',
                range: [0.5, 12.5],
                dtick: 1
            },
            yaxis: {
                title: 'Сумма (₽)',
                hoverformat: ',.2f',
                tickformat: ',.0f',
                rangemode: 'tozero'
            },
            hovermode: 'x unified',
            margin: {l: 50, r: 50, t: 30, b: 40},
            legend: {
                x: 0.05,
                y: 0.95,
                bgcolor: 'rgba(255, 255, 255, 0.5)',
                bordercolor: 'rgba(0, 0, 0, 0.2)'
            }
        };

        Plotly.newPlot('revenue-chart', [traceRevenue, traceExpenses, traceProfit], layout, {
            responsive: true,
            displayModeBar: false,
            scrollZoom: true
        });

        Plotly.newPlot('pdf-revenue-chart', [traceRevenue, traceExpenses, traceProfit], {
            ...layout,
            width: 1100,
            height: 400,
            margin: {l: 60, r: 60, t: 40, b: 50}
        }, {
            staticPlot: true
        });
    }

    function exportToPDF() {
        const now = new Date();
        const formattedDate = now.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        document.getElementById('pdf-date').textContent = formattedDate;
        document.getElementById('pdf-footer-date').textContent = formattedDate;

        document.getElementById('pdf-payback-period').textContent = document.getElementById('payback-period').textContent;
        document.getElementById('pdf-monthly-profit').textContent = document.getElementById('monthly-profit').textContent;
        document.getElementById('pdf-roi-display').textContent = document.getElementById('roi-display').textContent;

        const { jsPDF } = window.jspdf;
        const container = document.getElementById('pdf-export-container');

        container.style.display = 'block';

        html2canvas(container, {
            scale: 2,
            useCORS: true,
            logging: false,
            backgroundColor: '#ffffff'
        }).then(canvas => {
            container.style.display = 'none';

            // Создаем PDF
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });

            const imgProps = pdf.getImageProperties(imgData);
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save(`расчет_рентабельности_франшизы_${new Date().toISOString().split('T')[0]}.pdf`);

            document.getElementById('pdf-payback-chart').innerHTML = '';
            document.getElementById('pdf-revenue-chart').innerHTML = '';
        });
    }

    updateCalculations();
});