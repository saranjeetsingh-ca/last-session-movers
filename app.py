import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Mobile UI Layout Configurations
st.set_page_config(
    page_title="NSE Automated Turbo Scanner",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    h1 { font-size: 24px !important; text-align: center; color: #1E3A8A; font-weight: bold; }
    p.sub { text-align: center; font-size: 13px; color: #6B7280; margin-bottom: 15px; }
    div.stButton > button {
        width: 100%; background-color: #10B981; color: white;
        font-weight: bold; padding: 14px; border-radius: 8px; font-size: 16px; border: none;
    }
    div.stButton > button:hover { background-color: #059669; color: white; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⚡ Auto-Regime Momentum Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Filters: Vol Surge + Sector + Room + Volatility Compression (NR7)</p>", unsafe_allow_html=True)

# 2. Automated Market Regime Detector Engine
def detect_market_regime():
    try:
        nifty = yf.download("^NSEI", period="5d", interval="1d", progress=False)
        if isinstance(nifty.columns, pd.MultiIndex):
            nifty.columns = nifty.columns.get_level_values(0)
            
        last_row = nifty.iloc[-1]
        nifty_open = float(last_row['Open'])
        nifty_close = float(last_row['Close'])
        
        nifty_change = abs((nifty_close - nifty_open) / nifty_open) * 100
        
        if nifty_change >= 0.95:
            return 2.0, 12, f"Trending / High-Velocity Market detected (Nifty moved {nifty_change:.2f}%). Sliders locked to high institutional constraints."
        else:
            return 1.3, 20, f"Quiet / Sideways Market detected (Nifty moved {nifty_change:.2f}%). Sliders opened for midcap velocity moves."
    except Exception as e:
        return 1.5, 15, "Default market regime baseline applied."

if "vol_default" not in st.session_state:
    v, c, msg = detect_market_regime()
    st.session_state.vol_default = v
    st.session_state.close_default = c
    st.session_state.regime_msg = msg

st.info(st.session_state.regime_msg)

# 3. Dynamic Filter Parameters
st.markdown("### 🎛️ Dynamic Filter Parameters")
vol_threshold = st.slider("Min Volume Surge Multiplier", 1.0, 3.0, st.session_state.vol_default, 0.1)
close_percentile = st.slider("Candle Close Proximity (Top/Bottom %)", 10, 25, st.session_state.close_default, 1)

top_cutoff = 1 - (close_percentile / 100)
bottom_cutoff = close_percentile / 100

# 4. Sector Map Array Pool 
SECTOR_MAP = {
    "BANKING/FIN": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS", "PNB.NS", "YESBANK.NS", "IRFC.NS", "PFC.NS", "RECLTD.NS", "BOB.NS", "CANBK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "TATAELXSI.NS", "KPITTECH.NS", "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS"],
    "INFRA/POWER/ENERGY": ["RELIANCE.NS", "LT.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "TATAPOWER.NS", "ADANIPOWER.NS", "SUZLON.NS", "BHEL.NS", "GMRINFRA.NS", "HUDCO.NS", "NBCC.NS", "SJVN.NS", "NHPC.NS", "OIL.NS", "SAIL.NS", "GAIL.NS"],
    "DEFENSE/AERO": ["HAL.NS", "BEL.NS", "CGPOWER.NS", "SIEMENS.NS", "ABB.NS"],
    "AUTO": ["MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "EXIDEIND.NS"],
    "METALS": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "NMDC.NS", "NATIONALUM.NS", "VEDL.NS", "HINDCOPPER.NS"],
    "CONSUMER/PHARMA/MISC": ["ITC.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "GRASIM.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DIVISLAB.NS", "HINDUNILVR.NS", "TATACONSUM.NS", "ADANIPORTS.NS", "ZOMATO.NS", "JIOFIN.NS", "IREDA.NS", "RVNL.NS", "DLF.NS"]
}

TICKERS_POOL = [ticker for sublist in SECTOR_MAP.values() for ticker in sublist]

def safe_format_vol(val):
    try: return f"{float(val):.2f}x"
    except: return str(val)

# 5. Pipeline Analysis Logic with NR7 Check
def run_advanced_scan(tickers):
    raw_candidates = []
    sector_performance = {sec: 0 for sec in SECTOR_MAP.keys()}
    
    with st.spinner("Downloading full market data matrix..."):
        all_data = yf.download(tickers, period="35d", interval="1d", group_by="ticker", threads=True, progress=False)
        
    for ticker in tickers:
        clean_name = ticker.replace(".NS", "")
        assigned_sector = next((k for k, v in SECTOR_MAP.items() if ticker in v), "MISC")
        
        try:
            if ticker not in all_data.columns.get_level_values(0): continue
            df = all_data[ticker].dropna()
            if len(df) < 22: continue # Extra buffer days to look back 7 periods safely
                
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
            
            # --- VOLATILITY COMPRESSION (NR7 LOGIC) ---
            # Calculate the High-Low trading range for the last 7 available completed daily bars
            all_ranges = df['High'] - df['Low']
            last_7_ranges = all_ranges.tail(7)
            
            # Check if yesterday's range is strictly the minimum value among those 7 days
            is_nr7 = last_7_ranges.iloc[-1] == last_7_ranges.min()
            nr7_status = "⚡ NR7 Ready" if is_nr7 else "Normal"
            
            # Room to move structural ceiling calculations
            recent_closes = prev_rows['Close'].tail(20)
            highest_resistance_close = float(recent_closes.max())
            lowest_support_close = float(recent_closes.min())
            
            distance_to_res = ((highest_resistance_close - close_val) / close_val) * 100
            distance_to_sup = ((close_val - lowest_support_close) / close_val) * 100
            
            if vol_multiplier >= vol_threshold:
                if close_position >= top_cutoff:
                    if close_val < highest_resistance_close and distance_to_res < 1.0: continue
                    raw_candidates.append({
                        "Symbol": clean_name, "Close": close_val, "Vol Multi": vol_multiplier,
                        "Direction": "BULLISH", "Sector": assigned_sector, 
                        "Room %": f"{max(0.0, distance_to_res):.1f}%", "Setup": nr7_status
                    })
                    sector_performance[assigned_sector] += 1
                elif close_position <= bottom_cutoff:
                    if close_val > lowest_support_close and distance_to_sup < 1.0: continue
                    raw_candidates.append({
                        "Symbol": clean_name, "Close": close_val, "Vol Multi": vol_multiplier,
                        "Direction": "BEARISH", "Sector": assigned_sector, 
                        "Room %": f"{max(0.0, distance_to_sup):.1f}%", "Setup": nr7_status
                    })
                    sector_performance[assigned_sector] -= 1
        except:
            continue

    final_bullish = []
    final_bearish = []
    
    for item in raw_candidates:
        sec = item["Sector"]
        if item["Direction"] == "BULLISH" and sector_performance[sec] >= 0:
            final_bullish.append({
                "Symbol": item["Symbol"], "Close": f"₹{item['Close']:.2f}", 
                "Vol Multi": item["Vol Multi"], "Room to Ceiling": item["Room %"], "Setup Status": item["Setup"]
            })
        elif item["Direction"] == "BEARISH" and sector_performance[sec] <= 0:
            final_bearish.append({
                "Symbol": item["Symbol"], "Close": f"₹{item['Close']:.2f}", 
                "Vol Multi": item["Vol Multi"], "Room to Floor": item["Room %"], "Setup Status": item["Setup"]
            })
            
    return pd.DataFrame(final_bullish), pd.DataFrame(final_bearish)

# 6. UI Trigger Execution
if st.button("🚀 Run Auto-Regime Selection Scan"):
    bullish_df, bearish_df = run_advanced_scan(TICKERS_POOL)
    
    st.markdown("### 🔥 Confluent Bullish Watchlist")
    if not bullish_df.empty:
        bullish_df = bullish_df.sort_values(by="Vol Multi", ascending=False)
        bullish_df["Vol Multi"] = bullish_df["Vol Multi"].apply(safe_format_vol)
        st.dataframe(bullish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bullish stocks matched constraints under this regime pattern.")
        
    st.markdown("### ❄️ Confluent Bearish Watchlist")
    if not bearish_df.empty:
        bearish_df = bearish_df.sort_values(by="Vol Multi", ascending=False)
        bearish_df["Vol Multi"] = bearish_df["Vol Multi"].apply(safe_format_vol)
        st.dataframe(bearish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bearish stocks matched constraints under this regime pattern.")
        
    st.success("Advanced structural scanning complete!")
