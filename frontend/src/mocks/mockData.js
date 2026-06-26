export const mockApplications = [
  {application_id:'APP-000001',
    applicant_name:'Rahul Yadav',
    monthly_income:55107,
    requested_loan_amount:390000,
    foir:26.48, cibil_score:706,
    risk_tier:'Low'},
  {application_id:'APP-000002',
    applicant_name:'Priya Sharma',
    monthly_income:43911,
    requested_loan_amount:150000,
    foir:35.61, cibil_score:573,
    risk_tier:'Medium'},
  {application_id:'APP-000003',
    applicant_name:'Amit Kumar',
    monthly_income:77300,
    requested_loan_amount:170000,
    foir:35.63, cibil_score:680,
    risk_tier:'Low'},
  {application_id:'APP-000004',
    applicant_name:'Sneha Reddy',
    monthly_income:32000,
    requested_loan_amount:500000,
    foir:68.2, cibil_score:471,
    risk_tier:'High'},
  {application_id:'APP-000005',
    applicant_name:'Vikram Singh',
    monthly_income:95000,
    requested_loan_amount:800000,
    foir:42.1, cibil_score:720,
    risk_tier:'Medium'},
]

export const mockRedFlags = {
  'APP-000001': {
    application_id:'APP-000001',
    flag_count:1,
    highest_severity:'High',
    flags:[
      {rule:'GST Filing Gaps',
        evidence:'4 missing quarters',
        severity:'High'}
    ]
  },
  'APP-000002': {
    application_id:'APP-000002',
    flag_count:2,
    highest_severity:'High',
    flags:[
      {rule:'Low CIBIL',
        evidence:'CIBIL score is 573',
        severity:'High'},
      {rule:'Night Application',
        evidence:'Submitted between 11PM and 5AM',
        severity:'Medium'}
    ]
  },
  'APP-000003': {
    application_id:'APP-000003',
    flag_count:3,
    highest_severity:'High',
    flags:[
      {rule:'High Inquiries',
        evidence:'3 inquiries in 30 days',
        severity:'Medium'},
      {rule:'EMI Bounces',
        evidence:'1 bounces',
        severity:'High'},
      {rule:'Income Mismatch',
        evidence:'35.3% mismatch',
        severity:'High'}
    ]
  },
  'APP-000004': {
    application_id:'APP-000004',
    flag_count:2,
    highest_severity:'High',
    flags:[
      {rule:'Low CIBIL',
        evidence:'CIBIL score is 471',
        severity:'High'},
      {rule:'Previous Default',
        evidence:'Previous default found',
        severity:'High'}
    ]
  },
  'APP-000005': {
    application_id:'APP-000005',
    flag_count:3,
    highest_severity:'High',
    flags:[
      {rule:'High FOIR',
        evidence:'FOIR is 67.31%',
        severity:'High'},
      {rule:'Income Mismatch',
        evidence:'115.9% mismatch',
        severity:'High'},
      {rule:'GST Filing Gaps',
        evidence:'8 missing quarters',
        severity:'High'}
    ]
  }
}

export const mockRiskScores = {
  'APP-000001': { risk_score:0.581, risk_tier:'Low' },
  'APP-000002': { risk_score:0.642, risk_tier:'Medium' },
  'APP-000003': { risk_score:0.532, risk_tier:'Low' },
  'APP-000004': { risk_score:0.812, risk_tier:'High' },
  'APP-000005': { risk_score:0.694, risk_tier:'Medium' },
}

export const mockMemos = {
  'APP-000001': {
    application_id:'APP-000001',
    sections:[
      {
        title:'Executive Summary',
        content:'Stable salaried profile with low FOIR and good CIBIL.'
      },
      {
        title:'Income and Obligations',
        content:'Monthly income 55107 with FOIR 26.48%. EMI obligations appear manageable.'
      },
      {
        title:'Red Flags',
        content:'GST filing gaps - 4 missing quarters.'
      },
      {
        title:'Recommendation',
        content:'Approve with standard terms.'
      }
    ]
  },
  'APP-000002': {
    application_id:'APP-000002',
    sections:[
      {
        title:'Executive Summary',
        content:'Moderate risk due to low CIBIL and night application.'
      },
      {
        title:'Red Flags',
        content:'Low CIBIL (573) and submission between 11PM and 5AM.'
      },
      {
        title:'Recommendation',
        content:'Approve with tighter limits and manual verification.'
      }
    ]
  },
  'APP-000003': {
    application_id:'APP-000003',
    sections:[
      {
        title:'Executive Summary',
        content:'Low risk tier with multiple recent concerns.'
      },
      {
        title:'Red Flags',
        content:'High inquiries, EMI bounce, and income mismatch.'
      },
      {
        title:'Recommendation',
        content:'Route for manual review before approval.'
      }
    ]
  },
  'APP-000004': {
    application_id:'APP-000004',
    sections:[
      {
        title:'Executive Summary',
        content:'High risk due to low CIBIL and previous default.'
      },
      {
        title:'Red Flags',
        content:'CIBIL 471 and previous default found.'
      },
      {
        title:'Recommendation',
        content:'Decline or require strong collateral.'
      }
    ]
  },
  'APP-000005': {
    application_id:'APP-000005',
    sections:[
      {
        title:'Executive Summary',
        content:'Medium risk with high FOIR and income mismatch.'
      },
      {
        title:'Red Flags',
        content:'FOIR 67.31%, income mismatch 115.9%, GST filing gaps.'
      },
      {
        title:'Recommendation',
        content:'Approve with conditions and tighter monitoring.'
      }
    ]
  }
}

