import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Mobile UI Layout Configurations
st.set_page_config(
    page_title="NSE Comprehensive Screener",
    page_icon="📊",
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
    .global-card { padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px; }
    /* Mobile text scale adjustments for comprehensive horizontal rows */
    .stDataFrame div { font-size: 12px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>📊 Raw Momentum Matrix Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Broad-spectrum engine: Filter constraints removed for manual selection</p>", unsafe_allow_html=True)

# 2. Global Synopsis Fetching Engine
def fetch_global_synopsis():
    synopsis = {}
    try:
        nifty_df = yf.download("^NSEI", period="5d", interval="1d", progress=False, multi_level_index=False)
        if not nifty_df.empty and len(nifty_df) >= 2:
            last_nifty = nifty_df.iloc[-1]
            nifty_close = float(last_nifty['Close'])
            nifty_prev = float(nifty_df.iloc[-2]['Close'])
            nifty_pct = ((nifty_close - nifty_prev) / nifty_prev) * 100
            synopsis['NIFTY'] = {"val": nifty_close, "pct": nifty_pct}
            
        sp_df = yf.download("^GSPC", period="5d", interval="1d", progress=False, multi_level_index=False)
        if not sp_df.empty and len(sp_df) >= 2:
            last_sp = sp_df.iloc[-1]
            sp_close = float(last_sp['Close'])
            sp_prev = float(sp_df.iloc[-2]['Close'])
            sp_pct = ((sp_close - sp_prev) / sp_prev) * 100
            synopsis['SP500'] = {"val": sp_close, "pct": sp_pct}
    except:
        pass
    return synopsis

global_metrics = fetch_global_synopsis()
if global_metrics:
    st.markdown("### 🌍 Global Market Cues")
    col1, col2 = st.columns(2)
    with col1:
        n_data = global_metrics.get('NIFTY', {"val": 0, "pct": 0})
        n_color = "#D1FAE5" if n_data['pct'] >= 0 else "#FEE2E2"
        st.markdown(f'<div class="global-card" style="background-color: {n_color}; color: #065F46;">NIFTY 50<br><span style="font-size: 16px;">{n_data["val"]:.2f}</span> ({n_data["pct"]:.2f}%)</div>', unsafe_allow_html=True)
    with col2:
        s_data = global_metrics.get('SP500', {"val": 0, "pct": 0})
        s_color = "#D1FAE5" if s_data['pct'] >= 0 else "#FEE2E2"
        st.markdown(f'<div class="global-card" style="background-color: {s_color}; color: #065F46;">US S&P 500<br><span style="font-size: 16px;">{s_data["val"]:.2f}</span> ({s_data["pct"]:.2f}%)</div>', unsafe_allow_html=True)

# 3. Expanded Ticker Pool Configuration
TICKERS_POOL = [
    # Top Active Mid/Small/Large Cap Momentum Counters
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
    "DELHIVERY.NS", "PAYTM.NS", "NYKAA.NS", "UNIONBANK.NS", "IOB.NS", "CUB.NS",
    "ZENTEC.NS", "TATAELXSI.NS", "KPITTECH.NS", "COFORGE.NS", "PERSISTENT.NS",
    "DIXON.NS", "POLYCAB.NS", "KEI.NS", "IRCTC.NS", "CONCOR.NS", "AMBUJACEM.NS",
    "ACC.NS", "DLF.NS", "GODREJPROP.NS", "OBERREALTY.NS", "PFC.NS", "RECLTD.NS",
    "GAIL.NS", "SAIL.NS", "NMDC.NS", "NATIONALUM.NS", "VEDL.NS", "HINDCOPPER.NS",
    "EXIDEIND.NS", "VOLTAS.NS", "BLUESTARCO.NS", "HAVELLS.NS", "CUMMINSIND.NS",
    "SIEMENS.NS", "ABB.NS", "CGPOWER.NS", "BOB.NS", "CANBK.NS", "IDFCFIRSTB.NS",
    "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS", "BIOCON.NS", "GLENMARK.NS",
    "LUPIN.NS", "AUROPHARMA.NS", "LAURUSLABS.NS", "DEEPAKNTR.NS", "SRF.NS"
]

# Catalyst Evaluator Engine
def analyze_catalysts(ticker_obj, current_close):
    catalyst = "None"
    target_headroom = "N/A"
    try:
        targets = ticker_obj.analyst_price_targets
        if targets and 'mean' in targets and targets['mean'] is not None:
            headroom = ((float(targets['mean']) - current_close) / current_close) * 100
            target_headroom = f"{headroom:.1f}%"
        news_list = ticker_obj.news
        if news_list:
            for item in news_list[:2]:
                title = item.get('title', '').lower()
                if any(kw in title for kw in ['earning', 'profit', 'dividend', 'acquisition', 'order', 'deal', 'fda']):
                    catalyst = "📰 News"
                    break
    except:
        pass
    return target_headroom, catalyst

# 4. Raw Spectrum Execution Loader
def run_broad_screener(tickers):
    complete_matrix = []
    
    with st.spinner("Downloading full technical chart blocks..."):
        all_data = yf.download(tickers, period="35d", interval="1d", group_by="ticker", threads=True, progress=False)
        
    for ticker in tickers:
        clean_name = ticker.replace(".NS", "")
        try:
            if ticker not in all_data.columns.get_level_values(0): continue
            df = all_data[ticker].dropna()
            if len(df) < 22: continue
                
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            prev_2_row = df.iloc[-3]
            
            close_val = float(last_row['Close'])
            high_val = float(last_row['High'])
            low_val = float(last_row['Low'])
            vol_val = float(last_row['Volume'])
            
            avg_vol_20 = float(df.iloc[:-1]['Volume'].tail(20).mean())
            candle_range = high_val - low_val
            if candle_range == 0 or avg_vol_20 == 0: continue
                
            # Compute raw baseline metrics without drop filters
            close_position_pct = ((close_val - low_val) / candle_range) * 100
            vol_multiplier = vol_val / avg_vol_20
            
            # Volatility Compression Structure
            all_ranges = df['High'] - df['Low']
            is_nr7 = all_ranges.tail(7).iloc[-1] == all_ranges.tail(7).min()
            setup_status = "⚡ NR7" if is_nr7 else "Normal"
            
            # Geometric Shapes Engine
            is_higher_lows = (float(last_row['Low']) > float(prev_row['Low'])) and (float(prev_row['Low']) > float(prev_2_row['Low']))
            is_inside_bar = (float(last_row['High']) < float(prev_row['High'])) and (float(last_row['Low']) > float(prev_row['Low']))
            chart_shape = "Inside Sqz" if is_inside_bar else ("Higher Lows" if is_higher_lows else "Normal")
            
            # Core values to write out to matrix rows
            complete_matrix.append({
                "Symbol": clean_name,
                "Price": f"₹{close_val:.2f}",
                "Vol Surge": vol_multiplier,
                "Close Pos %": close_position_pct,
                "Pattern": setup_status,
                "Chart Shape": chart_shape,
                "TickerObj": ticker,
                "RawClose": close_val
            })
        except:
            continue
            
    return pd.DataFrame(complete_matrix)

# 5. UI Application Process Trigger
if st.button("🚀 Load Complete Raw Momentum Matrix"):
    raw_df = run_broad_screener(TICKERS_POOL)
    
    if not raw_df.empty:
        # Sort by highest relative volume surges immediately to highlight activity paths
        raw_df = raw_df.sort_values(by="Vol Surge", ascending=False)
        
        # Pull lazy catalyst parameters for only top 25 high volume volume leaders to protect mobile runtime speeds
        with st.spinner("Extracting catalysts for volume leaders..."):
            catalyst_tags = []
            headrooms = []
            for _, row in raw_df.iterrows():
                if len(catalyst_tags) < 25:
                    t_obj = yf.Ticker(row['TickerObj'])
                    hr, cat = analyze_catalysts(t_obj, row['RawClose'])
                    headrooms.append(hr)
                    catalyst_tags.append(cat)
                else:
                    headrooms.append("N/A")
                    catalyst_tags.append("None")
                    
            raw_df["Analyst Trgt"] = headrooms
            raw_df["Catalyst"] = catalyst_tags
            
        # Format the final columns for clean mobile visualization tables
        raw_df["Vol Surge"] = raw_df["Vol Surge"].map(lambda x: f"{x:.2f}x")
        raw_df["Close Pos %"] = raw_df["Close Pos %"].map(lambda x: f"{x:.0f}%")
        
        final_clean_df = raw_df[["Symbol", "Price", "Vol Surge", "Close Pos %", "Pattern", "Chart Shape", "Analyst Trgt", "Catalyst"]]
        
        st.markdown("### 📋 Full Market Momentum Monitor")
        st.dataframe(final_clean_df, use_container_width=True, hide_index=True)
        st.success(f"Successfully tracked {len(final_clean_df)} core assets! Select your setup matches.")
    else:
        st.error("Data tracking pipeline encountered an unexpected sync refresh.")
