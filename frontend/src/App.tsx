
import { useEffect, useState } from 'react'
import './App.css'

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'

const API_URL = 'http://127.0.0.1:8000'

type AnalysisRow = {
  startTime: string
  forecast: number
  actual: number
  error: number
  absoluteError: number
}

type Analysis = {
  startDate: string
  endDate: string
  decisionCutoff: string
  actualHalfHourlyIntervals: number
  completeHourlyActualIntervals: number
  eligibleForecastIntervals: number
  matchedIntervals: number
  metrics: {
    maeMW: number
    rmseMW: number
    biasMW: number
  } | null
  data: AnalysisRow[]
  warning?: string
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-GB', {
    maximumFractionDigits: 0,
  }).format(value)
}

function App() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [startDate, setStartDate] = useState('2026-01-01')
  const [endDate, setEndDate] = useState('2026-01-31')

  async function loadAnalysis() {
    setLoading(true)
    setError('')

    try {
      const params = new URLSearchParams({ start_date: startDate, end_date: endDate })
      const response = await fetch(`${API_URL}/api/analysis?${params}`)

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || 'Unable to load wind forecast analysis.')
      }

      const result: Analysis = await response.json()
      setAnalysis(result)
    } catch {
      setError(
  'We couldn’t load wind generation data. Please check your connection and try again.'
)
      setAnalysis(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadAnalysis()
  }, [])

  const metrics = analysis?.metrics
  const chartRows = analysis?.data ?? []
const dailyRows = Object.values(
  chartRows.reduce<
    Record<string, { date: string; forecastTotal: number; actualTotal: number; count: number }>
  >((groups, row) => {
    const date = row.startTime.slice(0, 10)


    if (!groups[date]) {
      groups[date] = {
        date,
        forecastTotal: 0,
        actualTotal: 0,
        count: 0,
      }
    }

    groups[date].forecastTotal += row.forecast
    groups[date].actualTotal += row.actual
    groups[date].count += 1

    return groups
  }, {}),
).map((day) => ({
  date: day.date.slice(5),
  forecast: Math.round(day.forecastTotal / day.count),
  actual: Math.round(day.actualTotal / day.count),
}))

const worstDay = [...dailyRows].sort(
  (a, b) => Math.abs(b.forecast - b.actual) - Math.abs(a.forecast - a.actual)
)[0]

  return (
    <main className="dashboard">
      <aside className="sidebar">
        <a className="brand" href="#">
          <span className="brand-mark">G</span>
          <span>gridbricks<span className="brand-dot">.</span></span>
        </a>

        <div className="workspace-label">WORKSPACE</div>
        <div className="nav-item active"><span>▥</span> Overview</div>
        <div className="nav-item"><span>↗</span> Forecast analysis</div>
        <div className="nav-item"><span>◷</span> Historical data</div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>Data connection</strong>
            <small>Elexon BMRS API</small>
          </div>
        </div>
      </aside>

      <section className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Energy intelligence <span>/</span> Wind generation</div>
          <div className="live-label"><span /> UK NATIONAL GRID</div>
        </header>

        <div className="page-heading">
          <div>
            <p className="eyebrow">RENEWABLES / UNITED KINGDOM</p>
            <h1>Wind generation <span>intelligence</span></h1>
            <p className="subtitle">
              Understand forecast performance and actual wind generation across the UK.
            </p>
          </div>
          <div className="date-control">
            <label>
              From
              <input
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
              />
            </label>
            <label>
              To
              <input
                type="date"
                value={endDate}
                onChange={(event) => setEndDate(event.target.value)}
              />
            </label>
            <button onClick={() => void loadAnalysis()} disabled={loading}>
              {loading ? 'Loading…' : 'Apply'}
            </button>
          </div>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <div className="section-label">PERFORMANCE SNAPSHOT <span>·</span> {startDate} — {endDate}</div>

        <div className="metric-grid">
          <article className="metric-card primary-metric">
            <div className="metric-top"><span>Mean absolute error</span><span className="metric-icon">↕</span></div>
            <div className="metric-value">{loading ? '—' : metrics ? formatNumber(metrics.maeMW) : 'N/A'} <small>MW</small></div>
            <div className="metric-foot">Average absolute forecast deviation</div>
          </article>
          <article className="metric-card">
            <div className="metric-top"><span>Root mean square error</span><span className="metric-icon">⌁</span></div>
            <div className="metric-value">{loading ? '—' : metrics ? formatNumber(metrics.rmseMW) : 'N/A'} <small>MW</small></div>
            <div className="metric-foot">Penalises larger forecast misses</div>
          </article>
          <article className="metric-card">
            <div className="metric-top"><span>Forecast bias</span><span className="metric-icon">±</span></div>
            <div className="metric-value">{loading ? '—' : metrics ? `${metrics.biasMW > 0 ? '+' : ''}${formatNumber(metrics.biasMW)}` : 'N/A'} <small>MW</small></div>
            <div className="metric-foot">{metrics && metrics.biasMW > 0 ? 'Forecasts higher than actuals on average' : 'Average forecast minus actual'}</div>
          </article>
          <article className="metric-card">
            <div className="metric-top"><span>Matched intervals</span><span className="metric-icon">✓</span></div>
            <div className="metric-value">{loading ? '—' : formatNumber(analysis?.matchedIntervals ?? 0)} <small>/ {formatNumber(analysis?.completeHourlyActualIntervals ?? 0)}</small></div>
            <div className="metric-foot">Hourly intervals compared</div>
          </article>
        </div>

       
<section className="panel chart-panel">
  <div className="panel-heading">
    <div>
      <h2>Forecast vs actual generation</h2>
      <p>Daily average wind generation · MW · timestamps in UTC</p>
    </div>
    <div className="chart-legend">
      <span><i className="legend-forecast" /> Forecast</span>
      <span><i className="legend-actual" /> Actual</span>
    </div>
  </div>

  {loading ? (
    <div className="chart-message">Loading generation data…</div>
  ) : dailyRows.length === 0 ? (
    <div className="chart-message">No matched data available for this date range.</div>
  ) : (
    <div className="line-chart-wrap">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart
          data={dailyRows}
          margin={{ top: 20, right: 12, left: 8, bottom: 5 }}
        >
          <CartesianGrid stroke="#e9eee7" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: '#7c8b80', fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: '#e3e9e1' }}
            interval={Math.max(0, Math.floor(dailyRows.length / 8) - 1)}
          />
          <YAxis
            tick={{ fill: '#7c8b80', fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: number) => `${Math.round(value / 1000)}k`}
            width={42}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 10,
              border: '1px solid #e2e9df',
              fontSize: 12,
            }}
            formatter={(value) => [
              `${Number(value).toLocaleString('en-GB')} MW`,
            ]}
            labelFormatter={(label) => `January ${label}`}
          />
          <Legend verticalAlign="top" height={32} />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            stroke="#9dbf70"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual"
            stroke="#234c3a"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )}
