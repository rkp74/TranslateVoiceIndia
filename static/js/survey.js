// Data for the survey results
const surveyData = {
    labels: ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi'],
    datasets: [{
        label: 'Preferred Language by State Students',
        data: [30, 20, 15, 10, 25], // Example data (replace with actual survey data)
        backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)'
        ],
        borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)'
        ],
        borderWidth: 1
    }]
};

// Draw the graph
window.onload = function() {
    var ctx = document.getElementById('languageChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: surveyData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
};
