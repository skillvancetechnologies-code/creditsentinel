# Red Flag Rule Documentation

## Rule 1 — Low CIBIL Score

Rule ID: RF001

Condition:
IF CIBIL Score < 600

Evidence:
Current CIBIL Score

Rationale:
Low credit scores indicate elevated repayment risk.

Threshold Justification:
600 is commonly used as a high-risk threshold.

---

## Rule 2 — High FOIR

Rule ID: RF002

Condition:
IF FOIR > 60%

Evidence:
Current FOIR Percentage

Rationale:
High debt obligations reduce repayment capacity.

Threshold Justification:
FOIR above 60% is considered financially stressed.

---

## Rule 3 — High Credit Inquiries

Rule ID: RF003

Condition:
IF Credit Inquiries >= 3 in 30 Days

Evidence:
Inquiry Count

Rationale:
Frequent credit seeking may indicate financial distress.

Threshold Justification:
3+ inquiries within a short period is considered elevated risk.

---

## Rule 4 — EMI Bounce History

Rule ID: RF004

Condition:
IF EMI Bounces >= 1

Evidence:
Bounce Count

Rationale:
Missed payments are strong indicators of repayment risk.

Threshold Justification:
Any recent bounce indicates potential financial instability.

---

## Rule 5 — GST Filing Gaps

Rule ID: RF005

Condition:
IF Missing GST Quarters >= 4

Evidence:
Missing Quarter Count

Rationale:
Missing filings may indicate business instability.

Threshold Justification:
Four missing quarters represent a prolonged compliance gap.

---

## Rule 6 — Income Mismatch

Rule ID: RF006

Condition:
IF Income Mismatch > 25%

Evidence:
Income Difference Percentage

Rationale:
Large discrepancies may indicate inaccurate declarations.

Threshold Justification:
25% difference is materially significant.

---

## Rule 7 — Night Application

Rule ID: RF007

Condition:
IF Application Submitted During Night Hours

Evidence:
Application Timestamp

Rationale:
Night-time activity may indicate unusual behavior patterns.

Threshold Justification:
Used as a supplemental behavioral indicator.

---

## Rule 8 — Previous Defaults

Rule ID: RF008

Condition:
IF Previous Default Exists

Evidence:
Default History

Rationale:
Past defaults strongly correlate with future repayment risk.

Threshold Justification:
Any recorded default increases risk.

---

## Rule 9 — Low Bank Balance

Rule ID: RF009

Condition:
IF Average Bank Balance < 10,000

Evidence:
Average Balance

Rationale:
Low liquidity reduces repayment flexibility.

Threshold Justification:
10,000 serves as a minimum stability benchmark.

---

## Rule 10 — Short Employment History

Rule ID: RF010

Condition:
IF Employment Duration < 2 Years

Evidence:
Employment Years

Rationale:
Short employment history may indicate income instability.

Threshold Justification:
Two years provides a basic stability indicator.
