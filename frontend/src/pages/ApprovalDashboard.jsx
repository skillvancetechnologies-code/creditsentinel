import React, { useEffect, useState } from 'react';
import { API_CONFIG } from '../api/config';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import html2canvas from 'html2canvas';
import {
  mockApplications,
  mockHistories
} from '../mocks/mockData';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart,
  Bar
} from 'recharts';

const ApprovalDashboard = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');

  const [searchTerm, setSearchTerm] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [history, setHistory] = useState([]);
  const [selectedApp, setSelectedApp] = useState(null);
  const [emailReport, setEmailReport] = useState(false);
  const [emailTo, setEmailTo] = useState('');
  const [latencyMs, setLatencyMs] = useState('');
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Analyst filtering and latency tracking state
  const [allDecisions, setAllDecisions] = useState([]);
  const [allDecisionsLoading, setAllDecisionsLoading] = useState(true);
  const [analystFilter, setAnalystFilter] = useState('All');
  const [simulateHighLatency, setSimulateHighLatency] = useState(false);

  const trendData = [
    { day: 'Mon', approvals: 12 },
    { day: 'Tue', approvals: 18 },
    { day: 'Wed', approvals: 15 },
    { day: 'Thu', approvals: 22 },
    { day: 'Fri', approvals: 20 },
    { day: 'Sat', approvals: 10 },
    { day: 'Sun', approvals: 14 }
  ];

  useEffect(() => {
    fetchApplications();
  }, []);

  useEffect(() => {
    if (applications.length > 0) {
      fetchAllHistories();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [applications]);

  const fetchApplications = async () => {
    try {
      if (API_CONFIG.USE_MOCK) {
        setApplications(mockApplications);
        setLastUpdated(new Date());
        return;
      }
      const response = await fetch(
        `${API_CONFIG.APPLICATIONS_API}/api/applications?limit=100&offset=0`
      );
      const data = await response.json();
      setApplications(data.applications || []);
      setLastUpdated(new Date());
    } catch (err) {
      console.warn("Failed to fetch applications, using mock:", err);
      setApplications(mockApplications);
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (applicationId) => {
    try {
      if (API_CONFIG.USE_MOCK) {
        const mockH = mockHistories[applicationId] || [];
        setHistory(mockH);
        setEmailReport(true);
        setEmailTo('mock@example.com');
        setLatencyMs(mockH.length > 0 ? mockH[0].latency_ms : 100);
        setSelectedApp(applicationId);
        return;
      }
      const response = await fetch(
        `${API_CONFIG.APPLICATIONS_API}/api/applications/${applicationId}/history`
      );

      const data = await response.json();
      setHistory(data.history || []);
      setEmailReport(data.email_report);
      setEmailTo(data.email_to);
      setLatencyMs(data.latency_ms);
      setSelectedApp(applicationId);
    } catch (err) {
      console.warn("Failed to fetch history, using mock:", err);
      const mockH = mockHistories[applicationId] || [];
      setHistory(mockH);
      setEmailReport(true);
      setEmailTo('mock@example.com');
      setLatencyMs(mockH.length > 0 ? mockH[0].latency_ms : 100);
      setSelectedApp(applicationId);
    }
  };

  const fetchAllHistories = async () => {
    setAllDecisionsLoading(true);
    try {
      const historiesList = await Promise.all(
        applications.map(async (app) => {
          if (API_CONFIG.USE_MOCK) {
            const h = mockHistories[app.application_id] || [];
            return h.map(item => ({
              ...item,
              application_id: app.application_id,
              applicant_name: app.applicant_name,
              loan_amount: app.loan_amount
            }));
          }

          try {
            const response = await fetch(
              `${API_CONFIG.APPLICATIONS_API}/api/applications/${app.application_id}/history`
            );
            if (!response.ok) throw new Error("HTTP error");
            const data = await response.json();
            return (data.history || []).map(item => ({
              ...item,
              application_id: app.application_id,
              applicant_name: app.applicant_name,
              loan_amount: app.loan_amount
            }));
          } catch (err) {
            console.warn(`Failed to fetch history for ${app.application_id}, using mock:`, err);
            const h = mockHistories[app.application_id] || [];
            return h.map(item => ({
              ...item,
              application_id: app.application_id,
              applicant_name: app.applicant_name,
              loan_amount: app.loan_amount
            }));
          }
        })
      );
      const flatDecisions = historiesList.flat();
      setAllDecisions(flatDecisions);
    } catch (err) {
      console.error("Error in fetchAllHistories:", err);
    } finally {
      setAllDecisionsLoading(false);
    }
  };

  const calculatePercentile = (values, percentile) => {
    if (!values || values.length === 0) return 0;
    const sorted = [...values].sort((a, b) => a - b);
    const index = (percentile / 100) * (sorted.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index - lower;
    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
  };

  const totalApplications = applications.length;

  const approvedCount = applications.filter(
    app => app.application_status === 'Approved'
  ).length;

  const rejectedCount = applications.filter(
    app => app.application_status === 'Rejected'
  ).length;

  const reviewCount = applications.filter(
    app => app.application_status === 'Under Review'
  ).length;

  const approvalRate =
    totalApplications > 0
      ? ((approvedCount / totalApplications) * 100).toFixed(1)
      : 0;

  const rejectionRate =
    totalApplications > 0
      ? ((rejectedCount / totalApplications) * 100).toFixed(1)
      : 0;

  const reviewRate =
    totalApplications > 0
      ? ((reviewCount / totalApplications) * 100).toFixed(1)
      : 0;

  const approvalDropAlert = Number(approvalRate) < 40;
  const rejectionSpikeAlert = Number(rejectionRate) > 25;

  // Analyst decisions filtering
  const analystDecisions = allDecisions.filter(d => analystFilter === 'All' || d.analyst_name === analystFilter);
  const analystTotal = analystDecisions.length;
  const analystApproved = analystDecisions.filter(d => d.decision.toUpperCase() === 'APPROVE' || d.decision.toUpperCase() === 'APPROVED').length;
  const analystRejected = analystDecisions.filter(d => d.decision.toUpperCase() === 'REJECT' || d.decision.toUpperCase() === 'REJECTED').length;
  const analystRate = analystTotal > 0 ? ((analystApproved / analystTotal) * 100).toFixed(1) : '0.0';

  // Global latency alert: when avg latency > 2 seconds (filtered by selected analyst)
  const allLatencies = analystDecisions.map(d => Number(d.latency_ms || 0));
  let avgLatencyMs = allLatencies.length > 0 
    ? allLatencies.reduce((sum, l) => sum + l, 0) / allLatencies.length
    : 0;
  if (simulateHighLatency) {
    avgLatencyMs += 2500;
  }
  const latencyAlert = avgLatencyMs > 2000;

  const displayLatencies = allLatencies.map(l => simulateHighLatency ? l + 2500 : l);
  const p50 = calculatePercentile(displayLatencies, 50);
  const p95 = calculatePercentile(displayLatencies, 95);
  const p99 = calculatePercentile(displayLatencies, 99);

  // unique analyst names list
  const uniqueAnalysts = Array.from(new Set(allDecisions.map(d => d.analyst_name).filter(Boolean)));

  const pieData = [
    { name: 'Approved', value: approvedCount },
    { name: 'Rejected', value: rejectedCount },
    { name: 'Under Review', value: reviewCount }
  ];

  const COLORS = ['#28a745', '#dc3545', '#ffc107'];

  const lowRiskCount = applications.filter(
    app => app.risk_tier === 'Low'
  ).length;

  const mediumRiskCount = applications.filter(
    app => app.risk_tier === 'Medium'
  ).length;

  const highRiskCount = applications.filter(
    app => app.risk_tier === 'High'
  ).length;

  const riskData = [
    { risk: 'Low', count: lowRiskCount },
    { risk: 'Medium', count: mediumRiskCount },
    { risk: 'High', count: highRiskCount }
  ];

  // 7-day latency trend grouping (filtered by selected analyst)
  const get7DayLatencyTrend = () => {
    let baseline = new Date();
    const analystDecs = allDecisions.filter(d => analystFilter === 'All' || d.analyst_name === analystFilter);

    if (analystDecs.length > 0) {
      const timestamps = analystDecs.map(d => new Date(d.timestamp).getTime());
      const maxTime = Math.max(...timestamps);
      baseline = new Date(maxTime);
    }

    const trendList = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(baseline);
      d.setDate(d.getDate() - i);
      const dateStr = d.toISOString().split('T')[0];
      
      const dailyDecisions = analystDecs.filter(dec => {
        const decDateStr = new Date(dec.timestamp).toISOString().split('T')[0];
        return decDateStr === dateStr;
      });

      const avgDaily = dailyDecisions.length > 0
        ? dailyDecisions.reduce((sum, dec) => sum + Number(dec.latency_ms || 0), 0) / dailyDecisions.length
        : 0;

      const displayDaily = simulateHighLatency ? avgDaily + 2500 : avgDaily;
      const label = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

      trendList.push({
        date: dateStr,
        label,
        avgLatencyMs: Math.round(displayDaily),
        count: dailyDecisions.length
      });
    }
    return trendList;
  };

  const trend7Days = get7DayLatencyTrend();

  const filteredApplications = applications.filter((app) => {
    const matchesStatus =
      statusFilter === 'All' ||
      app.application_status === statusFilter;
    const matchesRisk =
      riskFilter === 'All' ||
      app.risk_tier === riskFilter;
    const applicationDate = app.created_at;

    const matchesFromDate =
      !fromDate || applicationDate >= fromDate;

    const matchesToDate =
      !toDate || applicationDate <= toDate;
    const matchesSearch =
      app.applicant_name
        .toLowerCase()
        .includes(searchTerm.toLowerCase());

    const matchesAnalyst =
      analystFilter === 'All' ||
      allDecisions.some(
        d => d.application_id === app.application_id && d.analyst_name === analystFilter
      );

    return (
      matchesStatus &&
      matchesSearch &&
      matchesRisk &&
      matchesFromDate &&
      matchesToDate &&
      matchesAnalyst
    );
  });
const exportCSV = async () => {
  const headers = [
  'Application ID',
  'Applicant Name',
  'Loan Amount',
  'Status',
  'Decision History',
  'Approval Reason'
];
  
 const rows = filteredApplications.map((app) => [
  app.application_id,
  app.applicant_name,
  app.loan_amount,
  app.application_status,
  'Available in History View',
  'Available in History View'
]);

  const csvContent =
    [headers, ...rows]
      .map((row) => row.join(','))
      .join('\n');

  const blob = new Blob(
    [csvContent],
    { type: 'text/csv;charset=utf-8;' }
  );

  const link = document.createElement('a');

  link.href = URL.createObjectURL(blob);

  link.download = 'approval_dashboard.csv';

  link.click();
};
    
const exportPNG = async () => {
  const dashboard = document.getElementById('charts-section');
console.log(document.getElementById('charts-section'));
  const canvas = await html2canvas(dashboard);

  const link = document.createElement('a');
  link.download = 'dashboard_charts.png';
  link.href = canvas.toDataURL();
  link.click();
};

const exportPDF = async () => {
  const doc = new jsPDF();
  const charts = document.getElementById('charts-section');

const canvas = await html2canvas(charts);

const chartImage = canvas.toDataURL('image/png');

  doc.setFontSize(18);
  doc.text('Loan Approval Report', 14, 20);

  doc.setFontSize(12);
  doc.text(`Total Applications: ${totalApplications}`, 14, 35);
  doc.text(`Approved: ${approvedCount}`, 14, 45);
  doc.text(`Rejected: ${rejectedCount}`, 14, 55);
  doc.text(`Under Review: ${reviewCount}`, 14, 65);
  doc.text(`Approval Rate: ${approvalRate}%`, 14, 75);
 doc.addImage(
  chartImage,
  'PNG',
  5,
  80,
  200,
  120
);
  autoTable(doc, {
   startY: 210,
    head: [[
      'Application ID',
      'Applicant',
      'Loan Amount',
      'Status',
       'Decision Date'
    ]],
    body: filteredApplications.map(app => [
      app.application_id,
      app.applicant_name,
      app.loan_amount,
      app.application_status,
      app.decision_date || '-'
    ])
  });

  doc.save('approval-report.pdf');
};
  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '20px' }}>
        Loan Approval Dashboard
      </h1>
       <p style={{ color: '#666' }}>
  Last Updated: {lastUpdated.toLocaleTimeString()}
</p>
      {loading ? (
        <p>Loading dashboard...</p>
      ) : (
        <>
          <div
            style={{
              display: 'grid',
             gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '16px',
              marginTop: '20px'
            }}
          >
            <div
              style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
              }}
            >
              <h3>Total Applications</h3>
              <h1>{totalApplications}</h1>
            </div>

            <div
              style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
              }}
            >
              <h3>Approved</h3>
