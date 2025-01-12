from flask import Flask, request, render_template
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import FuncFormatter

app = Flask(__name__)

# Ensure the static directory exists
if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/')
def index():
    # List of assets and their respective company names
    assets_info = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com, Inc.',
        'TSLA': 'Tesla, Inc.',
        'FB': 'Meta Platforms, Inc.',
        'BRK.B': 'Berkshire Hathaway Inc.',
        'NVDA': 'NVIDIA Corporation',
        'V': 'Visa Inc.',
        'JNJ': 'Johnson & Johnson',
        'PG': 'Procter & Gamble Co.',
        'UNH': 'UnitedHealth Group Incorporated',
        'HD': 'The Home Depot, Inc.',
        'DIS': 'The Walt Disney Company',
        'VZ': 'Verizon Communications Inc.',
        'NFLX': 'Netflix, Inc.',
        'ADBE': 'Adobe Inc.',
        'CMCSA': 'Comcast Corporation',
        'INTC': 'Intel Corporation',
        'XOM': 'Exxon Mobil Corporation'
    }

    # Market representations with their index names
    market_representations = {
        'SPY': 'S&P 500 ETF',
        'IVV': 'iShares S&P 500 ETF',
        'VOO': 'Vanguard S&P 500 ETF',
        'DIA': 'Dow Jones Industrial Average ETF',
        'QQQ': 'Invesco QQQ Trust',
        'IWM': 'iShares Russell 2000 ETF',
        'XLF': 'Financial Select Sector SPDR Fund',
        'XLY': 'Consumer Discretionary Select Sector SPDR Fund'
    }

    return render_template('index.html', assets_info=assets_info, market_representations=market_representations)

