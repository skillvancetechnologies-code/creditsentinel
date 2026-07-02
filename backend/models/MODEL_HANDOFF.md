**1. What is the Model?**



This model predicts credit risk for loan applications using a LightGBM Classifier. It analyzes applicant financial, credit, employment, and banking features to estimate the probability of loan default.



Performance:

AUC Score: 0.8106



**2. How Does It Work?**



The model takes 47 engineered features as input, including:



Monthly Income

Requested Loan Amount

Existing Monthly EMI

Employment Years

FOIR

Loan-to-Income Ratio

CIBIL Score

Credit Utilization

Credit Inquiries

Previous Defaults

Banking Features

GST Features

Employment Type

City Tier Indicators



The model outputs a risk score between 0 and 1:



0 = Low Risk (Safer Applicant)

1 = High Risk (Riskier Applicant)



**3. Limitations**



Raw age information is not available, therefore age-based analysis cannot be performed.

The model performs best on applicant profiles similar to the training data.

Prediction quality may decrease if applicant behavior changes significantly over time.

Fairness across all demographic groups cannot be fully validated due to limited demographic information.



**4. How to Retrain the Model**



Collect the latest application and repayment data.

Update feature engineering datasets.

Run the model training script.

Validate model performance using AUC score.

Verify feature importance stability and data leakage checks.

Deploy the model if validation criteria are satisfied.

Save the updated model and documentation.



**5. Monitoring**



Weekly Monitoring

Check AUC score.

Monitor prediction distribution.

Monitor model stability.

Retraining Trigger

Retrain the model if AUC drops below 0.8106.

Retrain when significant data drift is detected.

Retrain after a substantial increase in new application data.

Monthly Monitoring

Review fairness metrics.

Monitor feature drift.

Review feature importance changes.



**Conclusion**



The LightGBM credit risk model has been validated, stress-tested, and documented for future maintenance. Regular monitoring and retraining are recommended to maintain model performance and reliability.