<h1 style={{ color: '#28a745' }}>
  {approvedCount}
</h1>
<p>{approvalRate}%</p>
            </div>

            <div
              style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
              }}
            >
              <h3>Rejected</h3>
<h1 style={{ color: '#dc3545' }}>
  {rejectedCount}
</h1>
<p>{rejectionRate}%</p>
            </div>

            <div
              style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
              }}
            >
              <h3>Under Review</h3>
<h1 style={{ color: '#ffc107' }}>
  {reviewCount}
</h1>
<p>{reviewRate}%</p>
            </div>
             
            <div
              style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
              }}
            >
              <h3>Today's Decisions</h3>
              <h1 style={{ color: '#007bff' }}>
                {approvedCount + rejectedCount + reviewCount}
              </h1>
            </div>

            <div
              style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
              }}
            >
              <h3>Analyst: {analystFilter}</h3>
              {allDecisionsLoading ? (
                <p style={{ margin: 0, fontSize: '14px', color: '#888' }}>Loading decisions...</p>
              ) : (
                <>
                  <h1 style={{ color: Number(analystRate) >= 50 ? '#28a745' : '#dc3545' }}>
                    {analystRate}%
                  </h1>
                  <p style={{ margin: 0, fontSize: '13px', color: '#666' }}>
                    Approved: {analystApproved} / {analystTotal} Decisions
                  </p>
                  <p style={{ margin: 0, fontSize: '13px', color: '#dc3545' }}>
                    Rejected: {analystRejected}
                  </p>
                </>
              )}
            </div>
          </div>
          <div id="charts-section">
