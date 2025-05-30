

class StockChart {
  constructor(containerId, ticker, initialData) {
    this.containerId = containerId;
    this.ticker = ticker;
    this.chartType = 'candlestick';
    this.timeframe = '1mo';
    this.data = this.processData(initialData);
    this.margin = {top: 20, right: 60, bottom: 30, left: 60};
    this.initChart();
  }

  processData(data) {
    if (!data || !Array.isArray(data)) return [];
    
    return data.map(item => {
      const date = item.Date || item.date;
      const open = Number(item.Open || item.open);
      const high = Number(item.High || item.high);
      const low = Number(item.Low || item.low);
      const close = Number(item.Close || item.close);
      const volume = Number(item.Volume || item.volume);

      return {
        date: date ? new Date(date) : null,
        open: isNaN(open) ? 0 : open,
        high: isNaN(high) ? 0 : high,
        low: isNaN(low) ? 0 : low,
        close: isNaN(close) ? 0 : close,
        volume: isNaN(volume) ? 0 : volume,
        day: date ? new Date(date).getDay() : null // 0=Sunday, 6=Saturday
      };
    }).filter(d => d.date !== null && d.day !== 0 && d.day !== 6); // Filter out weekends
  }

  initChart() {
    const container = document.getElementById(this.containerId);
    if (!container) {
      throw new Error(`Container element with ID '${this.containerId}' not found`);
    }
    
    container.innerHTML = this.getChartHTML();
    this.renderChart();
    this.addEventListeners();
  }

  getChartHTML() {
    const maxPrice = this.getMaxPrice();
    const minPrice = this.getMinPrice();
    const range = maxPrice - minPrice;
    const latestVolume = this.getLatestVolume();

    return `
      <div class="chart-header">
        <div class="chart-title">${this.ticker} - PRICE CHART</div>
        <div class="chart-controls">
          <select id="${this.containerId}-timeframe" class="timeframe-selector">
            <option value="1d">1D</option>
            <option value="5d">5D</option>
            <option value="1mo" selected>1M</option>
            <option value="3mo">3M</option>
            <option value="6mo">6M</option>
            <option value="1y">1Y</option>
            <option value="2y">2Y</option>
            <option value="5y">5Y</option>
            <option value="10y">10Y</option>
            <option value="ytd">YTD</option>
            <option value="max">MAX</option>
          </select>
          <div class="chart-type-buttons">
            <button data-type="candlestick" class="active">Candles</button>
            <button data-type="line">Line</button>
            <button data-type="ohlc">OHLC</button>
          </div>
        </div>
      </div>
      <div class="chart-container">
        <svg id="${this.containerId}-plot" width="100%" height="400"></svg>
      </div>
      <div class="chart-stats">
        <div class="stat-item">
          <span class="stat-label">HIGH:</span>
          <span class="stat-value positive">$${maxPrice.toFixed(2)}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">LOW:</span>
          <span class="stat-value negative">$${minPrice.toFixed(2)}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">RANGE:</span>
          <span class="stat-value">$${range.toFixed(2)}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">VOLUME:</span>
          <span class="stat-value">${latestVolume.toLocaleString()}</span>
        </div>
      </div>
    `;
  }

  addEventListeners() {
    // Chart type buttons
    document.querySelectorAll(`#${this.containerId} .chart-type-buttons button`).forEach(button => {
      button.addEventListener('click', () => {
        document.querySelectorAll(`#${this.containerId} .chart-type-buttons button`).forEach(btn => {
          btn.classList.remove('active');
        });
        button.classList.add('active');
        this.chartType = button.dataset.type;
        this.renderChart();
      });
    });

    // Timeframe selector
    document.getElementById(`${this.containerId}-timeframe`).addEventListener('change', async (e) => {
      this.timeframe = e.target.value;
      await this.updateData();
    });
  }

  async updateData() {
    try {
      const response = await fetch(`/api/chart/${this.ticker}?period=${this.timeframe}`);
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      const newData = await response.json();
      this.data = this.processData(newData.data);
      this.renderChart();
    } catch (error) {
      console.error("Error updating chart data:", error);
      // Show error message on chart
      const svg = d3.select(`#${this.containerId}-plot`);
      svg.selectAll("*").remove();
      svg.append("text")
        .attr("x", "50%")
        .attr("y", "50%")
        .attr("text-anchor", "middle")
        .attr("fill", "#ff9900")
        .text("Failed to load chart data");
    }
  }

