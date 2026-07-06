import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Mobile Layout Configuration
st.set_page_config(
    page_title="NSE Advanced Scanner",
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

st.markdown("<h1>⚡ Institutional Momentum Selector</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Filters: Volume Surge + Close Proximity + Sector + Room to Move</p>", unsafe_allow_html=True)

# 2. Configuration Parameters
st.markdown("### 🎛️ Sensitivity Parameters")
vol_threshold = st.slider("Min Volume Surge Multiplier", 1.0, 3.0, 1.5, 0.1)
close_percentile = st.slider("Candle Close Proximity (Top/Bottom %)", 10, 25, 15, 1)

top_cutoff = 1 - (close_percentile / 100)
bottom_cutoff = close_percentile / 100

with st.expander("📖 Quick Configuration Guide"):
    st.markdown("""
    **Match your sliders to the current market regime:**
    * **Setup A (Quiet Markets):** Vol `1.2x` \| Close Proximity `20%`
    * **Setup B (Trending Markets):** Vol `1.8x` \| Close Proximity `10% - 15%`
    """)

# 3. High-Velocity Ticker Pool with Internal Sector Mapping
SECTOR_MAP = {
    "BANKING/FIN": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS", "PNB.NS", "YESBANK.NS", "IRFC.NS", "PFC.NS", "RECLTD.NS", "BOB.NS", "CANBK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "TATAELXSI.NS", "KPITTECH.NS", "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS"],
    "INFRA/POWER/ENERGY": ["RELIANCE.NS", "LT.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "TATAPOWER.NS", "ADANIPOWER.NS", "SUZLON.NS", "BHEL.NS", "GMRINFRA.NS", "HUDCO.NS", "NBCC.NS", "SJVN.NS", "NHPC.NS", "OIL.NS", "GAS.NS", "SAIL.NS", "GAIL.NS"],
    "DEFENSE/AERO": ["HAL.NS", "BEL.NS", "CGPOWER.NS", "SIEMENS.NS", "ABB.NS"],
    "AUTO": ["MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "EXIDEIND.NS"],
    "METALS": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "NMDC.NS", "NATIONALUM.NS", "VEDL.NS", "HINDCOPPER.NS"],
    "CONSUMER/PHARMA/MISC": ["ITC.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "GRASIM.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DIVISLAB.NS", "HINDUNILVR.NS", "TATACONSUM.NS", "ADANIPORTS.NS", "ZOMATO.NS", "JIOFIN.NS", "IREDA.NS", "RVNL.NS", "DLF.NS"]
}

# Flatten the structure to form a clean, single ticker array
TICKERS_POOL = [ticker for sublist in SECTOR_MAP.values() for ticker in sublist]

# Helper function to format strings securely
def safe_format_vol(val):
    try: return f"{float(val):.2f}x"
    except: return str(val)

# 4. Multi-Stage Filtering Engine
def run_advanced_scan(tickers):
    raw_candidates = []
    sector_performance = {sec: 0 for sec in SECTOR_MAP.keys()} # Tracking sector momentum bias
    
    with st.spinner("Downloading full market data matrix..."):
        all_data = yf.download(tickers, period="35d", interval="1d", group_by="ticker", threads=True, progress=False)
        
    for ticker in tickers:
        clean_name = ticker.replace(".NS", "")
        # Identify the assigned tracking sector group
        assigned_sector = next((k for k, v in SECTOR_MAP.items() if ticker in v), "MISC")
        
        try:
            if ticker not in all_data.columns.get_level_values(0): continue
            df = all_data[ticker].dropna()
            if len(df) < 21: continue
                
            last_row = df.iloc[-1]
            prev_rows = df.iloc[:-1]
            
            close_val = float(last_row['Close'])
            high_val = float(last_row['High'])
            low_val = float(last_row['Low'])
            vol_val = float(last_row['Volume'])
            
            avg_vol_20 = float(prev_rows['Volume'].tail(20).mean())
            candle_range = high_val - low_val
            if candle_range == 0 or avg_vol_20 == 0: continue
                
            close_position = (close_val - low_val) / candle_range
            vol_multiplier = vol_val / avg_vol_20
            
            # STAGE 2 FILTER: Resistance and Support Ceiling Check via 20-Day Closures
            recent_closes = prev_rows['Close'].tail(20)
            highest_resistance_close = float(recent_closes.max())
            lowest_support_close = float(recent_closes.min())
            
            # Calculate distance margins to major key structures
            distance_to_res = ((highest_resistance_close - close_val) / close_val) * 100
            distance_to_sup = ((close_val - lowest_support_close) / close_val) * 100
            
            # Initial Momentum Threshold Evaluation
            if vol_multiplier >= vol_threshold:
                if close_position >= top_cutoff:
                    # Filter: Ensure it has at least 1.0% upside room before hitting hard resistance
                    if close_val < highest_resistance_close and distance_to_res < 1.0:
                        continue # Dropped: Hit resistance ceiling
                        
                    raw_candidates.append({
                        "Symbol": clean_name, "Close": close_val, "Vol Multi": vol_multiplier,
                        "Direction": "BULLISH", "Sector": assigned_sector, "Room %": f"{max(0.0, distance_to_res):.1f}%"
                    })
                    sector_performance[assigned_sector] += 1 # Add positive sector weight
                    
                elif close_position <= bottom_cutoff:
                    # Filter: Ensure it has room down before hitting major support floors
                    if close_val > lowest_support_close and distance_to_sup < 1.0:
                        continue # Dropped: Hit floor base
                        
                    raw_candidates.append({
                        "Symbol": clean_name, "Close": close_val, "Vol Multi": vol_multiplier,
                        "Direction": "BEARISH", "Sector": assigned_sector, "Room %": f"{max(0.0, distance_to_sup):.1f}%"
                    })
                    sector_performance[assigned_sector] -= 1 # Add negative sector weight
        except:
            continue

    # STAGE 1 FILTER: Sector Confluence Verification Loop
    final_bullish = []
    final_bearish = []
    
    for item in raw_candidates:
        sec = item["Sector"]
        # A stock passes if its specific sector shows a matching net directional momentum bias
        if item["Direction"] == "BULLISH" and sector_performance[sec] >= 0:
            final_bullish.append({"Symbol": item["Symbol"], "Close": f"₹{item['Close']:.2f}", "Vol Multi": item["Vol Multi"], "Room to Ceiling": item["Room %"]})
        elif item["Direction"] == "BEARISH" and sector_performance[sec] <= 0:
            final_bearish.append({"Symbol": item["Symbol"], "Close": f"₹{item['Close']:.2f}", "Vol Multi": item["Vol Multi"], "Room to Floor": item["Room %"]})
            
    return pd.DataFrame(final_bullish), pd.DataFrame(final_bearish)

# 5. UI Trigger Execution
if st.button("🚀 Start Multi-Filter Market Scan"):
    bullish_df, bearish_df = run_advanced_scan(TICKERS_POOL)
    
    st.markdown("### 🔥 Confluent Bullish Watchlist")
    if not bullish_df.empty:
        bullish_df = bullish_df.sort_values(by="Vol Multi", ascending=False)
        bullish_df["Vol Multi"] = bullish_df["Vol Multi"].apply(safe_format_vol)
        st.dataframe(bullish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bullish breakout stocks survived the sector/resistance filters.")
        
    st.markdown("### ❄️ Confluent Bearish Watchlist")
    if not bearish_df.empty:
        bearish_df = bearish_df.sort_values(by="Vol Multi", ascending=False)
        bearish_df["Vol Multi"] = bearish_df["Vol Multi"].apply(safe_format_vol)
        st.dataframe(bearish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bearish breakdown stocks survived the sector/support filters.")
        
    st.success("Advanced structural scanning complete!")
