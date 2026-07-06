import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# Page configuration optimized for mobile viewport layout
st.set_page_config(
    page_title="NSE Momentum",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Mobile-First Styling
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 22px !important; text-align: center; margin-bottom: 5px; color: #1E3A8A; }
    p.subtitle { text-align: center; font-size: 13px; color: #6B7280; margin-bottom: 20px; }
    div.stButton > button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover { background-color: #1D4ED8; color: white; }
    .metric-card {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>📈 NSE Intraday Momentum</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Find structural EOD setups for the next session</p>", unsafe_allow_html=True)

# 50 Highly Liquid NSE Tickers for Scanning
NSE_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "INFY.NS", "ITC.NS", "SBIN.NS", "LICI.NS", "HINDUNILVR.NS", "LT.NS",
    "HCLTECH.NS", "BAJFINANCE.NS", "SUNPHARMA.NS", "MARUTI.NS", "ADANIENT.NS",
    "KOTAKBANK.NS", "TITAN.NS", "AXISBANK.NS", "ULTRACEMCO.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "ADANIPORTS.NS", "ASIANPAINT.NS", "COALINDIA.NS",
    "TATASTEEL.NS", "BAJAJFINSV.NS", "M&M.NS", "JSWSTEEL.NS", "TATAMOTORS.NS",
    "HINDALCO.NS", "GRASIM.NS", "SBILIFE.NS", "LTIM.NS", "DIVISLAB.NS",
    "TECHM.NS", "WIPRO.NS", "BPCL.NS", "EICHERMOT.NS", "NESTLEIND.NS",
    "INDUSINDBK.NS", "DRREDDY.NS", "TATACONSUM.NS", "CIPLA.NS", "HEROMOTOCO.NS",
    "APOLLOHOSP.NS", "BAJAJ-AUTO.NS", "BRITANNIA.NS", "JIOFIN.NS"
]

def clean_ticker_name(symbol):
    return symbol.replace(".NS", "")

def run_momentum_scan():
    bullish_list = []
    bearish_list = []
    
    # Progress indicator for mobile view
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(NSE_TICKERS)
    
    for idx, ticker in enumerate(NSE_TICKERS):
        status_text.text(f"Scanning {clean_ticker_name(ticker)} ({idx+1}/{total})...")
        progress_bar.progress((idx + 1) / total)
        
        try:
            # Fetch last 40 days to securely compute 20-day metrics
            df = yf.download(ticker, period="40d", progress=False, interval="1d")
            if df.empty or len(df) < 21:
                continue
                
            # Flatten multi-level columns if any (from yfinance updates)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Compute core mathematical parameters
            last_row = df.iloc[-1]
            prev_rows = df.iloc[:-1]
            
            close_val = float(last_row['Close'])
            high_val = float(last_row['High'])
            low_val = float(last_row['Low'])
            vol_val = float(last_row['Volume'])
            
            avg_vol_20 = float(prev_rows['Volume'].tail(20).mean())
            
            candle_range = high_val - low_val
            if candle_range == 0:
                continue
                
            # Location of close within the daily candle range (0.0 to 1.0)
            close_position = (close_val - low_val) / candle_range
            vol_multiplier = vol_val / avg_vol_20 if avg_vol_20 > 0 else 0
            
            # Application Logic Filters
            if vol_multiplier >= 1.5:
                # Bullish Filter: Closes in the top 15% of the day's range
                if close_position >= 0.85:
                    bullish_list.append({
                        "Symbol": clean_ticker_name(ticker),
                        "Close": f"₹{close_val:.2f}",
                        "Vol Multi": f"{vol_multiplier:.2fx}"
                    })
                # Bearish Filter: Closes in the bottom 15% of the day's range
                elif close_position <= 0.15:
                    bearish_list.append({
                        "Symbol": clean_ticker_name(ticker),
                        "Close": f"₹{close_val:.2f}",
                        "Vol Multi": f"{vol_multiplier:.2fx}"
                    })
        except Exception as e:
            continue
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(bullish_list), pd.DataFrame(bearish_list)

if st.button("🚀 Run EOD Momentum Scan"):
    with st.spinner("Processing market structural parameters..."):
        bullish_df, bearish_df = run_momentum_scan()
        
        # Display Results in a Mobile-Optimized Matrix
        st.markdown("### 🔥 Bullish Watchlist")
        if not bullish_df.empty:
            st.dataframe(bullish_df, use_container_width=True, hide_index=True)
        else:
            st.info("No scrips qualified for structural bullish momentum.")
            
        st.markdown("### ❄️ Bearish Watchlist")
        if not bearish_df.empty:
            st.dataframe(bearish_df, use_container_width=True, hide_index=True)
        else:
            st.info("No scrips qualified for structural bearish momentum.")
            
        st.success("Scan complete! Feed these tickers into your trade execution tool.")
