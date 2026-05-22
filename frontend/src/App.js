import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { API_CONFIG } from './api/config'
import {
  mockApplications,
  mockRedFlags,
  mockMemos,
  mockRiskScores,
  defaultMockMemo
} from './mocks/mockData'

const apiFetch = (baseUrl, path, options = {}) => {
  const headers = {
    'ngrok-skip-browser-warning': 'true',
    ...(options.headers || {})
  }

  return fetch(`${baseUrl}${path}`, {
    ...options,
    headers
  })
}

const buildPortfolioSummary = (applications) => {
  const counts = { High:0, Medium:0, Low:0 }

  applications.forEach((app) => {
    if (counts[app.risk_tier] !== undefined) {
      counts[app.risk_tier] += 1
    }
  })

  return {
    total_applications: applications.length,
    high_risk_count: counts.High,
    medium_risk_count: counts.Medium,
    low_risk_count: counts.Low,
    avg_risk_score: 0
  }
}

const getMockApplicationById = (appId) =>
  mockApplications.find((app) => app.application_id === appId) || null

const fetchApplications = async () => {
  if (API_CONFIG.USE_MOCK) {
    return mockApplications
  }

  try {
    const response = await apiFetch(API_CONFIG.APPLICATIONS_API, '/api/applications')

    if (!response.ok) {
      throw new Error('Applications API down')
    }

    const data = await response.json()
    return data.applications || []
  } catch (err) {
    console.log('Applications API down, using mock')
    return mockApplications
  }
}

const fetchApplicationById = async (appId) => {
  if (API_CONFIG.USE_MOCK) {
    return getMockApplicationById(appId)
  }

  try {
    const response = await apiFetch(API_CONFIG.APPLICATIONS_API, `/api/applications/${appId}`)

    if (!response.ok) {
      throw new Error('Application API down')
    }

    return await response.json()
  } catch (err) {
    console.log('Application API down, using mock')
    return getMockApplicationById(appId)
  }
}

const fetchRedFlags = async (appId) => {
  if (API_CONFIG.USE_MOCK) {
    return mockRedFlags[appId] || { flag_count:0, flags:[] }
  }

  try {
    const response = await apiFetch(API_CONFIG.REDFLAGS_API, '/api/redflags', {
      method:'POST',
      headers:{ 'Content-Type':'application/json' },
      body: JSON.stringify({ application_id: appId })
    })

    if (!response.ok) {
      throw new Error('Red flags API down')
    }

    return await response.json()
  } catch (err) {
    console.log('Red flags API down, using mock')
    return mockRedFlags[appId] || { flag_count:0, flags:[] }
  }
}

const getFallbackRiskScore = (appId, fallbackTier) =>
  mockRiskScores[appId] || { risk_score:0.6, risk_tier:fallbackTier || 'Medium' }

const fetchRiskScore = async (payload, appId, fallbackTier) => {
  if (API_CONFIG.USE_MOCK) {
    return getFallbackRiskScore(appId, fallbackTier)
  }

  try {
    const response = await apiFetch(API_CONFIG.APPLICATIONS_API, '/api/score', {
      method:'POST',
      headers:{
        'Content-Type':'application/json'
      },
      body:JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error('Risk score API down')
    }

    const scoreData = await response.json()

    if (!scoreData || typeof scoreData !== 'object') {
      return getFallbackRiskScore(appId, fallbackTier)
    }

    return {
      ...scoreData,
      risk_tier: scoreData.risk_tier || fallbackTier || 'Medium'
    }
  } catch (err) {
    console.log('Risk score API down, using mock')
    return getFallbackRiskScore(appId, fallbackTier)
  }
}

const fetchMemo = async (appId) => {
  if (API_CONFIG.USE_MOCK) {
    return mockMemos[appId] || defaultMockMemo
  }

  try {
    const response = await apiFetch(API_CONFIG.MEMO_API, '/api/memo', {
      method:'POST',
      headers:{
        'Content-Type':'application/json'
      },
      body: JSON.stringify({ application_id: appId })
    })

    if (!response.ok) {
      throw new Error('Memo API down')
    }

    return await response.json()
  } catch (err) {
    console.log('Memo API down, using mock')
    return mockMemos[appId] || defaultMockMemo
  }
}

const nav = {
  width: '210px',
  background: '#1B2A4A',
  minHeight: '100vh',
  padding: '20px'
}

const lnk = {
  display: 'block',
  color: '#D6E4F0',
  textDecoration: 'none',
  padding: '10px',
  marginBottom: '8px',
  borderRadius: '4px',
  fontSize: '14px'
}

const rc = (r) =>
  r === 'Low' ? '#1A6B3A' :
  r === 'Medium' ? '#B7791F' :
  '#C53030'

const formatCurrency = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return 'N/A'
  }

  return Number(value).toLocaleString()
}

