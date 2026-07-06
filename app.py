import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Mobile UI Configurations
st.set_page_config(
    page_title="NSE Turbo Scanner",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    h1 { font-size: 24px !important; text-align: center; color: #1E3A8A; font-weight: bold; }
    p.sub { text-align: center; font-size: 13px; color: #6B7280; margin-bottom: 15px; }
    div.stButton > button {
        width: 100%; background-color: #2563EB; color: white;
        font-weight: bold; padding: 14px; border-radius: 8px; font-size: 16px; border: none;
    }
    div.stButton > button:hover { background-color: #1D4ED8; color: white; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⚡ Turbo Nifty 500 Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Multi-threaded processing engine (Completed in seconds)</p>", unsafe_allow_html=True)

# 2. Configuration Parameters
st.markdown("### 🎛️ Sensitivity Parameters")
vol_threshold = st.slider("Min Volume Surge Multiplier", 1.0, 3.0, 1.5, 0.1)
close_percentile = st.slider("Candle Close Proximity (Top/Bottom %)", 10, 25, 15, 1)

top_cutoff = 1 - (close_percentile / 100)
bottom_cutoff = close_percentile / 100

# 3. Cached Index Loader
@st.cache_data(ttl=86400)
def get_nifty_500_tickers():
    try:
        url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return [str(symbol).strip() + ".NS" for symbol in df['Symbol'].dropna()]
    except:
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "SBIN.NS", "ZOMATO.NS"]

# 4. High-Speed Bulk Processing Logic
def run_turbo_scan(tickers):
    bullish_list = []
    bearish_list = []
    
    # STEP A: Download all 500 tickers at once using multi-threading
    with st.spinner("Downloading full Nifty 500 market data matrix..."):
        all_data = yf.download(tickers, period="35d", interval="1d", group_by="ticker", threads=True, progress=False)
    
    # STEP B: Process the downloaded matrix instantly out of local memory
    status_text = st.empty()
    status_text.info("Data downloaded successfully! Running mathematical matrix sorting...")
    
    for ticker in tickers:
        clean_name = ticker.replace(".NS", "")
        
        try:
            # Extract individual ticker data from the mega dataframe safely
            if ticker not in all_data.columns.get_level_values(0):
                continue
            df = all_data[ticker].dropna()
            
            if len(df) < 21:
                continue
                
            last_row = df.iloc[-1]
            prev_rows = df.iloc[:-1]
            
            close_val = float(last_row['Close'])
            high_val = float(last_row['High'])
            low_val = float(last_row['Low'])
            vol_val = float(last_row['Volume'])
            
            avg_vol_20 = float(prev_rows['Volume'].tail(20).mean())
            candle_range = high_val - low_val
            
            if candle_range == 0 or avg_vol_20 == 0:
                continue
                
            close_position = (close_val - low_val) / candle_range
            vol_multiplier = vol_val / avg_vol_20
            
            # Filter Checks
            if vol_multiplier >= vol_threshold:
                if close_position >= top_cutoff:
                    bullish_list.append({
                        "Symbol": clean_name, "Close": f"₹{close_val:.2f}", "Vol Multi": vol_multiplier
                    })
                elif close_position <= bottom_cutoff:
                    bearish_list.append({
                        "Symbol": clean_name, "Close": f"₹{close_val:.2f}", "Vol Multi": vol_multiplier
                    })
        except:
            continue
            
    status_text.empty()
    return pd.DataFrame(bullish_list), pd.DataFrame(bearish_list)

# 5. UI Trigger Execution
if st.button("🚀 Start High-Speed Market Scan"):
    tickers_list = get_nifty_500_tickers()
    bullish_df, bearish_df = run_turbo_scan(tickers_list)
    
    # Format and present results cleanly for mobile
    st.markdown("### 🔥 Bullish Watchlist")
    if not bullish_df.empty:
        bullish_df = bullish_df.sort_values(by="Vol Multi", ascending=False)
        bullish_df["Vol Multi"] = bullish_df["Vol Multi"].map(lambda x: f"{x:.2fx}")
        st.dataframe(bullish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bullish setups qualified.")
        
    st.markdown("### ❄️ Bearish Watchlist")
    if not bearish_df.empty:
        bearish_df = bearish_df.sort_values(by="Vol Multi", ascending=False)
        bearish_df["Vol Multi"] = bearish_df["Vol Multi"].map(lambda x: f"{x:.2fx}")
        st.dataframe(bearish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bearish setups qualified.")
        
    st.success("Scan complete!")