export const defaultMockMemo = {
  application_id:'UNKNOWN',
  sections:[
    {
      title:'Executive Summary',
      content:'Memo data not available. Using fallback template.'
    },
    {
      title:'Recommendation',
      content:'Request updated data from the memo service.'
    }
  ]
}

export const mockHistories = {
  'APP-000001': [
    {
      audit_id: 101,
      decision: 'APPROVE',
      notes: 'Strong credit history, CIBIL score is excellent.',
      timestamp: '2026-06-25T14:30:00.000Z',
      applicant_name: 'Rahul Yadav',
      analyst_name: 'Divya',
      application_date: '2026-06-25',
      decision_date: '2026-06-25T14:30:00.000Z',
      submitted_at: '2026-06-25',
      latency_ms: 150
    },
    {
      audit_id: 100,
      decision: 'REVIEW',
      notes: 'Initial check, reviewing income files.',
      timestamp: '2026-06-24T09:15:00.000Z',
      applicant_name: 'Rahul Yadav',
      analyst_name: 'Guru Prasad',
      application_date: '2026-06-24',
      decision_date: '2026-06-24T09:15:00.000Z',
      submitted_at: '2026-06-24',
      latency_ms: 2200
    }
  ],
  'APP-000002': [
    {
      audit_id: 201,
      decision: 'APPROVE',
      notes: 'Lower limit approved after verifying night application context.',
      timestamp: '2026-06-24T16:45:00.000Z',
      applicant_name: 'Priya Sharma',
      analyst_name: 'Guru Prasad',
      application_date: '2026-06-24',
      decision_date: '2026-06-24T16:45:00.000Z',
      submitted_at: '2026-06-24',
      latency_ms: 2500
    },
    {
      audit_id: 200,
      decision: 'REVIEW',
      notes: 'Low CIBIL score flagged. Needs detailed underwriting.',
      timestamp: '2026-06-23T11:00:00.000Z',
      applicant_name: 'Priya Sharma',
      analyst_name: 'Divya',
      application_date: '2026-06-23',
      decision_date: '2026-06-23T11:00:00.000Z',
      submitted_at: '2026-06-23',
      latency_ms: 800
    }
  ],
  'APP-000003': [
    {
      audit_id: 300,
      decision: 'APPROVE',
      notes: 'Standard approval granted. Income matching passed manual checks.',
      timestamp: '2026-06-23T10:30:00.000Z',
      applicant_name: 'Amit Kumar',
      analyst_name: 'Yuva Teja',
      application_date: '2026-06-23',
      decision_date: '2026-06-23T10:30:00.000Z',
      submitted_at: '2026-06-23',
      latency_ms: 450
    }
  ],
  'APP-000004': [
    {
      audit_id: 400,
      decision: 'REJECT',
      notes: 'Previous default found along with low CIBIL score of 471.',
      timestamp: '2026-06-22T15:20:00.000Z',
      applicant_name: 'Sneha Reddy',
      analyst_name: 'Guru Prasad',
      application_date: '2026-06-22',
      decision_date: '2026-06-22T15:20:00.000Z',
      submitted_at: '2026-06-22',
      latency_ms: 3100
    }
  ],
  'APP-000005': [
    {
      audit_id: 500,
      decision: 'REVIEW',
      notes: 'High FOIR (67.31%) and income mismatch. Escalating for higher authority review.',
      timestamp: '2026-06-21T08:50:00.000Z',
      applicant_name: 'Vikram Singh',
      analyst_name: 'Divya',
      application_date: '2026-06-21',
      decision_date: '2026-06-21T08:50:00.000Z',
      submitted_at: '2026-06-21',
      latency_ms: 1200
    }
  ]
}

