document.addEventListener('DOMContentLoaded', function() {
    const chartBtn = document.getElementById('chartBtn');
    const tableBtn = document.getElementById('tableBtn');
    const chartContainer = document.getElementById('chartContainer');
    const tableContainer = document.getElementById('tableContainer');
    const generateChartBtn = document.getElementById('generateChart');

    let myChart = null;

    generateChartBtn.addEventListener('click', function() {
        const fileInput = document.getElementById('fileUpload');
        if (!fileInput.files.length) {
            alert('Please upload a CSV file.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            updateChart(data.dates, data.predicted_values);
            updateTable(data.dates, data.predicted_values);
        })
        .catch(error => console.error('Error:', error));
    });

    function updateChart(labels, values) {
        const ctx = document.getElementById('myChart').getContext('2d');

        if (myChart) {
            myChart.destroy();
        }

        myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Predicted Fuel Demand',
                    data: values,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: 'Time' } },
                    y: { title: { display: true, text: 'Fuel Demand' } }
                }
            }
        });

        chartContainer.classList.add('active');
        tableContainer.classList.remove('active');
    }

    function updateTable(labels, values) {
        const tableBody = document.getElementById('myTable').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';

        for (let i = 0; i < labels.length; i++) {
            const row = tableBody.insertRow();
            row.insertCell(0).innerText = labels[i];
            row.insertCell(1).innerText = values[i];
        }
    }

    chartBtn.addEventListener('click', function() {
        chartContainer.classList.add('active');
        tableContainer.classList.remove('active');
    });

    tableBtn.addEventListener('click', function() {
        tableContainer.classList.add('active');
        chartContainer.classList.remove('active');
    });

    chartContainer.classList.add('active');
});
