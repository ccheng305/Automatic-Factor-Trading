# Automatic-Factor-Trading
-----------------------------------------------------------

Usage Notes
---------------------------------------------------------------
- The factors taken into consideration are Price to Book ratio, Price to Cash-Flow ratio, 
Price to Earning ratio, Price to Sales ratio, n-period momentum factor, m-period reversion factor
and L-period log return volatility. Each of the factor is assigned a weight, and the M-score is calculated 
for each stock. 100 stocks with highest M-scores will be selected to compose the portfolio. 

- Needs Yahoo Finance API

- Run with Python 3
