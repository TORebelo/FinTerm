// script.js
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('input');
    const output = document.getElementById('output');
    const chartContainer = document.getElementById('chart-container');
    const newsContainer = document.getElementById('news-container');

    // Focus on input when the page loads
    input.focus();

    // Handle Enter key press
    input.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter') {
            const command = input.value.trim();
            if (command) {
                appendOutput(`> ${command}`); // Display the command in the terminal
                input.value = ''; // Clear the input field
                await sendCommand(command); // Send the command to the backend
            }
        }
    });

    // Function to send a command to the backend
    async function sendCommand(command) {
        showLoading();
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command }),
            });

            const data = await response.json();

            if (data.message) {
                appendOutput(data.message);
            }

            if (data.chart) {
                renderChart(data.chart);
            }

            if (data.news) {
                renderNews(data.news);
            }

            if (data.comparison) {
                renderComparison(data.comparison);
            }
        } catch (error) {
            appendOutput(`Error: ${error.message}`);
        } finally {
            hideLoading();
        }
    }

    // Function to append output to the terminal
    function appendOutput(message) {
        const p = document.createElement('p');
        p.textContent = message;
        output.appendChild(p);
        output.scrollTop = output.scrollHeight; // Auto-scroll to the bottom
    }

    // Function to render a chart using Plotly
    function renderChart(chartData) {
        chartContainer.innerHTML = ''; // Clear previous chart
        Plotly.newPlot(chartContainer, chartData.data, chartData.layout);
    }

    // Function to render news articles
    function renderNews(news) {
        newsContainer.innerHTML = ''; // Clear previous news
        news.forEach(article => {
            const articleElement = document.createElement('div');
            articleElement.className = 'news-article';
            articleElement.innerHTML = `
                <h3>${article.title}</h3>
                <p>${article.description}</p>
                <a href="${article.url}" target="_blank">Read more</a>
            `;
            newsContainer.appendChild(articleElement);
        });
    }

    // Function to show loading indicator
    function showLoading() {
        const loading = document.createElement('div');
        loading.id = 'loading';
        loading.textContent = 'Loading...';
        output.appendChild(loading);
    }

    // Function to hide loading indicator
    function hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.remove();
        }
    }
});