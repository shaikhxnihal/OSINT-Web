const form = document.getElementById("analyzeForm");
const resultDiv = document.getElementById("result");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const domain = document.getElementById("domain").value;

    resultDiv.innerHTML = "<p>Analyzing... Please wait.</p>";

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ domain }),
        });

        if (!response.ok) {
            throw new Error("Failed to analyze the domain.");
        }

        const data = await response.json();
        displayResult(data);
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">${error.message}</p>`;
    }
});

let myChart = null; // Global variable to store the chart instance

function displayResult(data) {
    if (data.error) {
        resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
    }

    const report = data.report;
    const ratings = data.ratings;

    // Format and display the report as a structured HTML
    resultDiv.innerHTML = `
        <h3>Analysis Report</h3>
        <div class="report-section">
            <h4>Domain Info:</h4>
            <p><strong>Domain:</strong> ${report.domain || "N/A"}</p>
            <p><strong>IP Address:</strong> ${report.ip || "N/A"}</p>
        </div>
        <div class="report-section">
            <h4>SEO Overview:</h4>
            <p><strong>Title:</strong> ${report.meta_tags && report.meta_tags.title ? report.meta_tags.title : "N/A"}</p>
            <p><strong>Keywords:</strong> ${report.meta_tags && report.meta_tags.keywords ? report.meta_tags.keywords : "N/A"}</p>
        </div>
        <div class="report-section">
            <h4>Security Overview:</h4>
            <p><strong>SSL Certificate:</strong> ${report.ssl_status ? "Valid" : "Invalid"}</p>
            <p><strong>SSL Score:</strong> ${report.ssl_score || "N/A"}</p>
        </div>
        <div class="report-section">
            <h4>Readability:</h4>
            <p><strong>Readability Score:</strong> ${report.readability ? report.readability.score : "N/A"}</p>
        </div>
        <div class="report-section">
            <h4>Visibility:</h4>
            <p><strong>Google Rank Position:</strong> ${report.google_rank ? report.google_rank.position : "N/A"}</p>
        </div>
    `;

    // Render the chart with ratings
    renderChart(ratings);
}

function renderChart(ratings) {
    const ctx = document.getElementById("ratingsChart").getContext("2d");

    // If a chart already exists, destroy it
    if (myChart) {
        myChart.destroy();
    }

    const chartData = {
        labels: ["Security", "SEO", "Readability", "Visibility"],
        datasets: [
            {
                label: "Website Ratings (0-10)",
                data: [
                    ratings.security,
                    ratings.seo,
                    ratings.readability,
                    ratings.visibility,
                ],
                backgroundColor: "rgba(54, 162, 235, 0.2)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1,
            },
        ],
    };

    const chartOptions = {
        scales: {
            r: {
                suggestedMin: 0,
                suggestedMax: 10,
            },
        },
    };

    // Create a new chart
    myChart = new Chart(ctx, {
        type: "radar",
        data: chartData,
        options: chartOptions,
    });
}