<h2 style={{ marginTop: '40px' }}>
  Weekly Approval Trend
</h2>
{approvalDropAlert && (
  <div
    style={{
      background: '#fff3cd',
      color: '#856404',
      padding: '12px',
      borderRadius: '6px',
      marginTop: '20px',
      marginBottom: '10px',
      border: '1px solid #ffeeba'
    }}
  >
    ⚠ Alert: Approval rate below target (37%)
  </div>
)}

{rejectionSpikeAlert && (
  <div
    style={{
      background: '#f8d7da',
      color: '#721c24',
      padding: '12px',
      borderRadius: '6px',
      marginBottom: '10px',
      border: '1px solid #f5c6cb'
    }}
  >
    ⚠ Alert:  Rejection rate above target (30%)
  </div>
  
)}
{latencyAlert && (
  <div
    style={{
      background: '#ffe6e6',
      color: '#b00020',
      padding: '12px',
      borderRadius: '6px',
      marginBottom: '10px',
      border: '1px solid #ffb3b3',
      fontWeight: 'bold'
    }}
  >
    ⚠ High Processing Latency Detected (Avg Latency: {(avgLatencyMs / 1000).toFixed(2)}s)
  </div>
)}
<div
  style={{
    background: '#fff',
    padding: '20px',
    borderRadius: '8px',
    marginTop: '20px',
    marginBottom: '40px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
  }}
