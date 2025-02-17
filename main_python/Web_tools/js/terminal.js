document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('input');
    const mainArea = document.getElementById('main-area');
    const tabArea = document.getElementById('tab-area');
    const newTabButton = document.getElementById('new-tab');
    let commandHistory = [];
    let historyIndex = -1;
    let currentTab = 0;
    let windowIndex = 0;
    let tabs = [];

    // Create a new tab
    function createTab() {
        const tab = document.createElement('button');
        tab.className = 'tab';
        tab.textContent = `Terminal ${tabs.length + 1}`;
        tab.addEventListener('click', () => switchTab(tabs.length));
        tabArea.insertBefore(tab, newTabButton);
        tabs.push(tab);
        switchTab(tabs.length - 1);
        return tab;
    }

    // Switch between tabs
    function switchTab(index) {
        tabs.forEach((tab, i) => {
            tab.classList.toggle('active', i === index);
        });
        currentTab = index;
    }

    // Add event listener for the new tab button
    newTabButton.addEventListener('click', createTab);

    // Handle input commands
    input.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const command = input.value.trim();
            if (command) {
                commandHistory.push(command);
                historyIndex = commandHistory.length;
                input.value = '';
                await sendCommand(command);
            }
        } else if (e.key === 'ArrowUp') {
            if (commandHistory.length > 0 && historyIndex > 0) {
                historyIndex--;
                input.value = commandHistory[historyIndex];
            }
        } else if (e.key === 'ArrowDown') {
            if (commandHistory.length > 0 && historyIndex < commandHistory.length - 1) {
                historyIndex++;
                input.value = commandHistory[historyIndex];
            } else {
                historyIndex = commandHistory.length;
                input.value = '';
            }
        }
    });

    // Send command to the backend
    async function sendCommand(command) {
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command }),
            });

            const data = await response.json();
            createWindow(command, data);
        } catch (error) {
            createWindow(command, { message: `Error: ${error.message}` });
        }
    }

    // Create a new window for command output
    function createWindow(command, data) {
        const window = document.createElement('div');
        window.className = 'window';
        window.style.top = `${50 + (windowIndex * 20)}px`;
        window.style.left = `${50 + (windowIndex * 20)}px`;
        windowIndex = (windowIndex + 1) % 10;

        const header = document.createElement('div');
        header.className = 'window-header';
        header.textContent = `Command: ${command}`;

        const closeButton = document.createElement('button');
        closeButton.className = 'close-button';
        closeButton.textContent = 'X';
        closeButton.addEventListener('click', () => window.remove());

        header.appendChild(closeButton);

        const content = document.createElement('div');
        content.className = 'window-content';

        if (data.message) {
            const p = document.createElement('pre');
            p.textContent = data.message;
            content.appendChild(p);
        }

        if (data.chart) {
            renderChart(content, data.chart);
        }

        if (data.news) {
            renderNews(content, data.news);
        }

        if (data.comparison) {
            renderComparison(content, data.comparison);
        }

        window.appendChild(header);
        window.appendChild(content);
        mainArea.appendChild(window);

        makeDraggable(window);
        makeResizable(window);
    }

    // Make windows draggable using interact.js
    function makeDraggable(element) {
        interact(element).draggable({
            listeners: {
                start(event) {
                    event.target.style.zIndex = 1000; // Bring to front
                },
                move(event) {
                    const target = event.target;
                    const x = (parseFloat(target.getAttribute('data-x'))) || 0;
                    const y = (parseFloat(target.getAttribute('data-y'))) || 0;

                    target.style.transform = `translate(${x + event.dx}px, ${y + event.dy}px)`;
                    target.setAttribute('data-x', x + event.dx);
                    target.setAttribute('data-y', y + event.dy);
                }
            }
        });
    }

    // Make windows resizable using interact.js
    function makeResizable(element) {
        interact(element).resizable({
            edges: { bottom: true, right: true },
            listeners: {
                move(event) {
                    const target = event.target;
                    let { x, y } = target.dataset;

                    x = (parseFloat(x) || 0) + event.deltaRect.left;
                    y = (parseFloat(y) || 0) + event.deltaRect.top;

                    Object.assign(target.style, {
                        width: `${event.rect.width}px`,
                        height: `${event.rect.height}px`,
                        transform: `translate(${x}px, ${y}px)`
                    });

                    Object.assign(target.dataset, { x, y });
                }
            }
        });
    }

    // Render a chart (placeholder)
    function renderChart(container, chartData) {
        const chartElement = document.createElement('div');
        chartElement.textContent = 'Chart placeholder';
        container.appendChild(chartElement);
    }

    // Render news (placeholder)
    function renderNews(container, newsData) {
        const newsElement = document.createElement('div');
        newsElement.textContent = 'News placeholder';
        container.appendChild(newsElement);
    }

    // Render comparison (placeholder)
    function renderComparison(container, comparisonData) {
        const comparisonElement = document.createElement('div');
        comparisonElement.textContent = 'Comparison placeholder';
        container.appendChild(comparisonElement);
    }

    // Initialize the first tab
    createTab();
});