@app.route('/optimize', methods=['POST'])
def optimize():
    ASSETS = request.form['assets'].split(',')
    ASSETS = [ticker.strip() for ticker in ASSETS]
    START_DATE = request.form['start_date']
    END_DATE = request.form['end_date']
    MARKET_REPRESENTATION = request.form['market_representation']
    NUM_PORTFOLIOS = int(request.form['num_portfolios'])
    RISK_FREE_RATE = float(request.form['risk_free_rate'])

    # Download data
    data = yf.download(ASSETS, start=START_DATE, end=END_DATE)
    market_data = yf.download(MARKET_REPRESENTATION, start=START_DATE, end=END_DATE)

    data = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']
    market_data = market_data['Adj Close'] if 'Adj Close' in market_data.columns else market_data['Close']

    daily_returns = data.pct_change().dropna()
    cov_matrix = daily_returns.cov()
    market_daily_returns = market_data.pct_change().dropna()
    market_return = market_daily_returns.mean() * 252
    market_volatility = market_daily_returns.std() * np.sqrt(252)
    market_sharpe_ratio = (market_return - RISK_FREE_RATE) / market_volatility

    results = np.zeros((4, NUM_PORTFOLIOS))
    weights_record = np.zeros((len(ASSETS), NUM_PORTFOLIOS))

    for i in range(NUM_PORTFOLIOS):
        weights = np.random.random(len(ASSETS))
        weights /= np.sum(weights)
        weights_record[:, i] = weights

        portfolio_return = np.sum(weights * daily_returns.mean()) * 252
        portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        sharpe_ratio = (portfolio_return - RISK_FREE_RATE) / portfolio_stddev

        results[0, i] = portfolio_return
        results[1, i] = portfolio_stddev
        results[2, i] = sharpe_ratio
        results[3, i] = i

    columns = ['Return', 'Volatility', 'Sharpe Ratio', 'Simulation']
    simulated_portfolios = pd.DataFrame(results.T, columns=columns)

    market_return_value = market_return.iloc[0]
    market_volatility_value = market_volatility.iloc[0]
    market_sharpe_ratio_value = market_sharpe_ratio.iloc[0]

    optimal_idx = simulated_portfolios['Sharpe Ratio'].idxmax()
    optimal_portfolio = simulated_portfolios.loc[optimal_idx]
    optimal_weights = weights_record[:, optimal_idx]

    optimal_weights_zipped = list(zip(ASSETS, optimal_weights))

    # Visualization
    plt.figure(figsize=(12, 8))
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.1f}%'.format(x * 100)))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1f}%'.format(y * 100)))
    plt.scatter(simulated_portfolios['Volatility'], simulated_portfolios['Return'], c=simulated_portfolios['Sharpe Ratio'], cmap='YlGnBu')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.title('Efficient Frontier')
    plt.scatter(market_volatility_value, market_return_value, color='red', marker='o', s=100)
    plt.scatter(optimal_portfolio['Volatility'], optimal_portfolio['Return'], color='green', marker='*', s=100)

    # Save the plot as an image
    img_path = os.path.join('static', 'efficient_frontier.png')
    plt.savefig(img_path)
    plt.close()

    # Insights
    efficiency_message = ""
    if optimal_portfolio['Sharpe Ratio'] > market_sharpe_ratio_value:
        efficiency_message = "The Optimized Portfolio has a higher Sharpe Ratio than the Market, suggesting it is more efficient."
    else:
        efficiency_message = "The Market has a higher Sharpe Ratio, suggesting the portfolio may not offer a better risk-adjusted return."

    risk_return_tradeoff_message = (
        f"Optimal Portfolio lies on the Efficient Frontier with a Return of {optimal_portfolio['Return'] * 100:.2f}% "
        f"and Volatility of {optimal_portfolio['Volatility'] * 100:.2f}%. "
    )

    if optimal_portfolio['Return'] > market_return_value:
        risk_return_tradeoff_message += "The Optimized Portfolio offers a higher return than the Market, for a comparable level of risk."
    else:
        risk_return_tradeoff_message += "The Optimized Portfolio has a lower return than the Market but might offer better risk management."

    risk_free_rate_analysis = (
        f"Risk-Free Rate: {RISK_FREE_RATE * 100:.2f}%<br>"
        f"Optimized Portfolio's Sharpe Ratio: {optimal_portfolio['Sharpe Ratio']:.2f}<br>"
    )

    if RISK_FREE_RATE == 0:
        risk_free_rate_analysis += "Since the risk-free rate is assumed to be zero, the Sharpe ratio is directly comparing the portfolio's excess return to its volatility."
    else:
        risk_free_rate_analysis += "Any increase in the risk-free rate will reduce the Sharpe ratio, which will need a higher return to compensate."

    asset_weight_breakdown = []
    for asset, weight in zip(ASSETS, optimal_weights):
        asset_weight_breakdown.append(f"{asset}: {weight * 100:.2f}%")

    # Insights on Asset Contribution
    high_weight_assets = [asset for asset, weight in zip(ASSETS, optimal_weights) if weight > 0.2]  # Threshold for high weight assets
    asset_contribution_insight = ""
    if high_weight_assets:
        asset_contribution_insight = f"High-weight assets (greater than 20% allocation): {', '.join(high_weight_assets)}"
    else:
        asset_contribution_insight = "No assets have more than 20% allocation, showing a well-diversified portfolio."

    # Monte Carlo Simulation Insights
    monte_carlo_insights = (
        f"Number of Portfolios Simulated: {NUM_PORTFOLIOS}<br>"
        f"The optimized portfolio came from simulation #{optimal_portfolio['Simulation']}, which had the highest Sharpe Ratio."
    )

    extreme_risk_portfolio = simulated_portfolios[simulated_portfolios['Volatility'] > 0.3]
    if not extreme_risk_portfolio.empty:
        monte_carlo_insights += "Some portfolios with very high risk (>30% volatility) were simulated, indicating possible extreme risk/reward trade-offs."
    else:
        monte_carlo_insights += "No portfolios with extremely high risk were found in the simulation."

    # Summary of Simulation Results
    high_sharpe_ratio_portfolios = simulated_portfolios[simulated_portfolios['Sharpe Ratio'] > market_sharpe_ratio_value]
    summary_results = f"Number of portfolios outperforming the market Sharpe ratio: {len(high_sharpe_ratio_portfolios)}"

    return render_template('results.html',
                           optimal_portfolio_return=optimal_portfolio['Return'],
                           optimal_portfolio_volatility=optimal_portfolio['Volatility'],
                           optimal_portfolio_sharpe_ratio=optimal_portfolio['Sharpe Ratio'],
                           optimal_weights=optimal_weights_zipped,
                           market_return=market_return_value,
                           market_volatility=market_volatility_value,
                           market_sharpe_ratio=market_sharpe_ratio_value,
                           efficiency_message=efficiency_message,
                           risk_return_tradeoff_message=risk_return_tradeoff_message,
                           risk_free_rate_analysis=risk_free_rate_analysis,
                           asset_weight_breakdown=asset_weight_breakdown,
                           asset_contribution_insight=asset_contribution_insight,
                           monte_carlo_insights=monte_carlo_insights,
                           summary_results=summary_results,
                           img_path=img_path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")