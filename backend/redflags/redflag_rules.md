# Red Flag Detection Engine

## Rule 1 — High FOIR
Trigger: FOIR above 60%
Severity: High
Evidence format: "FOIR is XX%"

## Rule 2 — Low CIBIL
Trigger: CIBIL score below 650
Severity: High
Evidence format: "CIBIL score is XXX"

## Rule 3 — High Inquiry Velocity
Trigger: 3 or more credit inquiries in 30 days
Severity: Medium
Evidence format: "X inquiries in 30 days"

## Rule 4 — Loan Exceeds 5x Income
Trigger: Loan amount exceeds 5x annual income
Severity: High
Evidence format: "Loan is X.x times annual income"

## Rule 5 — Previous Default
Trigger: Previous loan default exists
Severity: High
Evidence format: "Previous default found"

## Rule 6 — Night Application
Trigger: Application submitted between 11PM and 5AM
Severity: Medium
Evidence format: "Submitted during night hours"

## Rule 7 — EMI Bounce History
Trigger: EMI bounces greater than 0
Severity: High
Evidence format: "X EMI bounces"

## Rule 8 — Income Mismatch
Trigger: Bank credits vs declared income mismatch > 25%
Severity: High
Evidence format: "XX% mismatch"

## Rule 9 — GST Filing Gaps
Trigger: Self-employed applicant with 2+ missing GST quarters
Severity: High
Evidence format: "X missing GST quarters"

## Rule 10 — Short Employment + High FOIR
Trigger: Employment below 1 year and FOIR above 50%
Severity: High
Evidence format: "X years employment with FOIR XX%"