>
  <ResponsiveContainer width={800} height={300}>
    <LineChart data={trendData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="day" />
      <YAxis />
      <Tooltip />
      <Line
        type="monotone"
        dataKey="approvals"
      />
    </LineChart>
  </ResponsiveContainer>
</div>
         <div
  style={{
    display: 'block'
  }}
>
<h2 style={{ marginTop: '40px' }}>
  Decision Status Distribution
</h2>

<div
  style={{
    background: '#fff',
    padding: '20px',
    borderRadius: '8px',
    marginTop: '20px',
    marginBottom: '40px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
  }}
>
  <ResponsiveContainer width={800} height={300}>
    <PieChart>
     <Pie
  data={pieData}
  dataKey="value"
  cx="50%"
  cy="50%"
  outerRadius={100}
  label
  onClick={(data) => setStatusFilter(data.name)}
>
        {pieData.map((entry, index) => (
          <Cell
            key={`cell-${index}`}
            fill={COLORS[index % COLORS.length]}
          />
        ))}
      </Pie>

      <Tooltip />
      <Legend />
    </PieChart>
  </ResponsiveContainer>
</div>

<h2 style={{ marginTop: '40px' }}>
  Risk Score Distribution
</h2>

<div
  style={{
    background: '#fff',
    padding: '20px',
    borderRadius: '8px',
    marginTop: '20px',
    marginBottom: '40px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
  }}
>
  <ResponsiveContainer width={800} height={300}>

    <BarChart data={riskData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="risk" />
      <YAxis />
      <Tooltip />
     <Bar
  dataKey="count"
  fill="#007bff"
  onClick={(data) => setRiskFilter(data.risk)}
/>
    </BarChart>
  </ResponsiveContainer>
</div>
</div> 
<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '40px' }}>
  <h2>Latency Trend (7-Day Avg)</h2>
  <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', background: '#e2e8f0', padding: '6px 12px', borderRadius: '20px', fontSize: '14px' }}>
    <input
      type="checkbox"
      checked={simulateHighLatency}
      onChange={(e) => setSimulateHighLatency(e.target.checked)}
      style={{ cursor: 'pointer' }}
    />
    <span>Simulate High Latency (> 2s)</span>
  </label>
