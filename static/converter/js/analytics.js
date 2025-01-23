document.addEventListener('DOMContentLoaded', function () {
    const totalUsers = JSON.parse(document.getElementById('totalUsers').textContent);
    const totalPdfs = JSON.parse(document.getElementById('totalPdfs').textContent);
    const totalTranslatedPdfs = JSON.parse(document.getElementById('totalTranslatedPdfs').textContent);
    const totalSummarizedPdfs = JSON.parse(document.getElementById('totalSummarizedPdfs').textContent);

    const ctx = document.getElementById('analyticsChart').getContext('2d');
    const analyticsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Users', 'PDFs', 'Translated PDFs', 'Summarized PDFs'],
            datasets: [{
                label: 'Count',
                data: [totalUsers, totalPdfs, totalTranslatedPdfs, totalSummarizedPdfs],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(153, 102, 255, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
