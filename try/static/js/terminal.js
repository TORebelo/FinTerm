import StockChart from "./chartModule.js"

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("input")
  const mainArea = document.getElementById("main-area")
  const windowCount = document.getElementById("window-count")
  const clock = document.getElementById("clock")

  const commandHistory = []
  let historyIndex = -1
  let windowIndex = 0
  let windows = []
  let activeWindow = null

  // Update clock
  function updateClock() {
    clock.textContent = new Date().toLocaleTimeString()
  }
  setInterval(updateClock, 1000)
  updateClock()

  // Update window count
  function updateWindowCount() {
    windowCount.textContent = `${windows.length} windows`
  }

  // Window management functions
  function bringToFront(window) {
    console.log("Bringing window to front:", window.querySelector(".window-header").textContent)

    const maxZIndex = Math.max(...windows.map((w) => Number.parseInt(w.style.zIndex) || 0))
    window.style.zIndex = maxZIndex + 1
    activeWindow = window

    // Update window selection visual indicator
    windows.forEach((w) => w.classList.remove("active-window"))
    window.classList.add("active-window")

    console.log("Active window set to:", activeWindow.querySelector(".window-header").textContent)
  }

  // Add keyboard shortcuts for window management (Windows-style)
  document.addEventListener("keydown", (e) => {
    // Log key presses for debugging
    console.log("Key pressed:", e.key, "Ctrl:", e.ctrlKey, "Alt:", e.altKey, "Shift:", e.shiftKey)

    // Windows-style window management
    if (e.ctrlKey && e.key === "ArrowLeft") {
      e.preventDefault()
      console.log("Ctrl+Left detected, organizing windows left")
      organizeWindows("left")
    } else if (e.ctrlKey && e.key === "ArrowRight") {
      e.preventDefault()
      console.log("Ctrl+Right detected, organizing windows right")
      organizeWindows("right")
    } else if (e.ctrlKey && e.key === "ArrowUp") {
      e.preventDefault()
      console.log("Ctrl+Up detected, maximizing window")
      if (activeWindow) {
        // Maximize window
        const savedSize =
          activeWindow.dataset.savedSize ||
          JSON.stringify({
            width: activeWindow.style.width,
            height: activeWindow.style.height,
            left: activeWindow.style.left,
            top: activeWindow.style.top,
          })

        activeWindow.dataset.savedSize = savedSize
        activeWindow.style.width = "90%"
        activeWindow.style.height = "80%"
        activeWindow.style.left = "5%"
        activeWindow.style.top = "10%"
      }
    } else if (e.ctrlKey && e.key === "ArrowDown") {
      e.preventDefault()
      console.log("Ctrl+Down detected, restoring window")
      if (activeWindow && activeWindow.dataset.savedSize) {
        // Restore window
        const savedSize = JSON.parse(activeWindow.dataset.savedSize)
        activeWindow.style.width = savedSize.width
        activeWindow.style.height = savedSize.height
        activeWindow.style.left = savedSize.left
        activeWindow.style.top = savedSize.top
      }
    }
  })

  input.addEventListener("keydown", async (e) => {
    if (e.key === "Enter") {
      const command = input.value.trim()
      if (command) {
        commandHistory.push(command)
        historyIndex = commandHistory.length
        input.value = ""
        await sendCommand(command)
      }
    } else if (e.key === "ArrowUp") {
      if (commandHistory.length > 0 && historyIndex > 0) {
        historyIndex--
        input.value = commandHistory[historyIndex]
      }
    } else if (e.key === "ArrowDown") {
      if (commandHistory.length > 0 && historyIndex < commandHistory.length - 1) {
        historyIndex++
        input.value = commandHistory[historyIndex]
      } else {
        historyIndex = commandHistory.length
        input.value = ""
      }
    }
  })

  async function sendCommand(command) {
    if (command.toLowerCase() === "clear" || command.toLowerCase() === "kill") {
      clearAllWindows()
      return
    }

    const parts = command.toLowerCase().split(" ")
    const action = parts[0]

    try {
      let data = {}
      let title = ""

      switch (action) {
        case "help":
          title = "Help"
          data.message = `
STOCK TERMINAL v2.0 - COMMAND REFERENCE
=====================================

COMMANDS:
  help                           - Show this help
  view <ticker>                  - View stock information
  quote <ticker>                 - Get quick stock quote
  price <ticker>                 - Live price updates (every second)
  chart <ticker> [period]        - Show stock chart (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)
  portfolio                      - Display portfolio
  add <ticker> <shares> <price>  - Add stock to portfolio
  news                           - Market news
  sec <ticker>                   - SEC filings
  clear                          - Clear all windows

WINDOW MANAGEMENT:
  Ctrl + Left Arrow              - Move active window left
  Ctrl + Right Arrow             - Move active window right
  Click window header            - Bring window to front

EXAMPLES:
  view AAPL
  quote MSFT
  price TSLA
  chart TSLA 1y
  add GOOGL 10 2800
  portfolio
          `
          break

        case "view":
          if (parts[1]) {
            const ticker = parts[1].toUpperCase()
            title = `${ticker} - Stock Information`
            try {
              const response = await fetch(`/api/stock/${ticker}`)
              if (!response.ok) {
                throw new Error(`API returned ${response.status}`)
              }
              data = await response.json()
            } catch (error) {
              data = getMockStockInfo(ticker)
            }
          } else {
            title = "Error"
            data.message = "Usage: view <ticker>"
          }
          break

        case "quote":
          if (parts[1]) {
            const ticker = parts[1].toUpperCase()
            title = `${ticker} - Quote`
            try {
              const response = await fetch(`/api/quote/${ticker}`)
              if (!response.ok) {
                throw new Error(`API returned ${response.status}`)
              }
              data = await response.json()
            } catch (error) {
              console.error("Quote API error:", error)
              data.message = `Error fetching quote: ${error.message}`
            }
          } else {
            title = "Error"
            data.message = "Usage: quote <ticker>"
          }
          break

        case "price":
          if (parts[1]) {
            const ticker = parts[1].toUpperCase()
            title = `${ticker} - Live Price`
            data.ticker = ticker
            data.isLivePrice = true
          } else {
            title = "Error"
            data.message = "Usage: price <ticker>"
          }
          break

        case "chart":
          if (parts[1]) {
            const ticker = parts[1].toUpperCase()
            const period = parts[2] || "1mo"
            title = `${ticker} - Chart`
            try {
              const response = await fetch(`/api/chart/${ticker}?period=${period}`)
              if (!response.ok) {
                throw new Error(`API returned ${response.status}`)
              }
              data = await response.json()
              data.ticker = ticker
            } catch (error) {
              data = { data: getMockChartData(ticker), ticker: ticker }
            }
          } else {
            title = "Error"
            data.message = "Usage: chart <ticker> [period]"
          }
          break

        case "portfolio":
          title = "Portfolio"
          try {
            const response = await fetch("/api/portfolio")
            if (!response.ok) {
              throw new Error(`API returned ${response.status}`)
            }
            data = await response.json()
          } catch (error) {
            data = getMockPortfolio()
          }
          break

        case "add":
          if (parts.length >= 4) {
            const ticker = parts[1].toUpperCase()
            const shares = Number(parts[2])
            const price = Number(parts[3])

            title = "Add Stock"
            try {
              console.log(`Attempting to add stock: ${ticker}, ${shares} shares at $${price}`)

              // Use query parameters as the API expects
              const url = `/api/portfolio?symbol=${encodeURIComponent(ticker)}&shares=${shares}&price=${price}`
              console.log("Trying URL:", url)

              let response = await fetch(url, {
                method: "POST",
                headers: {
                  Accept: "application/json",
                },
              })

              // If that fails, try the add endpoint
              if (!response.ok) {
                const addUrl = `/api/portfolio/add?symbol=${encodeURIComponent(ticker)}&shares=${shares}&price=${price}`
                console.log("Main endpoint failed, trying add endpoint:", addUrl)
                response = await fetch(addUrl, {
                  method: "POST",
                  headers: {
                    Accept: "application/json",
                  },
                })
              }

              if (!response.ok) {
                const errorText = await response.text()
                console.error("API Error Response:", errorText)

                let errorMessage
                try {
                  const errorData = JSON.parse(errorText)
                  if (errorData.detail) {
                    if (Array.isArray(errorData.detail)) {
                      errorMessage = errorData.detail
                        .map((err) => err.msg || err.message || JSON.stringify(err))
                        .join(", ")
                    } else {
                      errorMessage = errorData.detail
                    }
                  } else if (errorData.message) {
                    errorMessage = errorData.message
                  } else {
                    errorMessage = errorText
                  }
                } catch {
                  errorMessage = `HTTP ${response.status}: ${errorText}`
                }
                throw new Error(errorMessage)
              }

              const result = await response.json()
              console.log("Success response:", result)
              data.message = `Successfully added ${shares} shares of ${ticker} at $${price}`
              createNotification(`Added ${shares} shares of ${ticker} at $${price}`)
            } catch (error) {
              console.error("Full error details:", error)

              let errorMessage = "Unknown error occurred"

              if (error instanceof TypeError && error.message.includes("fetch")) {
                errorMessage = "Network error - unable to connect to API"
              } else if (error.message) {
                errorMessage = error.message
              } else if (typeof error === "string") {
                errorMessage = error
              } else {
                errorMessage = "Failed to add stock - check console for details"
              }

              data.message = `Error adding stock: ${errorMessage}`
            }
          } else {
            title = "Error"
            data.message = "Usage: add <ticker> <shares> <price>"
          }
          break

        case "news":
          title = "Market News"
          try {
            const newsResponse = await fetch("/api/news")
            if (!newsResponse.ok) {
              throw new Error(`API returned ${newsResponse.status}`)
            }
            data = await newsResponse.json()
          } catch (error) {
            data = { articles: getMockNews() }
          }
          break

        case "sec":
          if (parts[1]) {
            const ticker = parts[1].toUpperCase()
            title = `${ticker} - SEC Filings`
            try {
              const response = await fetch(`/api/sec/${ticker}`)
              if (!response.ok) {
                throw new Error(`API returned ${response.status}`)
              }
              data = await response.json()
            } catch (error) {
              data = { filings: getMockSECFilings(ticker) }
            }
          } else {
            title = "Error"
            data.message = "Usage: sec <ticker>"
          }
          break

        default:
          title = "Error"
          data.message = `Unknown command: ${action}. Type 'help' for available commands.`
      }

      createWindow(title, data, action)
    } catch (error) {
      createWindow("Error", { message: `Error: ${error.message}` }, "error")
    }
  }

  function createWindow(title, data, type) {
    // Calculate initial size based on content type
    let width = 600
    let height = 500

    switch (type) {
      case "quote":
        width = 400
        height = 250
        break
      case "price":
        width = 350
        height = 150
        break
      case "view":
        width = 700
        height = 600
        break
      case "chart":
        width = 800
        height = 550
        break
      case "portfolio":
        width = 750
        height = Math.min(600, 100 + (data.holdings?.length || 0) * 30)
        break
      case "news":
        width = 650
        height = Math.min(700, 150 + (data.articles?.length || 0) * 120)
        break
      case "sec":
        width = 650
        height = Math.min(500, 100 + (data.filings?.length || 0) * 30)
        break
    }

    const window = document.createElement("div")
    window.className = "window"
    window.style.top = `${50 + windowIndex * 30}px`
    window.style.left = `${100 + windowIndex * 30}px`
    window.style.width = `${width}px`
    window.style.height = `${height}px`
    window.style.zIndex = 1000 + windowIndex
    windowIndex = (windowIndex + 1) % 10

    const header = document.createElement("div")
    header.className = "window-header"
    header.textContent = title

    // Add click handler to bring window to front
    header.addEventListener("click", (e) => {
      console.log("Header clicked for window:", title)
      if (!e.target.classList.contains("close-button")) {
        e.preventDefault()
        e.stopPropagation()
        bringToFront(window)
      }
    })

    const closeButton = document.createElement("button")
    closeButton.className = "close-button"
    closeButton.textContent = "X"
    closeButton.addEventListener("click", () => {
      // Clean up any intervals
      if (window.dataset.intervalId) {
        clearInterval(Number(window.dataset.intervalId))
      }
      window.remove()
      windows = windows.filter((w) => w !== window)
      updateWindowCount()

      // Update active window
      if (activeWindow === window) {
        activeWindow = windows.length > 0 ? windows[windows.length - 1] : null
        if (activeWindow) {
          bringToFront(activeWindow)
        }
      }
    })

    header.appendChild(closeButton)

    const content = document.createElement("div")
    content.className = "window-content"

    if (data.message) {
      const pre = document.createElement("pre")
      pre.textContent = data.message
      content.appendChild(pre)
    }

    if (type === "quote" && data.symbol) {
      content.innerHTML = renderQuote(data)
    } else if (type === "view" && data.symbol) {
      content.innerHTML = renderStockInfo(data)
    } else if (type === "price" && data.isLivePrice) {
      content.innerHTML = renderLivePrice(data.ticker)
      startLivePriceUpdates(content, data.ticker, window)
    } else if (type === "chart" && data.data) {
      const chartId = `chart-${Date.now()}`
      content.innerHTML = `<div id="${chartId}" style="width:100%; height:400px;"></div>`

      setTimeout(() => {
        try {
          new StockChart(chartId, data.ticker, data.data)
        } catch (error) {
          console.error("Error initializing chart:", error)
          content.innerHTML = `<div>Error loading chart: ${error.message}</div>`
        }
      }, 0)
    } else if (type === "portfolio" && (data.holdings || data.stocks)) {
      content.innerHTML = renderPortfolio(data)
    } else if (type === "news" && data.articles) {
      content.innerHTML = renderNews(data.articles)
    } else if (type === "sec" && data.filings) {
      content.innerHTML = renderSECFilings(data.filings)
    }

    window.appendChild(header)
    window.appendChild(content)
    mainArea.appendChild(window)

    makeDraggable(window)
    makeResizable(window)

    windows.push(window)
    bringToFront(window)
    updateWindowCount()
  }

  function renderLivePrice(ticker) {
    return `
      <div class="live-price-container">
        <div class="live-price-ticker">${ticker}</div>
        <div class="live-price-display" id="live-price-${ticker}">
          <div class="loading">Loading...</div>
        </div>
        <div class="live-price-status">Updates every second</div>
      </div>
    `
  }

  function startLivePriceUpdates(content, ticker, window) {
    const updatePrice = async () => {
      try {
        console.log(`Fetching live price for ${ticker}`)
        const response = await fetch(`/api/quote/${ticker}`)

        if (!response.ok) {
          const errorText = await response.text()
          console.error(`API Error ${response.status}:`, errorText)

          // Handle 404 specifically
          if (response.status === 404) {
            throw new Error(`Quote not found for ${ticker}`)
          } else {
            throw new Error(`API returned ${response.status}: ${errorText}`)
          }
        }

        const quote = await response.json()

        const priceDisplay = content.querySelector(`#live-price-${ticker}`)
        if (priceDisplay) {
          const changeClass = quote.change >= 0 ? "positive" : "negative"
          const arrow = quote.change >= 0 ? "▲" : "▼"

          priceDisplay.innerHTML = `
          <div class="live-price ${changeClass}">
            $${quote.price.toFixed(2)} 
            <span class="live-change">${arrow} ${Math.abs(quote.changePercent).toFixed(2)}%</span>
          </div>
        `
        }
      } catch (error) {
        console.error("Error updating live price:", error)

        const priceDisplay = content.querySelector(`#live-price-${ticker}`)
        if (priceDisplay) {
          if (error.message.includes("Quote not found")) {
            priceDisplay.innerHTML = `<div class="error">Quote not available for ${ticker}</div>`
          } else {
            priceDisplay.innerHTML = `<div class="error">API Error: ${error.message}</div>`
          }
        }
      }
    }

    // Initial update
    updatePrice()

    // Set up interval for updates every 5 seconds (reduced frequency due to API issues)
    const intervalId = setInterval(updatePrice, 5000)
    window.dataset.intervalId = intervalId
  }

  function createNotification(message) {
    const notification = document.createElement("div")
    notification.className = "window notification"
    notification.style.top = `${50 + windowIndex * 30}px`
    notification.style.left = `${100 + windowIndex * 30}px`
    notification.style.width = "300px"
    notification.style.height = "auto"
    notification.style.zIndex = 2000
    windowIndex = (windowIndex + 1) % 10

    const header = document.createElement("div")
    header.className = "window-header"
    header.textContent = "Notification"

    const closeButton = document.createElement("button")
    closeButton.className = "close-button"
    closeButton.textContent = "X"
    closeButton.addEventListener("click", () => {
      notification.remove()
    })

    header.appendChild(closeButton)

    const content = document.createElement("div")
    content.className = "window-content"
    content.style.padding = "15px"
    content.innerHTML = `<div class="positive">${message}</div>`

    notification.appendChild(header)
    notification.appendChild(content)
    mainArea.appendChild(notification)

    makeDraggable(notification)

    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove()
      }
    }, 3000)
  }

  function renderQuote(data) {
    const changeClass = data.change >= 0 ? "positive" : "negative"
    return `
      <div style="font-size: 14px;">
          <div style="color: #ff9900; font-weight: bold; margin-bottom: 10px;">${data.symbol} - QUOTE</div>
          <table class="data-table">
              <tr><td>PRICE:</td><td class="positive">$${data.price.toFixed(2)}</td></tr>
              <tr><td>CHANGE:</td><td class="${changeClass}">${data.change >= 0 ? "+" : ""}${data.change.toFixed(2)} (${data.changePercent.toFixed(2)}%)</td></tr>
              <tr><td>VOLUME:</td><td>${data.volume.toLocaleString()}</td></tr>
              <tr><td>PREV CLOSE:</td><td>$${data.previousClose.toFixed(2)}</td></tr>
          </table>
      </div>
    `
  }

  function renderStockInfo(data) {
    const changeClass = data.change >= 0 ? "positive" : "negative"
    return `
      <div style="font-size: 12px;">
          <div style="color: #ff9900; font-weight: bold; margin-bottom: 10px;">${data.symbol} - ${data.name}</div>
          <div style="font-size: 18px; margin-bottom: 10px;">
              <span class="positive">$${data.price.toFixed(2)}</span>
              <span class="${changeClass}" style="margin-left: 10px;">${data.change >= 0 ? "▲" : "▼"} ${Math.abs(data.changePercent).toFixed(2)}%</span>
          </div>
          
          <div style="color: #ff9900; font-weight: bold; margin: 15px 0 5px 0;">MARKET DATA</div>
          <table class="data-table">
              <tr><td>MARKET CAP:</td><td>$${(data.marketCap / 1e9).toFixed(2)}B</td></tr>
              <tr><td>P/E RATIO:</td><td>${data.peRatio.toFixed(2)}</td></tr>
              <tr><td>EPS:</td><td>$${data.eps.toFixed(2)}</td></tr>
              <tr><td>52W HIGH:</td><td class="positive">$${data.high52w.toFixed(2)}</td></tr>
              <tr><td>52W LOW:</td><td class="negative">$${data.low52w.toFixed(2)}</td></tr>
              <tr><td>VOLUME:</td><td>${data.volume.toLocaleString()}</td></tr>
          </table>
          
          <div style="color: #ff9900; font-weight: bold; margin: 15px 0 5px 0;">COMPANY INFO</div>
          <table class="data-table">
              <tr><td>SECTOR:</td><td>${data.sector}</td></tr>
              <tr><td>INDUSTRY:</td><td>${data.industry}</td></tr>
              <tr><td>BETA:</td><td>${data.beta.toFixed(2)}</td></tr>
              <tr><td>DIV YIELD:</td><td>${data.dividendYield.toFixed(2)}%</td></tr>
          </table>
      </div>
    `
  }

  function renderPortfolio(data) {
    let html = '<div style="color: #ff9900; font-weight: bold; margin-bottom: 10px;">PORTFOLIO SUMMARY</div>'

    const holdings = data.holdings || data.stocks || []
    const totalValue = data.totalValue || data.total_value || 0
    const totalCost = data.totalCost || data.total_cost || 0
    const totalGainLoss = data.totalGainLoss || data.total_gain_loss || 0
    const totalGainLossPercent = data.totalGainLossPercent || data.total_return_percent || 0

    const totalGainLossClass = totalGainLoss >= 0 ? "positive" : "negative"
    html += `
      <table class="data-table" style="margin-bottom: 20px;">
          <tr><td>TOTAL VALUE:</td><td class="positive">$${totalValue.toFixed(2)}</td></tr>
          <tr><td>TOTAL COST:</td><td>$${totalCost.toFixed(2)}</td></tr>
          <tr><td>TOTAL P&L:</td><td class="${totalGainLossClass}">${totalGainLoss >= 0 ? "▲" : "▼"} $${Math.abs(totalGainLoss).toFixed(2)} (${totalGainLossPercent.toFixed(2)}%)</td></tr>
      </table>
    `

    html += '<div style="color: #ff9900; font-weight: bold; margin-bottom: 5px;">HOLDINGS</div>'
    html += '<table class="data-table">'
    html += "<tr><th>SYMBOL</th><th>SHARES</th><th>AVG COST</th><th>CURR PRICE</th><th>VALUE</th><th>P&L</th></tr>"

    holdings.forEach((holding) => {
      const symbol = holding.symbol || holding.ticker
      const shares = holding.shares
      const avgCost = holding.avgCost || holding.purchase_price
      const currentPrice = holding.currentPrice || holding.current_price || 0
      const totalValue = holding.totalValue || holding.current_value || 0
      const gainLoss = holding.gainLoss || holding.gain_loss || 0
      const gainLossClass = gainLoss >= 0 ? "positive" : "negative"

      html += `
        <tr>
            <td style="color: #ff9900; font-weight: bold;">${symbol}</td>
            <td>${shares}</td>
            <td>$${avgCost.toFixed(2)}</td>
            <td>$${currentPrice.toFixed(2)}</td>
            <td>$${totalValue.toFixed(2)}</td>
            <td class="${gainLossClass}">${gainLoss >= 0 ? "▲" : "▼"} $${Math.abs(gainLoss).toFixed(2)}</td>
        </tr>
      `
    })

    html += "</table>"
    return html
  }

  function renderNews(articles) {
    let html = '<div style="color: #ff9900; font-weight: bold; margin-bottom: 10px;">MARKET NEWS</div>'

    if (!articles || articles.length === 0) {
      return html + '<div class="text-center">No news articles available</div>'
    }

    articles.forEach((article) => {
      const sentimentClass =
        article.sentiment === "positive" ? "positive" : article.sentiment === "negative" ? "negative" : "neutral"
      html += `
        <div style="border: 1px solid #333; margin: 10px 0; padding: 10px;">
            <div style="color: #ff9900; font-weight: bold; margin-bottom: 5px;">${article.title}</div>
            <div style="margin-bottom: 5px; font-size: 11px;">${article.summary}</div>
            <div style="font-size: 10px; color: #888;">
                <span>${article.source}</span> | 
                <span class="${sentimentClass}">${article.sentiment.toUpperCase()}</span> | 
                <span>${new Date(article.publishedAt).toLocaleDateString()}</span>
            </div>
        </div>
      `
    })

    return html
  }

  function renderSECFilings(filings) {
    let html = '<div style="color: #ff9900; font-weight: bold; margin-bottom: 10px;">SEC FILINGS</div>'

    if (!filings || filings.length === 0) {
      return html + "<div>No SEC filings available</div>"
    }

    html += '<table class="data-table">'
    html += "<tr><th>FORM</th><th>FILED DATE</th><th>REPORT DATE</th></tr>"

    filings.forEach((filing) => {
      html += `
        <tr>
            <td>${filing.formType}</td>
            <td>${filing.filedDate}</td>
            <td>${filing.reportDate || "N/A"}</td>
        </tr>
      `
    })

    html += "</table>"
    return html
  }

  function organizeWindows(direction) {
    console.log(
      "Organizing windows:",
      direction,
      "Active window:",
      activeWindow ? activeWindow.querySelector(".window-header").textContent : "none",
    )

    if (!activeWindow || windows.length < 2) {
      console.log("No active window or not enough windows to organize")
      return
    }

    const currentIndex = windows.indexOf(activeWindow)
    console.log("Current window index:", currentIndex)

    let newIndex

    if (direction === "left" && currentIndex > 0) {
      newIndex = currentIndex - 1
    } else if (direction === "right" && currentIndex < windows.length - 1) {
      newIndex = currentIndex + 1
    } else {
      console.log("Cannot move window further in that direction")
      return
    }

    console.log("Moving window to index:", newIndex)

    // Swap positions
    const currentWindow = windows[currentIndex]
    const targetWindow = windows[newIndex]

    // Get current positions
    const currentRect = currentWindow.getBoundingClientRect()
    const targetRect = targetWindow.getBoundingClientRect()

    console.log("Current window position:", currentRect.left, currentRect.top)
    console.log("Target window position:", targetRect.left, targetRect.top)

    // Ensure windows don't go off-screen
    const maxLeft = window.innerWidth - 300 // minimum window width
    const maxTop = window.innerHeight - 200 // minimum window height

    const newCurrentLeft = Math.min(Math.max(0, targetRect.left), maxLeft)
    const newCurrentTop = Math.min(Math.max(0, targetRect.top), maxTop)
    const newTargetLeft = Math.min(Math.max(0, currentRect.left), maxLeft)
    const newTargetTop = Math.min(Math.max(0, currentRect.top), maxTop)

    // Swap positions with animation
    currentWindow.style.transition = "left 0.3s, top 0.3s"
    targetWindow.style.transition = "left 0.3s, top 0.3s"

    currentWindow.style.left = `${newCurrentLeft}px`
    currentWindow.style.top = `${newCurrentTop}px`
    targetWindow.style.left = `${newTargetLeft}px`
    targetWindow.style.top = `${newTargetTop}px`

    // Remove transition after animation completes
    setTimeout(() => {
      currentWindow.style.transition = ""
      targetWindow.style.transition = ""
    }, 300)

    // Update array
    windows[currentIndex] = targetWindow
    windows[newIndex] = currentWindow
  }

  function makeDraggable(element) {
    // Check if interact is available globally
    if (typeof interact !== "undefined") {
      interact(element).draggable({
        allowFrom: ".window-header",
        listeners: {
          start(event) {
            bringToFront(event.target)
          },
          move(event) {
            const target = event.target
            const x = (Number.parseFloat(target.getAttribute("data-x")) || 0) + event.dx
            const y = (Number.parseFloat(target.getAttribute("data-y")) || 0) + event.dy

            target.style.transform = `translate(${x}px, ${y}px)`
            target.setAttribute("data-x", x)
            target.setAttribute("data-y", y)
          },
        },
      })
    } else {
      // Fallback: basic drag functionality without interact.js
      let isDragging = false
      let startX, startY, initialX, initialY

      const header = element.querySelector(".window-header")
      if (header) {
        header.addEventListener("mousedown", (e) => {
          if (e.target.classList.contains("close-button")) return

          isDragging = true
          startX = e.clientX
          startY = e.clientY

          const rect = element.getBoundingClientRect()
          initialX = rect.left
          initialY = rect.top

          bringToFront(element)

          document.addEventListener("mousemove", onMouseMove)
          document.addEventListener("mouseup", onMouseUp)
        })

        function onMouseMove(e) {
          if (!isDragging) return

          const deltaX = e.clientX - startX
          const deltaY = e.clientY - startY

          element.style.left = initialX + deltaX + "px"
          element.style.top = initialY + deltaY + "px"
        }

        function onMouseUp() {
          isDragging = false
          document.removeEventListener("mousemove", onMouseMove)
          document.removeEventListener("mouseup", onMouseUp)
        }
      }
    }
  }

  function makeResizable(element) {
    // Check if interact is available globally
    if (typeof interact !== "undefined") {
      interact(element).resizable({
        edges: { bottom: true, right: true, top: false, left: false },
        listeners: {
          move(event) {
            const target = event.target
            let { x, y } = target.dataset

            x = (Number.parseFloat(x) || 0) + event.deltaRect.left
            y = (Number.parseFloat(y) || 0) + event.deltaRect.top

            Object.assign(target.style, {
              width: `${event.rect.width}px`,
              height: `${event.rect.height}px`,
              transform: `translate(${x}px, ${y}px)`,
            })

            Object.assign(target.dataset, { x, y })
          },
        },
      })
    } else {
      // Fallback: add resize handles manually
      const resizeHandle = document.createElement("div")
      resizeHandle.style.cssText = `
        position: absolute;
        bottom: 0;
        right: 0;
        width: 10px;
        height: 10px;
        background: #ff9900;
        cursor: se-resize;
        z-index: 1000;
      `

      element.appendChild(resizeHandle)

      let isResizing = false
      let startX, startY, startWidth, startHeight

      resizeHandle.addEventListener("mousedown", (e) => {
        isResizing = true
        startX = e.clientX
        startY = e.clientY
        startWidth = Number.parseInt(document.defaultView.getComputedStyle(element).width, 10)
        startHeight = Number.parseInt(document.defaultView.getComputedStyle(element).height, 10)

        document.addEventListener("mousemove", onMouseMove)
        document.addEventListener("mouseup", onMouseUp)
      })

      function onMouseMove(e) {
        if (!isResizing) return

        const width = startWidth + e.clientX - startX
        const height = startHeight + e.clientY - startY

        element.style.width = Math.max(300, width) + "px"
        element.style.height = Math.max(200, height) + "px"
      }

      function onMouseUp() {
        isResizing = false
        document.removeEventListener("mousemove", onMouseMove)
        document.removeEventListener("mouseup", onMouseUp)
      }
    }
  }

  function clearAllWindows() {
    windows.forEach((window) => {
      if (window.dataset.intervalId) {
        clearInterval(Number(window.dataset.intervalId))
      }
      window.remove()
    })
    windows = []
    windowIndex = 0
    activeWindow = null
    updateWindowCount()
  }

  // Mock data functions for when APIs fail
  function getMockQuote(ticker) {
    const price = 100 + Math.random() * 100
    const previousClose = price - (Math.random() * 10 - 5)
    const change = price - previousClose
    const changePercent = (change / previousClose) * 100

    return {
      symbol: ticker,
      price: price,
      change: change,
      changePercent: changePercent,
      volume: Math.floor(Math.random() * 10000000),
      previousClose: previousClose,
    }
  }

  function getMockStockInfo(ticker) {
    const price = 100 + Math.random() * 100
    const previousClose = price - (Math.random() * 10 - 5)
    const change = price - previousClose
    const changePercent = (change / previousClose) * 100

    return {
      symbol: ticker,
      name: `${ticker} Inc.`,
      price: price,
      change: change,
      changePercent: changePercent,
      volume: Math.floor(Math.random() * 10000000),
      previousClose: previousClose,
      marketCap: Math.random() * 1000 * 1e9,
      peRatio: 10 + Math.random() * 30,
      eps: 1 + Math.random() * 10,
      high52w: price * 1.2,
      low52w: price * 0.8,
      dividendYield: Math.random() * 5,
      beta: 0.5 + Math.random() * 1.5,
      sector: "Technology",
      industry: "Software",
    }
  }

  function getMockChartData(ticker) {
    const data = []
    const basePrice = 100 + Math.random() * 100
    const today = new Date()

    for (let i = 30; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(today.getDate() - i)

      // Skip weekends
      if (date.getDay() === 0 || date.getDay() === 6) continue

      const close = basePrice + (Math.random() * 20 - 10) + i / 3
      const open = close + (Math.random() * 5 - 2.5)
      const high = Math.max(open, close) + Math.random() * 3
      const low = Math.min(open, close) - Math.random() * 3

      data.push({
        date: date.toISOString().split("T")[0],
        open: open,
        high: high,
        low: low,
        close: close,
        volume: Math.floor(Math.random() * 10000000),
      })
    }

    return data
  }

  function getMockPortfolio() {
    const holdings = [
      {
        symbol: "AAPL",
        shares: 10,
        avgCost: 150,
        currentPrice: 170,
        totalValue: 1700,
        gainLoss: 200,
        gainLossPercent: 13.33,
      },
      {
        symbol: "MSFT",
        shares: 5,
        avgCost: 250,
        currentPrice: 280,
        totalValue: 1400,
        gainLoss: 150,
        gainLossPercent: 12,
      },
      {
        symbol: "GOOGL",
        shares: 2,
        avgCost: 2000,
        currentPrice: 2200,
        totalValue: 4400,
        gainLoss: 400,
        gainLossPercent: 10,
      },
    ]

    const totalValue = holdings.reduce((sum, h) => sum + h.totalValue, 0)
    const totalCost = holdings.reduce((sum, h) => sum + h.avgCost * h.shares, 0)
    const totalGainLoss = totalValue - totalCost
    const totalGainLossPercent = (totalGainLoss / totalCost) * 100

    return {
      holdings: holdings,
      totalValue: totalValue,
      totalCost: totalCost,
      totalGainLoss: totalGainLoss,
      totalGainLossPercent: totalGainLossPercent,
    }
  }

  function getMockNews() {
    return [
      {
        title: "Federal Reserve Signals Potential Rate Cut in Q2",
        summary:
          "The Federal Reserve indicated in today's meeting that economic conditions may warrant a rate reduction in the second quarter, citing inflation concerns and employment data.",
        url: "https://example.com/news/1",
        publishedAt: new Date().toISOString(),
        source: "Financial Times",
        sentiment: "positive",
      },
      {
        title: "Tech Stocks Rally on AI Breakthrough Announcements",
        summary:
          "Major technology companies saw significant gains following announcements of new artificial intelligence capabilities and partnerships.",
        url: "https://example.com/news/2",
        publishedAt: new Date(Date.now() - 3600000).toISOString(),
        source: "Reuters",
        sentiment: "positive",
      },
      {
        title: "Energy Sector Faces Headwinds Amid Regulatory Changes",
        summary:
          "New environmental regulations are expected to impact energy companies' operations and profitability in the coming quarters.",
        url: "https://example.com/news/3",
        publishedAt: new Date(Date.now() - 7200000).toISOString(),
        source: "Bloomberg",
        sentiment: "negative",
      },
    ]
  }

  function getMockSECFilings(ticker) {
    return [
      {
        formType: "10-K",
        filedDate: "2023-02-15",
        reportDate: "2022-12-31",
        url: "https://example.com/sec/1",
        accessionNumber: "0001234567-23-000123",
      },
      {
        formType: "10-Q",
        filedDate: "2023-05-10",
        reportDate: "2023-03-31",
        url: "https://example.com/sec/2",
        accessionNumber: "0001234567-23-000456",
      },
      {
        formType: "8-K",
        filedDate: "2023-06-01",
        reportDate: null,
        url: "https://example.com/sec/3",
        accessionNumber: "0001234567-23-000789",
      },
    ]
  }

  // Focus input on click
  document.addEventListener("click", (e) => {
    // Only focus input if not clicking on a window
    if (!e.target.closest(".window")) {
      input.focus()
    }
  })

  // Add keyboard shortcuts help
  const shortcutsHelp = document.createElement("div")
  shortcutsHelp.id = "keyboard-shortcuts"
  shortcutsHelp.innerHTML = `
  <div><strong>Window Controls:</strong></div>
  <div><kbd>Ctrl</kbd>+<kbd>←</kbd> Move Left</div>
  <div><kbd>Ctrl</kbd>+<kbd>→</kbd> Move Right</div>
  <div><kbd>Ctrl</kbd>+<kbd>↑</kbd> Maximize</div>
  <div><kbd>Ctrl</kbd>+<kbd>↓</kbd> Restore</div>
`
  document.body.appendChild(shortcutsHelp)

  // Add click handler to focus input when clicking on terminal background
  document.getElementById("terminal").addEventListener("click", (e) => {
    // Only focus input if clicking directly on terminal background
    if (e.target.id === "terminal" || e.target.id === "main-area") {
      input.focus()
    }
  })
})
