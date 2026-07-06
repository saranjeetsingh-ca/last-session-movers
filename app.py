import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Mobile UI Configuration
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

st.markdown("<h1>⚡ Turbo Momentum Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>High-Velocity Large, Mid & Small-Cap Selector</p>", unsafe_allow_html=True)

# 2. Configuration Parameters
st.markdown("### 🎛️ Sensitivity Parameters")
vol_threshold = st.slider("Min Volume Surge Multiplier", 1.0, 3.0, 1.5, 0.1)
close_percentile = st.slider("Candle Close Proximity (Top/Bottom %)", 10, 25, 15, 1)

top_cutoff = 1 - (close_percentile / 100)
bottom_cutoff = close_percentile / 100

# 3. High-Velocity High-Liquidity Ticker List (Large, Mid, & Small Caps included)
# Hardcoded to bypass the NiftyIndices server block and guarantee instant execution
TICKERS_POOL = [
    # High Velocity Mid & Small Caps
    "ZOMATO.NS", "SUZLON.NS", "JIOFIN.NS", "IREDA.NS", "RVNL.NS", "IRFC.NS", 
    "BHEL.NS", "GMRINFRA.NS", "IDEA.NS", "YESBANK.NS", "PNB.NS", "HUDCO.NS",
    "NBCC.NS", "SJVN.NS", "NHPC.NS", "OIL.NS", "HAL.NS", "BEL.NS", "TATAPOWER.NS",
    "ADANIPOWER.NS", "HDFCBANK.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "SBIN.NS",
    "ICICIBANK.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "COALINDIA.NS", "TATASTEEL.NS",
    "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "M&M.NS", "TATAMOTORS.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "BAJFINANCE.NS", "SUNPHARMA.NS", "MARUTI.NS", "HCLTECH.NS",
    "ADANIENT.NS", "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "HINDALCO.NS",
    "JSWSTEEL.NS", "GRASIM.NS", "WIPRO.NS", "TECHM.NS", "BPCL.NS", "CIPLA.NS",
    "DRREDDY.NS", "APOLLOHOSP.NS", "NESTLEIND.NS", "EICHERMOT.NS", "BRITANNIA.NS",
    "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "INDUSINDBK.NS", "DIVISLAB.NS", "LTIM.NS",
    "BAJAJFINSV.NS", "SBILIFE.NS", "HINDUNILVR.NS", "TATACONSUM.NS", "ADANIPORTS.NS",
    # Additional Highly Active Midcaps
    "LICI.NS", "PAYTM.NS", "NYKAA.NS", "UNIONBANK.NS", "IOB.NS", "CENTRALBK.NS",
    "ZENTEC.NS", "TATAELXSI.NS", "KPITTECH.NS", "COFORGE.NS", "PERSISTENT.NS",
    "MPHASIS.NS", "DIXON.NS", "POLYCAB.NS", "KEI.NS", "IRCTC.NS", "CONCOR.NS",
    "AMBUJACEM", "ACC.NS", "DLF.NS", "GODREJPROP.NS", "OBERREALTY.NS", "SOBHA.NS",
    "PFC.NS", "RECLTD.NS", "GAIL.NS", "SAIL.NS", "NMDC.NS", "NATIONALUM.NS",
    "VEDL.NS", "HINDCOPPER.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "VOLTAS.NS",
    "BLUESTARCO.NS", "HAVELLS.NS", "CUMMINSIND.NS", "AIAENG.NS", "THERMAX.NS",
    "SIEMENS.NS", "ABB.NS", "CGPOWER.NS", "BOB.NS", "CANBK.NS", "IDFCFIRSTB.NS",
    "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS", "CUB.NS", "KARURVYSYA.NS",
    "BIOCON.NS", "GLENMARK.NS", "LUPIN.NS", "AUBROPHARMA.NS", "LAURUSLABS.NS",
    "CHAMBLFERT.NS", "GNFC.NS", "GSFC.NS", "COROMANDEL.NS", "DEEPAKNTR.NS",
    "SRF.NS", "TATACHEM.NS", "PIDILITIND.NS", "BALRAMCHIN.NS", "RENUKA.NS",
    "PRAJIND.NS", "MAXHEALTH.NS", "FORTIS.NS", "GLOBALHEALTH.NS", "MEDANTA.NS"
]

# 4. High-Speed Bulk Processing Logic
def run_turbo_scan(tickers):
    bullish_list = []
    bearish_list = []
    
    with st.spinner("Downloading full market data matrix (takes ~5-10 seconds)..."):
        # Download data simultaneously in one parallel network batch
        all_data = yf.download(tickers, period="35d", interval="1d", group_by="ticker", threads=True, progress=False)
    
    status_text = st.empty()
    status_text.info("Data extracted! Filtering high-momentum structures...")
    
    for ticker in tickers:
        clean_name = ticker.replace(".NS", "")
        
        try:
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
            
            # Application Logic Threshold Filter Checks
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
    bullish_df, bearish_df = run_turbo_scan(TICKERS_POOL)
    
    # Render Output Layout Tables on Mobile Interface
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