</section>

<section className="panel table-panel">
  <div className="panel-heading">
    <div>
      <h2>Daily generation breakdown</h2>
      <p>Average forecast and actual wind generation · MW</p>
    </div>
  </div>

  <div className="table-scroll">
    <table className="generation-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Forecast (MW)</th>
          <th>Actual (MW)</th>
          <th>Gap (MW)</th>
        </tr>
      </thead>
      <tbody>
        {dailyRows.map((day) => (
          <tr key={day.date}>
            <td>{day.date}</td>
            <td>{formatNumber(day.forecast)}</td>
            <td>{formatNumber(day.actual)}</td>
            <td className={day.forecast - day.actual >= 0 ? 'positive-gap' : 'negative-gap'}>
              {day.forecast - day.actual > 0 ? '+' : ''}
              {formatNumber(day.forecast - day.actual)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
</section>

        <div className="lower-grid">
          <section className="panel insight-panel">
            <div className="panel-heading">
              <div><h2>Decision insight</h2><p>What the metrics tell us</p></div>
              <span className="insight-symbol">↗</span>
            </div>
            {metrics ? (
              <>
                <div className="insight-number">{metrics.biasMW > 0 ? 'Over-forecasting' : metrics.biasMW < 0 ? 'Under-forecasting' : 'Low average bias'}</div>
                <p className="insight-copy">
                  The average forecast error is {formatNumber(Math.abs(metrics.biasMW))} MW
                  {metrics.biasMW > 0 ? ' above' : metrics.biasMW < 0 ? ' below' : ' from'} actual generation.
                  Use the error profile alongside operating context before making balancing or procurement decisions.
                </p>
              </>
            ) : (
              <p className="insight-copy">Insights will appear when analysis data is available.</p>
            )}
          </section>

          {worstDay && (
  <div className="worst-day">
    <span>Largest daily average gap</span>
    <strong>{worstDay.date}</strong>
    <p>
      Forecast: {formatNumber(worstDay.forecast)} MW · Actual:{' '}
      {formatNumber(worstDay.actual)} MW
    </p>
  </div>
)}

          <section className="panel methodology-panel">
            <div className="panel-heading"><div><h2>Methodology</h2><p>Data and comparison rules</p></div></div>
            <div className="method-row"><span>Actuals source</span><strong>FUELHH · WIND</strong></div>
            <div className="method-row"><span>Forecast source</span><strong>WINDFOR</strong></div>
            <div className="method-row"><span>Comparison grain</span><strong>Hourly average</strong></div>
            <div className="method-row"><span>Decision cutoff</span><strong>09:50 UTC · prior day</strong></div>
          </section>
        </div>

        {analysis?.warning && <p className="data-note">Note: {analysis.warning}</p>}

        <footer className="footer">
          <span>GRIDBRICKS <span className="brand-dot">·</span> ENERGY DECISIONS, MADE CLEAR</span>
          <span>Data: Elexon BMRS · January 2026</span>
        </footer>
      </section>
    </main>
  )
}

export default App
