import React, { useState, useEffect } from 'react';
import { API_CONFIG } from '../api/config'
const DecisionPanel = ({ applicationId, onDecision }) => {
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(true)
  const maxChars = 500;


  const handleNotesChange = (e) => {
    if (e.target.value.length <= maxChars) {
      setNotes(e.target.value);
    }
  };

  const handleDecision = async (decision) => {
  try {
    setLoading(true)

    const response = await fetch(
      `${API_CONFIG.APPLICATIONS_API}/api/applications/${applicationId}/decision`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          decision,
          notes,
          timestamp: new Date().toISOString()
        })
      }
    )

    if (!response.ok) {
      throw new Error('Failed to submit decision')
    }

    alert('Decision submitted successfully')
    fetchHistory()
  } catch (err) {
    alert(err.message)
  } finally {
    setLoading(false)
  }
}
const fetchHistory = async () => {
  try {
    setHistoryLoading(true)

    const response = await fetch(
      `${API_CONFIG.APPLICATIONS_API}/api/applications/${applicationId}/history`
    )

    const data = await response.json()

    setHistory(data.history || [])
  } catch (err) {
    console.error(err)
  } finally {
    setHistoryLoading(false)
  }
}
console.log("Current Applicant:", applicationId)
useEffect(() => {
  fetchHistory()
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [applicationId])
  return (
    <div
      style={{
        background: '#fff',
        padding: '24px',
        borderRadius: '8px',
        marginTop: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}
    >
      <h2 style={{ color: '#1B2A4A' }}>Decision Panel</h2>

      <textarea
        value={notes}
        onChange={handleNotesChange}
        placeholder="Enter analyst notes..."
        rows={5}
        style={{
          width: '100%',
          padding: '12px',
          borderRadius: '6px',
          border: '1px solid #ccc',
          resize: 'vertical',
          marginTop: '10px',
        }}
      />
       
      <div
        style={{
          textAlign: 'right',
          marginTop: '6px',
          color: '#666',
          fontSize: '12px',
        }}
      >
        {notes.length}/{maxChars}
      </div>

      <div
        style={{
          display: 'flex',
          gap: '12px',
          marginTop: '20px',
        }}
      >
        <button
  disabled={loading}
  onClick={() => handleDecision('Approve')}
  style={{
    background: '#28a745',
    color: '#fff',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    cursor: loading ? 'not-allowed' : 'pointer',
    opacity: loading ? 0.6 : 1
  }}
>
  {loading ? 'Submitting...' : 'APPROVE'}
</button>

<button
  disabled={loading}
  onClick={() => handleDecision('Review')}
  style={{
    background: '#ffc107',
    color: '#000',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    cursor: loading ? 'not-allowed' : 'pointer',
    opacity: loading ? 0.6 : 1
  }}
>
  {loading ? 'Submitting...' : 'REVIEW'}
</button>

<button
  disabled={loading}
  onClick={() => handleDecision('Reject')}
  style={{
    background: '#dc3545',
    color: '#fff',
    border: 'none',
    padding: '10px 18px',
    borderRadius: '6px',
    cursor: loading ? 'not-allowed' : 'pointer',
    opacity: loading ? 0.6 : 1
  }}
>
  {loading ? 'Submitting...' : 'REJECT'}
</button>
  </div>

      <hr style={{ margin: '20px 0' }} />

      <h3>Decision History</h3>

      {historyLoading ? (
        <p>Loading...</p>
      ) : history.length === 0 ? (
        <p>No decision yet</p>
      ) : (
        <div>
          {history.map((item) => (
            <div
              key={item.audit_id}
              style={{
                border: '1px solid #ddd',
                padding: '10px',
                borderRadius: '6px',
                marginBottom: '10px'
              }}
            >
              <strong>{item.decision}</strong>

              <div>
                {new Date(item.timestamp).toLocaleString()}
              </div>

              {item.notes && (
                <div>
                  Notes: {item.notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

 </div>
);
};

export default DecisionPanel;