</div>

<div
  style={{
    background: '#fff',
    padding: '20px',
    borderRadius: '8px',
    marginTop: '20px',
    marginBottom: '20px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
  }}
>
  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={trend7Days}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="label" />
      <YAxis label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft' }} />
      <Tooltip formatter={(value) => [`${value} ms`, 'Avg Latency']} />
      <Line
        type="monotone"
        dataKey="avgLatencyMs"
        stroke="#ff7300"
        strokeWidth={3}
        activeDot={{ r: 8 }}
      />
    </LineChart>
  </ResponsiveContainer>
</div>

<div
  style={{
    background: '#fff',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '40px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
  }}
>
  <h3 style={{ margin: '0 0 15px 0' }}>Latency Percentiles</h3>
  <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: '15px' }}>
    <div style={{ textAlign: 'center', flex: 1, minWidth: '100px' }}>
      <p style={{ margin: '0 0 5px 0', color: '#666', fontSize: '13px' }}>Median (p50)</p>
      <h2 style={{ margin: 0, color: '#333' }}>{Math.round(p50)} ms</h2>
    </div>
    <div style={{ textAlign: 'center', flex: 1, minWidth: '100px', borderLeft: '1px solid #eee', borderRight: '1px solid #eee' }}>
      <p style={{ margin: '0 0 5px 0', color: '#666', fontSize: '13px' }}>95th Percentile (p95)</p>
      <h2 style={{ margin: 0, color: '#ff7300' }}>{Math.round(p95)} ms</h2>
    </div>
    <div style={{ textAlign: 'center', flex: 1, minWidth: '100px' }}>
      <p style={{ margin: '0 0 5px 0', color: '#666', fontSize: '13px' }}>99th Percentile (p99)</p>
      <h2 style={{ margin: 0, color: '#dc3545' }}>{Math.round(p99)} ms</h2>
    </div>
  </div>
