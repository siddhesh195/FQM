function renderPieChart(canvasElement, dataObj) {
    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);

    return new Chart(canvasElement.getContext("2d"), {
        type: "pie",
        data: {
            labels: labels,
            datasets: [
                {
                    data: values
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}
