
# Portfolio Optimization using Monte Carlo Simulation

This notebook demonstrates portfolio optimization to find the optimal investment portfolio that maximizes returns while minimizing risk.

## Features

- Uses Monte Carlo simulation to generate thousands of possible portfolio combinations.
- Calculates portfolio return, volatility, and Sharpe ratio for each combination.
- Identifies the portfolio with the highest Sharpe ratio as the optimal portfolio.
- Visualizes the efficient frontier, showing the relationship between return and volatility.
- Displays the optimal portfolio weights for each asset.
- Compares the optimal portfolio with the market performance (using SPY as a benchmark).


## Libraries
- `numpy`: Utilized for array and numerical computations. It is particularly used during the Monte Carlo simulation for optimizing performance.
- `pandas`: Used for data transformations. Creates easier handling of Monte Carlo simulation results.
- `yfinance`: Primary source for downloading stock market data. Used for finding asset data for portfolio that will be optimized.
- `matplotlib`: Crucial for data visualization. Used to show the Efficient Frontier and multitude of simulated portfolios.



## How it works

1. **Import Libraries:** Imports necessary libraries like `yfinance`, `pandas`, `numpy`, and `matplotlib`.
2. **Define Inputs:** Defines the list of assets, start and end dates for data retrieval, and other parameters like the number of portfolios to simulate.
3. **Fetch Stock Data:** Downloads historical adjusted closing prices of the selected assets from Yahoo Finance.
4. **Calculate Returns and Covariance:** Calculates daily returns and the covariance matrix for the assets.
5. **Monte Carlo Simulation:** Generates random portfolio weights for a large number of portfolios. For each portfolio:
    - Calculate annualized portfolio return.
    - Calculate annualized portfolio volatility.
    - Calculate the Sharpe ratio (risk-adjusted return).
6. **Identify Optimal Portfolio:** Finds the portfolio with the highest Sharpe ratio.
7. **Visualization:** Plots the efficient frontier, highlighting the optimal portfolio and the market performance (SPY).
8. **Display Optimal Portfolio Details:** Shows the optimal portfolio weights and performance metrics.
9. **Display Market Performance:** Shows the market (SPY) performance metrics.


# Conclusion:
The code successfully generated an efficient frontier of potential investment portfolios based on a Monte Carlo simulation.

The optimal portfolio identified maximizes the Sharpe ratio, indicating a balance between high return and low risk.

The visualization clearly shows the relationship between portfolio return and volatility, with the optimal portfolio marked for easy identification.

The optimal portfolio weights provide insights into the allocation strategy.

The comparison with the market's (SPY) performance highlights the potential benefits of portfolio optimization.

This approach can help investors make informed decisions about asset allocation to achieve their investment goals.