  renderChart() {
    const svg = d3.select(`#${this.containerId}-plot`);
    svg.selectAll("*").remove();

    if (!this.data || this.data.length === 0) {
      svg.append("text")
        .attr("x", "50%")
        .attr("y", "50%")
        .attr("text-anchor", "middle")
        .attr("fill", "#ff9900")
        .text("No chart data available");
      return;
    }

    const containerWidth = svg.node().getBoundingClientRect().width;
    const containerHeight = 400;
    const width = containerWidth - this.margin.left - this.margin.right;
    const height = containerHeight - this.margin.top - this.margin.bottom;

    // Create chart group
    const g = svg.append("g")
      .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

    // Set scales
    const x = d3.scaleTime()
      .domain(d3.extent(this.data, d => d.date))
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([
        d3.min(this.data, d => d.low) * 0.99,
        d3.max(this.data, d => d.high) * 1.01
      ])
      .range([height, 0])
      .nice();

    // Add grid lines (lighter and thinner)
    g.append("g")
      .attr("class", "grid y-grid")
      .call(d3.axisLeft(y)
        .tickSize(-width)
        .tickFormat("")
        .tickSizeOuter(0));

    g.append("g")
      .attr("class", "grid x-grid")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x)
        .tickSize(-height)
        .tickFormat("")
        .tickSizeOuter(0));

    // Add axes
    const xAxis = g.append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x)
        .tickFormat(d3.timeFormat("%b %d"))
        .tickSizeOuter(0));

    const yAxis = g.append("g")
      .attr("class", "y-axis")
      .call(d3.axisRight(y).ticks(5))
      .attr("transform", `translate(${width},0)`);

    // Add current price line
    const currentPrice = this.data[this.data.length - 1].close;
    g.append("line")
      .attr("class", "current-price-line")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", y(currentPrice))
      .attr("y2", y(currentPrice))
      .attr("stroke", "#ff9900")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "3,3");

    // Draw chart based on type
    if (this.chartType === 'candlestick') {
      this.renderCandlestickChart(g, x, y, width);
    } else if (this.chartType === 'line') {
      this.renderLineChart(g, x, y);
    } else if (this.chartType === 'ohlc') {
      this.renderOHLCChart(g, x, y, width);
    }

    // Add crosshair
    this.addCrosshair(g, x, y, width, height);
  }

  renderCandlestickChart(g, x, y, width) {
    const barWidth = Math.max(1, width / this.data.length * 0.8);

    // Draw wicks first (so they're behind candles)
    g.selectAll(".wick")
      .data(this.data)
      .enter()
      .append("line")
      .attr("class", d => `wick ${d.close >= d.open ? 'up' : 'down'}`)
      .attr("x1", d => x(d.date))
      .attr("x2", d => x(d.date))
      .attr("y1", d => y(d.high))
      .attr("y2", d => y(d.low))
      .attr("stroke-width", 1);

    // Draw candles
    g.selectAll(".candle")
      .data(this.data)
      .enter()
      .append("rect")
      .attr("class", d => `candle ${d.close >= d.open ? 'up' : 'down'}`)
      .attr("x", d => x(d.date) - barWidth/2)
      .attr("y", d => y(Math.max(d.open, d.close)))
      .attr("width", barWidth)
      .attr("height", d => Math.abs(y(d.open) - y(d.close)) || 1)
      .attr("stroke-width", 1);
  }
  renderLineChart(g, x, y) {
    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.close))
      .curve(d3.curveMonotoneX);

    g.append("path")
      .datum(this.data)
      .attr("class", "line")
      .attr("fill", "none")
      .attr("stroke", "#ff9900")
      .attr("stroke-width", 2)
      .attr("d", line);
  }

  renderOHLCChart(g, x, y, width) {
    const barWidth = Math.max(1, width / this.data.length * 0.3);

    this.data.forEach(d => {
      // Open tick
      g.append("line")
        .attr("x1", x(d.date) - barWidth)
        .attr("x2", x(d.date))
        .attr("y1", y(d.open))
        .attr("y2", y(d.open))
        .attr("stroke", d.close >= d.open ? "#4CAF50" : "#F44336")
        .attr("stroke-width", 1);

      // Close tick
      g.append("line")
        .attr("x1", x(d.date))
        .attr("x2", x(d.date) + barWidth)
        .attr("y1", y(d.close))
        .attr("y2", y(d.close))
        .attr("stroke", d.close >= d.open ? "#4CAF50" : "#F44336")
        .attr("stroke-width", 1);

      // High-low line
      g.append("line")
        .attr("x1", x(d.date))
        .attr("x2", x(d.date))
        .attr("y1", y(d.high))
        .attr("y2", y(d.low))
        .attr("stroke", d.close >= d.open ? "#4CAF50" : "#F44336")
        .attr("stroke-width", 1);
    });
  }

  addCrosshair(g, x, y, width, height) {
    const focus = g.append("g")
      .attr("class", "focus")
      .style("display", "none");

    focus.append("line")
      .attr("class", "x-hair")
      .attr("y1", 0)
      .attr("y2", height);

    focus.append("line")
      .attr("class", "y-hair")
      .attr("x1", 0)
      .attr("x2", width);

    focus.append("circle")
      .attr("r", 4.5);

    focus.append("text")
      .attr("x", 9)
      .attr("dy", ".35em");

    g.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .style("fill", "none")
      .style("pointer-events", "all")
      .on("mouseover", () => focus.style("display", null))
      .on("mouseout", () => focus.style("display", "none"))
      .on("mousemove", (event) => {
        const bisectDate = d3.bisector(d => d.date).left;
        const x0 = x.invert(d3.pointer(event)[0]);
        const i = bisectDate(this.data, x0, 1);
        const d = this.data[i];

        focus.attr("transform", `translate(${x(d.date)},${y(d.close)})`);
        focus.select("text").text(`$${d.close.toFixed(2)}`);
        focus.select(".x-hair").attr("y2", height - y(d.close));
        focus.select(".y-hair").attr("x2", -x(d.date));
      });
  }

  getMaxPrice() {
    if (!this.data || this.data.length === 0) return 0;
    return d3.max(this.data, d => d.high);
  }

  getMinPrice() {
    if (!this.data || this.data.length === 0) return 0;
    return d3.min(this.data, d => d.low);
  }

  getLatestVolume() {
    if (!this.data || this.data.length === 0) return 0;
    return this.data[this.data.length - 1].volume;
  }
}

export default StockChart;