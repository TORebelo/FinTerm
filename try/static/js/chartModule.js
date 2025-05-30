// d3 is loaded via script tag in HTML
// Check if d3 is available globally
if (typeof d3 === "undefined") {
  console.error("d3 is not available. Make sure d3 is loaded via script tag.")
}

class StockChart {
  constructor(containerId, ticker, initialData) {
    this.containerId = containerId
    this.ticker = ticker
    this.chartType = "candlestick"
    this.timeframe = "1mo"
    this.data = this.processData(initialData)
    this.margin = { top: 20, right: 60, bottom: 30, left: 60 }
    this.initChart()

    // Add cleanup method to prevent memory leaks
    this.setupCleanup()
  }

  setupCleanup() {
    // Create a MutationObserver to detect when the chart container is removed
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.removedNodes.forEach((node) => {
          if (node.contains && node.contains(document.getElementById(this.containerId))) {
            console.log(`Chart container ${this.containerId} removed, cleaning up intervals`)
            if (this.updateInterval) {
              clearInterval(this.updateInterval)
            }
            observer.disconnect()
          }
        })
      })
    })

    // Start observing the document body for removed nodes
    observer.observe(document.body, { childList: true, subtree: true })
  }

  processData(data) {
    if (!data || !Array.isArray(data)) return []

    // Process and filter out weekends, but maintain trading day sequence
    const processed = data
      .map((item) => {
        const date = new Date(item.Date || item.date)
        return {
          ...item,
          date,
          dateValue: +date,
          day: date.getDay(),
          open: Number(item.Open || item.open),
          high: Number(item.High || item.high),
          low: Number(item.Low || item.low),
          close: Number(item.Close || item.close),
          volume: Number(item.Volume || item.volume),
        }
      })
      .filter((d) => ![0, 6].includes(d.day) && !isNaN(d.close)) // Remove weekends and invalid data

    // Sort by date to ensure proper order
    return processed.sort((a, b) => a.dateValue - b.dateValue)
  }

  initChart() {
    const container = document.getElementById(this.containerId)
    if (!container) {
      throw new Error(`Container element with ID '${this.containerId}' not found`)
    }

    container.innerHTML = this.getChartHTML()
    this.renderChart()
    this.addEventListeners()

    // Add real-time updates
    this.startRealtimeUpdates()
  }

  getChartHTML() {
    const maxPrice = this.getMaxPrice()
    const minPrice = this.getMinPrice()
    const range = maxPrice - minPrice
    const latestVolume = this.getLatestVolume()

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
    `
  }

  addEventListeners() {
    // Chart type buttons
    document.querySelectorAll(`#${this.containerId} .chart-type-buttons button`).forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll(`#${this.containerId} .chart-type-buttons button`).forEach((btn) => {
          btn.classList.remove("active")
        })
        button.classList.add("active")
        this.chartType = button.dataset.type
        this.renderChart()
      })
    })

    // Timeframe selector
    document.getElementById(`${this.containerId}-timeframe`).addEventListener("change", async (e) => {
      this.timeframe = e.target.value
      await this.updateData()
    })
  }

  // Fixed data updating function
  async updateData() {
    try {
      console.log(`Updating chart data for ${this.ticker} with period ${this.timeframe}`)
      const response = await fetch(`/api/chart/${this.ticker}?period=${this.timeframe}`)
      if (!response.ok) {
        throw new Error(`API returned ${response.status}: ${response.statusText}`)
      }
      const result = await response.json()
      const newData = result.data || result

      if (!newData || newData.length === 0) {
        throw new Error("No data received from API")
      }

      this.data = this.processData(newData)
      this.renderChart()
      this.updateStats()
    } catch (error) {
      console.error("Error updating chart data:", error)
      const svg = d3.select(`#${this.containerId}-plot`)
      svg.selectAll("*").remove()
      svg
        .append("text")
        .attr("x", "50%")
        .attr("y", "50%")
        .attr("text-anchor", "middle")
        .attr("fill", "#ff9900")
        .text(`Error loading data: ${error.message}`)
    }
  }

  startRealtimeUpdates() {
    // Update every 2 seconds for more responsive real-time data
    this.updateInterval = setInterval(async () => {
      console.log(`Auto-updating chart data for ${this.ticker}`)

      // Add visual indicator that chart is updating
      const container = document.getElementById(this.containerId)
      if (container) {
        const title = container.querySelector(".chart-title")
        if (title) {
          const originalText = title.textContent
          title.textContent = `${originalText} (Updating...)`

          // Update the data
          await this.updateData()

          // Remove updating indicator
          setTimeout(() => {
            if (title) {
              title.textContent = originalText
            }
          }, 500)
        }
      }
    }, 2000) // 2 seconds for more frequent updates

    // Store the interval ID in the container element for cleanup
    const container = document.getElementById(this.containerId)
    if (container) {
      container.dataset.chartUpdateInterval = this.updateInterval
    }
  }

  updateStats() {
    const container = document.getElementById(this.containerId)
    if (!container) return

    const maxPrice = this.getMaxPrice()
    const minPrice = this.getMinPrice()
    const range = maxPrice - minPrice
    const latestVolume = this.getLatestVolume()

    const statsContainer = container.querySelector(".chart-stats")
    if (statsContainer) {
      statsContainer.innerHTML = `
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
      `
    }
  }

  renderChart() {
    const svg = d3.select(`#${this.containerId}-plot`)
    svg.selectAll("*").remove()

    if (!this.data || this.data.length === 0) {
      svg
        .append("text")
        .attr("x", "50%")
        .attr("y", "50%")
        .attr("text-anchor", "middle")
        .attr("fill", "#ff9900")
        .text("No chart data available")
      return
    }

    const containerWidth = svg.node().getBoundingClientRect().width
    const containerHeight = 400
    const width = containerWidth - this.margin.left - this.margin.right
    const height = containerHeight - this.margin.top - this.margin.bottom

    // Create chart group
    const g = svg.append("g").attr("transform", `translate(${this.margin.left},${this.margin.top})`)

    // Use ordinal scale for x-axis to remove gaps between non-trading days
    const x = d3
      .scaleBand()
      .domain(this.data.map((d, i) => i))
      .range([0, width])
      .padding(0.1)

    const y = d3
      .scaleLinear()
      .domain([d3.min(this.data, (d) => d.low) * 0.99, d3.max(this.data, (d) => d.high) * 1.01])
      .range([height, 0])
      .nice()

    // Add grid lines
    g.append("g").attr("class", "grid y-grid").call(d3.axisLeft(y).tickSize(-width).tickFormat("").tickSizeOuter(0))

    // Add axes with better date formatting
    const xAxis = g
      .append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(0,${height})`)
      .call(
        d3
          .axisBottom(x)
          .tickFormat((d, i) => {
            const date = this.data[i]?.date
            if (!date) return ""
            return d3.timeFormat("%m/%d")(date)
          })
          .tickValues(x.domain().filter((d, i) => i % Math.ceil(this.data.length / 8) === 0)),
      )

    const yAxis = g
      .append("g")
      .attr("class", "y-axis")
      .call(d3.axisRight(y).ticks(5))
      .attr("transform", `translate(${width},0)`)

    // Add current price line
    if (this.data.length > 0) {
      const currentPrice = this.data[this.data.length - 1].close
      g.append("line")
        .attr("class", "current-price-line")
        .attr("x1", 0)
        .attr("x2", width)
        .attr("y1", y(currentPrice))
        .attr("y2", y(currentPrice))
        .attr("stroke", "#ff9900")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "3,3")
    }

    // Draw chart based on type
    if (this.chartType === "candlestick") {
      this.renderCandlestickChart(g, x, y, width)
    } else if (this.chartType === "line") {
      this.renderLineChart(g, x, y)
    } else if (this.chartType === "ohlc") {
      this.renderOHLCChart(g, x, y, width)
    }

    // Add crosshair
    this.addCrosshair(g, x, y, width, height)
  }

  renderCandlestickChart(g, x, y, width) {
    const barWidth = x.bandwidth()

    // Draw wicks first
    g.selectAll(".wick")
      .data(this.data)
      .enter()
      .append("line")
      .attr("class", (d) => `wick ${d.close >= d.open ? "up" : "down"}`)
      .attr("x1", (d, i) => x(i) + barWidth / 2)
      .attr("x2", (d, i) => x(i) + barWidth / 2)
      .attr("y1", (d) => y(d.high))
      .attr("y2", (d) => y(d.low))
      .attr("stroke-width", 1)

    // Draw candles
    g.selectAll(".candle")
      .data(this.data)
      .enter()
      .append("rect")
      .attr("class", (d) => `candle ${d.close >= d.open ? "up" : "down"}`)
      .attr("x", (d, i) => x(i))
      .attr("y", (d) => y(Math.max(d.open, d.close)))
      .attr("width", barWidth)
      .attr("height", (d) => Math.abs(y(d.open) - y(d.close)) || 1)
      .attr("stroke-width", 1)
  }

  renderLineChart(g, x, y) {
    const line = d3
      .line()
      .x((d, i) => x(i) + x.bandwidth() / 2)
      .y((d) => y(d.close))
      .curve(d3.curveMonotoneX)

    g.append("path")
      .datum(this.data)
      .attr("class", "line")
      .attr("fill", "none")
      .attr("stroke", "#ff9900")
      .attr("stroke-width", 2)
      .attr("d", line)
  }

  renderOHLCChart(g, x, y, width) {
    const barWidth = x.bandwidth() * 0.3

    this.data.forEach((d, i) => {
      const xPos = x(i) + x.bandwidth() / 2

      // Open tick
      g.append("line")
        .attr("x1", xPos - barWidth)
        .attr("x2", xPos)
        .attr("y1", y(d.open))
        .attr("y2", y(d.open))
        .attr("stroke", d.close >= d.open ? "#4CAF50" : "#F44336")
        .attr("stroke-width", 1)

      // Close tick
      g.append("line")
        .attr("x1", xPos)
        .attr("x2", xPos + barWidth)
        .attr("y1", y(d.close))
        .attr("y2", y(d.close))
        .attr("stroke", d.close >= d.open ? "#4CAF50" : "#F44336")
        .attr("stroke-width", 1)

      // High-low line
      g.append("line")
        .attr("x1", xPos)
        .attr("x2", xPos)
        .attr("y1", y(d.high))
        .attr("y2", y(d.low))
        .attr("stroke", d.close >= d.open ? "#4CAF50" : "#F44336")
        .attr("stroke-width", 1)
    })
  }

  addCrosshair(g, x, y, width, height) {
    const focus = g.append("g").attr("class", "focus").style("display", "none")

    focus.append("line").attr("class", "x-hair").attr("y1", 0).attr("y2", height)

    focus.append("line").attr("class", "y-hair").attr("x1", 0).attr("x2", width)

    focus.append("circle").attr("r", 4.5)

    focus.append("text").attr("x", 9).attr("dy", ".35em")

    g.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .style("fill", "none")
      .style("pointer-events", "all")
      .on("mouseover", () => focus.style("display", null))
      .on("mouseout", () => focus.style("display", "none"))
      .on("mousemove", (event) => {
        const [mouseX] = d3.pointer(event)
        const index = Math.round(mouseX / x.bandwidth())
        const d = this.data[index]

        if (d) {
          const xPos = x(index) + x.bandwidth() / 2
          focus.attr("transform", `translate(${xPos},${y(d.close)})`)
          focus.select("text").text(`$${d.close.toFixed(2)}`)
          focus.select(".x-hair").attr("y2", height - y(d.close))
          focus.select(".y-hair").attr("x2", -xPos)
        }
      })
  }

  getMaxPrice() {
    if (!this.data || this.data.length === 0) return 0
    return d3.max(this.data, (d) => d.high)
  }

  getMinPrice() {
    if (!this.data || this.data.length === 0) return 0
    return d3.min(this.data, (d) => d.low)
  }

  getLatestVolume() {
    if (!this.data || this.data.length === 0) return 0
    return this.data[this.data.length - 1].volume
  }
}

export default StockChart