</div>
 <div
  style={{
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '20px'
  }}
>
  <h2>Applications by Status</h2>

  <div>
    <button
      aria-label="Export applications as CSV"
      onClick={exportCSV}
      style={{
        background: '#28a745',
        color: '#fff',
        border: 'none',
        padding: '10px 16px',
        borderRadius: '6px',
        cursor: 'pointer'
      }}
    >
      Export CSV
    </button>
     <button
  onClick={exportPNG}
  style={{
    background: '#007bff',
    color: '#fff',
    border: 'none',
    padding: '10px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
    marginLeft: '10px'
  }}
>
  Export PNG
</button>
    <button
      aria-label="Export applications as PDF"
      onClick={exportPDF}
      style={{
        background: '#dc3545',
        color: '#fff',
        border: 'none',
        padding: '10px 16px',
        borderRadius: '6px',
        cursor: 'pointer',
        marginLeft: '10px'
      }}
    >
      Export PDF
    </button>
  </div>
</div>
  
</div>
<div
  style={{
    display: 'flex',
    gap: '10px',
    marginTop: '15px',
    marginBottom: '15px'
  }}
>

</div>
<input
  aria-label="Search applicant name"
  type="text"
  placeholder="Search applicant name..."
  value={searchTerm}
  onChange={(e) => setSearchTerm(e.target.value)}
  style={{
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #ccc',
    marginRight: '10px',
    width: '250px'
  }}
/>

<div style={{ marginTop: '15px' }}>
  <select
  aria-label="Filter applications by status"
    value={statusFilter}
    onChange={(e) => setStatusFilter(e.target.value)}
    style={{
      padding: '10px',
      borderRadius: '6px',
      border: '1px solid #ccc'
    }}
  >
    <option value="All">All Statuses</option>
    <option value="Approved">Approved</option>
    <option value="Rejected">Rejected</option>
    <option value="Under Review">Under Review</option>
  </select>
</div>
<div style={{ marginTop: '15px' }}>
  <select
    aria-label="Filter by risk score band"
    value={riskFilter}
    onChange={(e) => setRiskFilter(e.target.value)}
    style={{
      padding: '10px',
      borderRadius: '6px',
      border: '1px solid #ccc'
    }}
  >
    <option value="All">All Risk Bands</option>
    <option value="Low">Low</option>
    <option value="Medium">Medium</option>
    <option value="High">High</option>
  </select>
</div>

<div style={{ marginTop: '15px' }}>
  <select
    aria-label="Filter by analyst"
    value={analystFilter}
    onChange={(e) => setAnalystFilter(e.target.value)}
    style={{
      padding: '10px',
      borderRadius: '6px',
      border: '1px solid #ccc'
    }}
  >
    <option value="All">All Analysts</option>
    {uniqueAnalysts.map(analyst => (
      <option key={analyst} value={analyst}>{analyst}</option>
    ))}
  </select>
</div>
<div style={{ marginTop: '10px' }}>
  <label><strong>From Date</strong></label>
  <br />
  <input
    type="date"
    value={fromDate}
    onChange={(e) => setFromDate(e.target.value)}
    style={{ padding: '8px', width: '180px' }}
  />
</div>

<div style={{ marginTop: '10px' }}>
  <label><strong>To Date</strong></label>
  <br />
  <input
    type="date"
    value={toDate}
    onChange={(e) => setToDate(e.target.value)}
    style={{ padding: '8px', width: '180px' }}
  />
