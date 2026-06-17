# MODEL_INSIGHTS

## Most Important Features

The top features influencing model predictions are:

1. cibil_score
2. income_bank_mismatch
3. foir
4. gst_missing_quarters
5. is_night_application
6. employment_years
7. credit_utilization_pct
8. num_credit_inquiries_30d
9. total_emi_bounces
10. credit_age_months

These features indicate that credit history, repayment capacity, income verification, and borrowing behavior are the primary drivers of risk assessment.

## Edge Cases Handled Well

* Applicants with low CIBIL scores and previous defaults were assigned higher risk scores.
* High-income applicants with strong credit profiles received lower risk scores.
* High credit utilization, multiple active loans, and high EMI obligations increased predicted risk.
* Self-employed applicants with missing GST records were identified as higher risk.

## Edge Cases to Watch

* Applicants with no credit history may have less reliable predictions.
* New-to-credit customers can be sensitive to small changes in features.
* Extremely high loan amounts may require additional manual review.

## Fairness Findings

Subgroup analysis was performed across income levels, age groups, and employment types. Risk scores varied across income groups as expected due to differences in repayment capacity. No significant bias was observed across employment categories or age groups based on the available data.

## Recommendations

* Continue monitoring new-to-credit applicants.
* Perform periodic fairness and performance evaluations.
* Monitor key features such as CIBIL score, FOIR, and credit utilization for data drift.
* Retrain the model regularly as new credit data becomes available.

## Conclusion

The model relies on meaningful credit risk indicators and performed reasonably well across the tested edge cases. Regular monitoring and retraining will help maintain model accuracy and fairness.