const formatRiskScore = (value) => {
  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return 'N/A'
  }

  return `${(numericValue * 100).toFixed(1)}%`
}

const memoValueToText = (value) => {
  if (value === null || value === undefined) {
    return ''
  }

  if (typeof value === 'string') {
    return value
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }

  if (Array.isArray(value)) {
    return value.map((item) => memoValueToText(item)).join('\n')
  }

  return JSON.stringify(value, null, 2)
}

const normalizeMemoSections = (memo) => {
  if (!memo) {
    return []
  }

  if (Array.isArray(memo)) {
    return memo.map((section, index) => ({
      title: section.title || section.heading || section.name || `Section ${index + 1}`,
      content: memoValueToText(section.content || section.body || section.text || section)
    }))
  }

  if (Array.isArray(memo.sections)) {
    return memo.sections.map((section, index) => ({
      title: section.title || section.heading || section.name || `Section ${index + 1}`,
      content: memoValueToText(section.content || section.body || section.text || section)
    }))
  }

  if (typeof memo === 'object') {
    return Object.entries(memo)
      .filter(([key, value]) => key !== 'application_id' && key !== 'sections' && value !== undefined)
      .map(([key, value]) => ({
        title: key.replace(/_/g, ' '),
        content: memoValueToText(value)
      }))
  }

  return []
}

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const Dashboard = () => {
  const [portfolio, setPortfolio] = useState({
    total_applications: 15000,
    high_risk_count: 2700,
    medium_risk_count: 4500,
    low_risk_count: 7800,
    avg_risk_score: 42.3
  })

  useEffect(() => {
    if (API_CONFIG.USE_MOCK) {
      setPortfolio(buildPortfolioSummary(mockApplications))
      return
    }

    apiFetch(API_CONFIG.APPLICATIONS_API, '/api/portfolio/summary')
      .then((r) => r.json())
      .then((data) => setPortfolio(data))
      .catch(() => setPortfolio(buildPortfolioSummary(mockApplications)))
  }, [])

  return (
    <div style={{
      padding:'40px',
      flex:1,
      background:'#F4F6F9',
      minHeight:'100vh'
    }}>
      <h2 style={{ color:'#1B2A4A', marginBottom:'8px' }}>
        Dashboard
      </h2>

      <p style={{ color:'#4A5568', marginBottom:'30px' }}>
        CreditSentinel — Live Overview
      </p>

      <div style={{
        display:'flex',
        gap:'20px',
        marginBottom:'30px',
        flexWrap:'wrap'
      }}>
        {[
          {
            label:'Total Applications',
            value:portfolio.total_applications,
            color:'#1B2A4A'
          },
          {
            label:'High Risk',
            value:portfolio.high_risk_count,
            color:'#C53030'
          },
          {
            label:'Medium Risk',
            value:portfolio.medium_risk_count,
            color:'#B7791F'
          },
          {
            label:'Low Risk',
            value:portfolio.low_risk_count,
            color:'#1A6B3A'
          }
        ].map((k) => (
          <div
            key={k.label}
            style={{
              background:'white',
              padding:'24px',
              borderRadius:'8px',
              flex:1,
              minWidth:'160px',
              boxShadow:'0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            <p style={{ color:'#4A5568', fontSize:'13px', margin:'0 0 8px' }}>
              {k.label}
            </p>
            <h3 style={{ color:k.color, fontSize:'28px', margin:0, fontWeight:'bold' }}>
              {Number(k.value).toLocaleString()}
            </h3>
          </div>
        ))}
      </div>
    </div>
  )
}

const Applications = () => {
  const [applications, setApplications] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    let isMounted = true

    fetchApplications()
      .then((data) => {
        if (isMounted) {
          setApplications(data)
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  return (
    <div style={{
      padding:'40px',
      flex:1,
      background:'#F4F6F9',
      minHeight:'100vh'
    }}>
      <h2 style={{ color:'#1B2A4A' }}>
        Loan Applications
      </h2>
      <p style={{ color:'#4A5568', marginBottom:'20px' }}>
        Showing {applications.length} applications
      </p>

      <table style={{
        width:'100%',
        borderCollapse:'collapse',
        background:'white',
        borderRadius:'8px',
        overflow:'hidden',
        boxShadow:'0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <thead>
          <tr style={{ background:'#1B2A4A' }}>
            {['App ID','Applicant','Income','Loan Amount','FOIR','Risk'].map((h) => (
              <th
                key={h}
                style={{ padding:'12px', color:'white', textAlign:'left', fontSize:'13px' }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {applications.map((a, index) => (
            <tr
              key={a.application_id}
              onClick={() => navigate(`/application/${a.application_id}`)}
              style={{
                background:index % 2 === 0 ? '#F4F6F9' : 'white',
                borderBottom:'1px solid #E2E8F0',
                cursor:'pointer'
              }}
            >
              <td style={{ padding:'10px 12px', fontSize:'13px', color:'#4A5568' }}>{a.application_id}</td>
              <td style={{ padding:'10px 12px', fontSize:'13px' }}>{a.applicant_name}</td>
              <td style={{ padding:'10px 12px', fontSize:'13px' }}>₹{formatCurrency(a.monthly_income)}</td>
              <td style={{ padding:'10px 12px', fontSize:'13px' }}>₹{formatCurrency(a.requested_loan_amount)}</td>
              <td style={{ padding:'10px 12px', fontSize:'13px' }}>{a.foir}%</td>
              <td style={{
                padding:'10px 12px',
                fontWeight:'bold',
                fontSize:'13px',
                color:rc(a.risk_tier)
              }}>{a.risk_tier}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const ApplicationDetail = () => {
  const { id } = useParams()
  const [application, setApplication] = useState(null)
  const [riskResult, setRiskResult] = useState(null)
  const [redFlags, setRedFlags] = useState({ flag_count:0, flags:[] })
  const [memoData, setMemoData] = useState(null)
  const [memoLoading, setMemoLoading] = useState(false)
  const [memoError, setMemoError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchDetail() {
      try {
        setMemoData(null)
        setMemoLoading(false)
        setMemoError('')

        const data = await fetchApplicationById(id)
        setApplication(data)

        const flagsData = await fetchRedFlags(id)
        setRedFlags(flagsData)

        if (data) {
          const scorePayload = {
            application_id:data.application_id,
            monthly_income:data.monthly_income,
            requested_loan_amount:data.requested_loan_amount,
            existing_monthly_emi:data.existing_monthly_emi || 0,
            employment_type:data.employment_type || 'Salaried',
            employment_years:data.employment_years || 1,
            foir:data.foir,
            loan_to_income_ratio:data.loan_to_income_ratio || 0.6,
            is_night_application:data.is_night_application || 0,
            cibil_score:data.cibil_score || 700,
            num_credit_inquiries_30d:data.num_credit_inquiries_30d || 0,
            has_previous_default:data.has_previous_default || 0,
            credit_utilization_pct:data.credit_utilization_pct || 40
          }

          const scoreData = await fetchRiskScore(scorePayload, data.application_id, data.risk_tier)
          setRiskResult(scoreData)
        }
      } catch (err) {
        console.log(err)
      }

      setLoading(false)
    }

    fetchDetail()
  }, [id])

  const memoSections = normalizeMemoSections(memoData)

  const handleGenerateMemo = async () => {
    if (!application?.application_id) {
      return
    }

    setMemoLoading(true)
    setMemoError('')

    try {
      const [memo] = await Promise.all([
        fetchMemo(application.application_id),
        delay(400)
      ])
      setMemoData(memo)
    } catch (err) {
      console.log(err)
      setMemoError('Unable to generate memo right now.')
    } finally {
      setMemoLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ padding:'40px', flex:1 }}>
        Loading...
      </div>
    )
  }

  if (!application) {
    return (
      <div style={{ padding:'40px', flex:1 }}>
        Application not found
      </div>
    )
  }

  return (
    <div style={{
      padding:'40px',
      flex:1,
      background:'#F4F6F9',
      minHeight:'100vh'
    }}>
      <h2 style={{ color:'#1B2A4A' }}>
        Application Detail
      </h2>

      <div style={{
        background:'white',
        padding:'24px',
        borderRadius:'8px',
        marginTop:'20px',
        boxShadow:'0 2px 6px rgba(0,0,0,0.1)'
      }}>
        <h3>{application.applicant_name}</h3>

        <p><strong>Application ID:</strong> {application.application_id}</p>
        <p><strong>Income:</strong> ₹{formatCurrency(application.monthly_income)}</p>
        <p><strong>Loan Amount:</strong> ₹{formatCurrency(application.requested_loan_amount)}</p>
        <p><strong>FOIR:</strong> {application.foir}%</p>
        <p><strong>CIBIL:</strong> {application.cibil_score || 'N/A'}</p>
      </div>

      <div style={{
        background:'white',
        padding:'24px',
        borderRadius:'8px',
        marginTop:'20px',
        boxShadow:'0 2px 6px rgba(0,0,0,0.1)'
      }}>
        <h3>Risk Score</h3>

        {riskResult && (
          <>
            <h2 style={{ color:rc(riskResult.risk_tier) }}>
              {formatRiskScore(riskResult.risk_score)}
            </h2>

            <p style={{
              color:rc(riskResult.risk_tier),
              fontWeight:'bold'
            }}>
              {riskResult.risk_tier} Risk
            </p>
          </>
        )}
      </div>

      <div style={{
        background:'white',
        padding:'24px',
        borderRadius:'8px',
        marginTop:'20px',
        boxShadow:'0 2px 6px rgba(0,0,0,0.1)'
      }}>
        <h3>Red Flags</h3>

        <ul>
          {(redFlags?.flags || []).length === 0 && (
            <li>No red flags found</li>
          )}
          {(redFlags?.flags || []).map((flag) => (
            <li key={`${flag.rule}-${flag.evidence}`}>
              {flag.rule} - {flag.evidence}
            </li>
          ))}
        </ul>
      </div>

      <div style={{
        background:'white',
        padding:'24px',
        borderRadius:'8px',
        marginTop:'20px',
        boxShadow:'0 2px 6px rgba(0,0,0,0.1)'
      }}>
        <h3>Credit Memo</h3>

        <button
          onClick={handleGenerateMemo}
          disabled={memoLoading}
          style={{
            background:'#1B2A4A',
            color:'white',
            padding:'12px 24px',
            border:'none',
            borderRadius:'6px',
            cursor:memoLoading ? 'default' : 'pointer',
            opacity:memoLoading ? 0.7 : 1,
            display:'inline-flex',
            alignItems:'center',
            gap:'8px'
          }}
        >
          {memoLoading && <span className="spinner" aria-hidden="true" />}
          {memoLoading ? 'Generating...' : 'Generate Memo'}
        </button>

        {memoError && (
          <p style={{ marginTop:'12px', color:'#C53030' }}>
            {memoError}
          </p>
        )}

        {memoSections.length > 0 && (
          <div style={{
            marginTop:'16px',
            display:'grid',
            gap:'12px',
            gridTemplateColumns:'repeat(auto-fit, minmax(220px, 1fr))'
          }}>
            {memoSections.map((section, index) => (
              <div
                key={`${section.title}-${index}`}
                style={{
                  background:'#F4F6F9',
                  padding:'16px',
                  borderRadius:'6px'
                }}
              >
                <h4 style={{ margin:'0 0 8px', color:'#1B2A4A' }}>
                  {section.title}
                </h4>
                <p style={{ margin:0, color:'#4A5568', whiteSpace:'pre-wrap' }}>
                  {section.content}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

const RiskScore = () => {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [form] = useState({
    application_id:'APP-000001',
    monthly_income:55107,
    requested_loan_amount:390000,
    existing_monthly_emi:0,
    cibil_score:706,
    employment_years:1.0,
    foir:26.48,
    loan_to_income_ratio:0.59,
    is_night_application:0
  })

  const getScore = () => {
    setLoading(true)

    fetchRiskScore(form, form.application_id, 'Medium')
      .then((data) => {
        setResult(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  return (
    <div style={{ padding:'40px', flex:1, background:'#F4F6F9', minHeight:'100vh' }}>
      <h2 style={{ color:'#1B2A4A' }}>Risk Score</h2>

      <div style={{
        background:'white',
        padding:'24px',
        borderRadius:'8px',
        marginTop:'20px',
        maxWidth:'400px',
        boxShadow:'0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <p style={{ color:'#4A5568', fontSize:'13px', marginBottom:'16px' }}>
          Application ID: {form.application_id}
        </p>
        <p style={{ color:'#4A5568', fontSize:'13px' }}>
          Income: Rs {form.monthly_income.toLocaleString()}
        </p>
        <p style={{ color:'#4A5568', fontSize:'13px' }}>
          FOIR: {form.foir}%
        </p>
        <p style={{ color:'#4A5568', fontSize:'13px', marginBottom:'20px' }}>
          CIBIL: {form.cibil_score}
        </p>

        <button
          onClick={getScore}
          style={{
            background:'#1B2A4A',
            color:'white',
            padding:'10px 24px',
            border:'none',
            borderRadius:'6px',
            cursor:'pointer',
            fontSize:'14px'
          }}
        >
          {loading ? 'Scoring...' : 'Get Risk Score'}
        </button>

        {result && (
          <div style={{
            marginTop:'20px',
            padding:'16px',
            background:'#F4F6F9',
            borderRadius:'6px'
          }}>
            <p style={{ margin:'0 0 8px', fontSize:'13px', color:'#4A5568' }}>
              Risk Score
            </p>
            <h2 style={{ margin:'0 0 8px', color:rc(result.risk_tier), fontSize:'36px' }}>
              {formatRiskScore(result.risk_score)}
            </h2>
            <p style={{ margin:0, fontWeight:'bold', color:rc(result.risk_tier) }}>
              {result.risk_tier} Risk
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

const Reports = () => (
  <div style={{
    padding:'40px',
    flex:1,
    background:'#F4F6F9',
    minHeight:'100vh'
  }}>
    <h2 style={{ color:'#1B2A4A' }}>Reports</h2>
    <p style={{ color:'#4A5568' }}>
      Credit memo reports will appear here in Week 2.
    </p>
  </div>
)

function App() {
  return (
    <BrowserRouter>
      <div style={{ display:'flex' }}>
        <div style={nav}>
          <h2 style={{ color:'white' }}>CreditSentinel</h2>
          <Link to="/" style={lnk}>Dashboard</Link>
          <Link to="/applications" style={lnk}>Applications</Link>
          <Link to="/risk" style={lnk}>Risk Score</Link>
          <Link to="/reports" style={lnk}>Reports</Link>
        </div>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/applications" element={<Applications />} />
          <Route path="/application/:id" element={<ApplicationDetail />} />
          <Route path="/risk" element={<RiskScore />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
