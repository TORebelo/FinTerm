// import { NextResponse } from "next/server"

// export async function GET() {
//   try {
//     // Mock news data for demo
//     // In production, integrate with real news APIs like NewsAPI, Alpha Vantage, or Finnhub
//     const mockNews = [
//       {
//         title: "Federal Reserve Signals Potential Rate Cut in Q2",
//         summary:
//           "The Federal Reserve indicated in today's meeting that economic conditions may warrant a rate reduction in the second quarter, citing inflation concerns and employment data.",
//         url: "https://example.com/news/1",
//         publishedAt: new Date().toISOString(),
//         source: "Financial Times",
//         sentiment: "positive" as const,
//       },
//       {
//         title: "Tech Stocks Rally on AI Breakthrough Announcements",
//         summary:
//           "Major technology companies saw significant gains following announcements of new artificial intelligence capabilities and partnerships.",
//         url: "https://example.com/news/2",
//         publishedAt: new Date(Date.now() - 3600000).toISOString(),
//         source: "Reuters",
//         sentiment: "positive" as const,
//       },
//       {
//         title: "Energy Sector Faces Headwinds Amid Regulatory Changes",
//         summary:
//           "New environmental regulations are expected to impact energy companies' operations and profitability in the coming quarters.",
//         url: "https://example.com/news/3",
//         publishedAt: new Date(Date.now() - 7200000).toISOString(),
//         source: "Bloomberg",
//         sentiment: "negative" as const,
//       },
//       {
//         title: "Consumer Spending Data Shows Mixed Signals",
//         summary:
//           "Latest consumer spending reports indicate varied performance across different sectors, with retail showing strength while services lag.",
//         url: "https://example.com/news/4",
//         publishedAt: new Date(Date.now() - 10800000).toISOString(),
//         source: "Wall Street Journal",
//         sentiment: "neutral" as const,
//       },
//       {
//         title: "Cryptocurrency Market Stabilizes After Recent Volatility",
//         summary:
//           "Digital assets are showing signs of stabilization following a period of high volatility, with institutional adoption continuing to grow.",
//         url: "https://example.com/news/5",
//         publishedAt: new Date(Date.now() - 14400000).toISOString(),
//         source: "CoinDesk",
//         sentiment: "neutral" as const,
//       },
//     ]

//     return NextResponse.json({ articles: mockNews })
//   } catch (error) {
//     console.error("News API error:", error)
//     return NextResponse.json({ error: "Failed to fetch news" }, { status: 500 })
//   }
// }