</div>
          <div
           style={{
  background: '#fff',
  padding: '20px',
  borderRadius: '8px',
  marginTop: '20px',
  boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
  overflowX: 'auto'
}}
          >
            <table
              style={{
  width: '100%',
  minWidth: '900px',
  borderCollapse: 'collapse'
}}
            >
              <thead>
                <tr
                  style={{
                    borderBottom: '2px solid #ddd'
                  }}
                >
                  <th style={{ padding: '10px', textAlign: 'left' }}>
                    Application ID
                  </th>

                  <th style={{ padding: '10px', textAlign: 'left' }}>
                    Applicant
                  </th>

                  <th style={{ padding: '10px', textAlign: 'left' }}>
                    Loan Amount
                  </th>

                  <th style={{ padding: '10px', textAlign: 'left' }}>
                    Status
                  </th>

                  <th style={{ padding: '10px', textAlign: 'left' }}>
                    Decision Date
                  </th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>
  Actions
</th>
                </tr>
              </thead>

              <tbody>
  {filteredApplications.map((app) => (
                  <tr key={app.application_id}>
                    <td style={{ padding: '10px' }}>
                      {app.application_id}
                    </td>
                     
                    <td style={{ padding: '10px' }}>
                      {app.applicant_name}
                    </td>

                    <td style={{ padding: '10px' }}>
                      ₹{(app.loan_amount ?? app.requested_loan_amount ?? 0).toLocaleString()}
                    </td>

                    <td
                      style={{
                        padding: '10px',
                        color:
                          app.application_status === 'Approved'
                            ? '#28a745'
                            : app.application_status === 'Rejected'
                            ? '#dc3545'
                            : '#ffc107'
                      }}
                    >
                      {app.application_status}
                    </td>
                     
                    <td style={{ padding: '10px' }}>
                      {(() => {
                        const appDecs = allDecisions.filter(d => d.application_id === app.application_id);
                        if (appDecs.length === 0) return '-';
                        const sorted = [...appDecs].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                        return new Date(sorted[0].timestamp).toLocaleDateString();
                      })()}
                    </td>
                    <td style={{ padding: '10px' }}>
  <button
  onClick={() => fetchHistory(app.application_id)}
    style={{
      padding: '6px 12px',
      border: 'none',
      borderRadius: '4px',
      background: '#007bff',
      color: '#fff',
      cursor: 'pointer'
    }}
  >
    View History
  </button>
</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {selectedApp && (
  <div style={{ marginTop: '30px' }}>
    <h3>Decision History - {selectedApp}</h3>

    {history.length === 0 ? (
      <p>No history found</p>
    ) : (
      history.map((item) => (
        <div
          key={item.audit_id}
          style={{
            border: '1px solid #ddd',
            padding: '12px',
            marginBottom: '10px',
            borderRadius: '6px'
          }}
        >
          <strong>{item.decision}</strong>

          <div>
            {new Date(item.timestamp).toLocaleString()}
          </div>
          <div><strong>Analyst:</strong> {item.analyst_name}</div>

<div><strong>Application Date:</strong> {new Date(item.application_date).toLocaleDateString()}</div>

<div><strong>Decision Date:</strong> {new Date(item.decision_date).toLocaleString()}</div>

<div><strong>Submitted At:</strong> {new Date(item.submitted_at).toLocaleDateString()}</div>

<div><strong>Email Report:</strong> {emailReport ? 'Yes' : 'No'}</div>

<div><strong>Email:</strong> {emailTo}</div>

<div><strong>Latency:</strong> {Number(item.latency_ms !== undefined ? item.latency_ms : latencyMs).toFixed(2)} ms</div>
          {item.notes && (
            <div>
              Notes: {item.notes}
            </div>
          )}
        </div>
      ))
    )}
  </div>
)}
          </div>
        </>
      )}
    </div>
  );
};

export default ApprovalDashboard;