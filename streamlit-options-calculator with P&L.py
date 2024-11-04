import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm

[Previous imports and functions remain the same...]

def calculate_pnl_scenarios(S, K, T, sigma, r, premium, option_type='call', scenarios=None):
    """Calculate P&L for different price scenarios"""
    if scenarios is None:
        # Generate scenarios from -30% to +30% of current price
        scenarios = np.linspace(S * 0.7, S * 1.3, 25)
    
    results = []
    for scenario_price in scenarios:
        if option_type == 'call':
            # Call option payoff: max(0, S - K)
            payoff = max(0, scenario_price - K)
            pnl = payoff - premium
        else:
            # Put option payoff: max(0, K - S)
            payoff = max(0, K - scenario_price)
            pnl = payoff - premium
            
        # Calculate return on investment
        if premium > 0:
            roi = (pnl / premium) * 100
        else:
            roi = 0
            
        results.append({
            'scenario_price': scenario_price,
            'price_change_pct': ((scenario_price - S) / S) * 100,
            'payoff': payoff,
            'pnl': pnl,
            'roi': roi
        })
    
    return pd.DataFrame(results)

# Update the main Streamlit interface
st.set_page_config(page_title="Options P&L Calculator", layout="wide")
st.title("Options P&L Calculator")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Basic Analysis", "P&L Scenarios", "Greeks", "Visualizations"])

with tab1:
    [Previous tab1 content remains the same...]

with tab2:
    st.subheader("Profit/Loss Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### Scenario Settings")
        custom_scenarios = st.checkbox("Use custom price scenarios")
        
        if custom_scenarios:
            min_price = st.number_input("Minimum Price Scenario", 
                                      value=float(spot_price * 0.7),
                                      step=1.0)
            max_price = st.number_input("Maximum Price Scenario", 
                                      value=float(spot_price * 1.3),
                                      step=1.0)
            num_scenarios = st.number_input("Number of Scenarios", 
                                          value=25,
                                          min_value=5,
                                          max_value=100,
                                          step=5)
            scenarios = np.linspace(min_price, max_price, num_scenarios)
        else:
            scenarios = None
        
        # Calculate current prices
        call_price, _, _ = calculate_black_scholes(spot_price, strike_price, time_to_expiry, 
                                                 volatility, risk_free_rate, 'call')
        put_price, _, _ = calculate_black_scholes(spot_price, strike_price, time_to_expiry, 
                                                volatility, risk_free_rate, 'put')
        
        st.write("### Current Option Prices")
        st.write(f"Call Premium: ${call_price:.2f}")
        st.write(f"Put Premium: ${put_price:.2f}")
    
    with col2:
        # Calculate P&L scenarios
        call_scenarios = calculate_pnl_scenarios(spot_price, strike_price, time_to_expiry, 
                                               volatility, risk_free_rate, call_price, 
                                               'call', scenarios)
        put_scenarios = calculate_pnl_scenarios(spot_price, strike_price, time_to_expiry, 
                                              volatility, risk_free_rate, put_price, 
                                              'put', scenarios)
        
        # Create P&L visualization
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=("P&L at Expiration", "Return on Investment (%)"))
        
        # P&L Plot
        fig.add_trace(
            go.Scatter(x=call_scenarios['scenario_price'], 
                      y=call_scenarios['pnl'],
                      name="Call P&L",
                      line=dict(color='green')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=put_scenarios['scenario_price'], 
                      y=put_scenarios['pnl'],
                      name="Put P&L",
                      line=dict(color='red')),
            row=1, col=1
        )
        
        # ROI Plot
        fig.add_trace(
            go.Scatter(x=call_scenarios['scenario_price'], 
                      y=call_scenarios['roi'],
                      name="Call ROI",
                      line=dict(color='green', dash='dash')),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=put_scenarios['scenario_price'], 
                      y=put_scenarios['roi'],
                      name="Put ROI",
                      line=dict(color='red', dash='dash')),
            row=2, col=1
        )
        
        # Add reference lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        fig.add_vline(x=spot_price, line_dash="dash", line_color="blue")
        fig.add_vline(x=strike_price, line_dash="dot", line_color="orange")
        
        fig.update_layout(height=700, showlegend=True)
        fig.update_xaxes(title_text="Stock Price", row=2, col=1)
        fig.update_yaxes(title_text="P&L ($)", row=1, col=1)
        fig.update_yaxes(title_text="ROI (%)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # P&L Scenario Table
    st.write("### Detailed P&L Scenarios")
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("#### Call Option Scenarios")
        call_table = call_scenarios.round(2)
        call_table.columns = ['Stock Price', 'Price Change %', 'Payoff', 'P&L', 'ROI %']
        st.dataframe(call_table.style.highlight_max(['P&L'], color='lightgreen')
                                   .highlight_min(['P&L'], color='lightpink'))
        
        # Key statistics
        st.write("#### Call Option Statistics")
        st.write(f"Maximum Profit: ${call_scenarios['pnl'].max():.2f}")
        st.write(f"Maximum Loss: ${call_scenarios['pnl'].min():.2f}")
        st.write(f"Break-even Price: ${strike_price + call_price:.2f}")
    
    with col4:
        st.write("#### Put Option Scenarios")
        put_table = put_scenarios.round(2)
        put_table.columns = ['Stock Price', 'Price Change %', 'Payoff', 'P&L', 'ROI %']
        st.dataframe(put_table.style.highlight_max(['P&L'], color='lightgreen')
                                  .highlight_min(['P&L'], color='lightpink'))
        
        # Key statistics
        st.write("#### Put Option Statistics")
        st.write(f"Maximum Profit: ${put_scenarios['pnl'].max():.2f}")
        st.write(f"Maximum Loss: ${put_scenarios['pnl'].min():.2f}")
        st.write(f"Break-even Price: ${strike_price - put_price:.2f}")

    # Add explanation
    st.markdown("""
    ### Understanding P&L Analysis
    
    #### Key Metrics:
    - **P&L**: Profit or loss at different stock price levels
    - **ROI**: Percentage return on investment
    - **Break-even Point**: Stock price where P&L becomes zero
    
    #### Important Points:
    - Maximum loss for bought options is limited to premium paid
    - P&L shown is at expiration (doesn't include time value)
    - Break-even points include the cost of premium
    
    #### Chart Features:
    - Blue vertical line: Current stock price
    - Orange vertical line: Strike price
    - Solid lines: P&L at expiration
    - Dashed lines: Return on Investment (ROI)
    """)

[Previous tab3 and tab4 content remains the same...]
