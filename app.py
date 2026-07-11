import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Mobile UI Viewport Setup
st.set_page_config(
    page_title="NSE Alpha Ranker",
    page_icon="🏆",
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
    .global-card { padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px; }
    .stDataFrame div { font-size: 11px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏆 Institutional Alpha Ranker</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Enterprise Engine (Stability & Table Layout Patch Loaded)</p>", unsafe_allow_html=True)

# 2. Global Synopsis Engine
def fetch_global_synopsis():
    synopsis = {}
    try:
        nifty_df = yf.download("^NSEI", period="2d", interval="1d", progress=False, multi_level_index=False)
        if not nifty_df.empty and len(nifty_df) >= 2:
            last_nifty = nifty_df.iloc[-1]
            synopsis['NIFTY'] = {"val": float(last_nifty['Close']), "pct": ((float(last_nifty['Close']) - float(nifty_df.iloc[-2]['Close'])) / float(nifty_df.iloc[-2]['Close'])) * 100}
        sp_df = yf.download("^GSPC", period="2d", interval="1d", progress=False, multi_level_index=False)
        if not sp_df.empty and len(sp_df) >= 2:
            last_sp = sp_df.iloc[-1]
            synopsis['SP500'] = {"val": float(last_sp['Close']), "pct": ((float(last_sp['Close']) - float(sp_df.iloc[-2]['Close'])) / float(sp_df.iloc[-2]['Close'])) * 100}
    except: pass
    return synopsis

global_metrics = fetch_global_synopsis()
if global_metrics:
    st.markdown("### 🌍 Global Market Cues")
    col1, col2 = st.columns(2)
    with col1:
        n_data = global_metrics.get('NIFTY', {"val": 0, "pct": 0})
        st.markdown(f'<div class="global-card" style="background-color: {"#D1FAE5" if n_data["pct"] >= 0 else "#FEE2E2"}; color: #065F46;">NIFTY 50<br><span style="font-size: 16px;">{n_data["val"]:.2f}</span> ({n_data["pct"]:.2f}%)</div>', unsafe_allow_html=True)
    with col2:
        s_data = global_metrics.get('SP500', {"val": 0, "pct": 0})
        st.markdown(f'<div class="global-card" style="background-color: {"#D1FAE5" if s_data["pct"] >= 0 else "#FEE2E2"}; color: #065F46;">US S&P 500<br><span style="font-size: 16px;">{s_data["val"]:.2f}</span> ({s_data["pct"]:.2f}%)</div>', unsafe_allow_html=True)

# 3. Base Hardcoded Ticker Pools (Removed potentially unlisted/restructured symbols)
NIFTY_50_POOL = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "INFY.NS", "ITC.NS", "SBIN.NS", "HINDUNILVR.NS", "LT.NS", "HCLTECH.NS",
    "BAJFINANCE.NS", "SUNPHARMA.NS", "MARUTI.NS", "ADANIENT.NS", "KOTAKBANK.NS",
    "TITAN.NS", "AXISBANK.NS", "ULTRACEMCO.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS",
    "ADANIPORTS.NS", "ASIANPAINT.NS", "COALINDIA.NS", "TATASTEEL.NS", "BAJAJFINSV.NS",
    "M&M.NS", "JSWSTEEL.NS", "HINDALCO.NS", "GRASIM.NS", "SBILIFE.NS",
    "DIVISLAB.NS", "TECHM.NS", "WIPRO.NS", "BPCL.NS", "EICHERMOT.NS",
    "NESTLEIND.NS", "INDUSINDBK.NS", "DRREDDY.NS", "TATACONSUM.NS", "CIPLA.NS",
    "HEROMOTOCO.NS", "APOLLOHOSP.NS", "BAJAJ-AUTO.NS", "BRITANNIA.NS", "SHRIRAMFIN.NS", "BEL.NS"
]

EXPANDED_POOL = NIFTY_50_POOL + [
    "ZOMATO.NS", "SUZLON.NS", "JIOFIN.NS", "IREDA.NS", "RVNL.NS", "IRFC.NS", "BHEL.NS",
    "GMRINFRA.NS", "IDEA.NS", "YESBANK.NS", "PNB.NS", "HUDCO.NS", "NBCC.NS", "SJVN.NS",
    "NHPC.NS", "OIL.NS", "HAL.NS", "TATAPOWER.NS", "ADANIPOWER.NS", "DELHIVERY.NS",
    "PAYTM.NS", "NYKAA.NS", "UNIONBANK.NS", "IOB.NS", "CUB.NS", "ZENTEC.NS",
    "TATAELXSI.NS", "KPITTECH.NS", "COFORGE.NS", "PERSISTENT.NS", "DIXON.NS",
    "POLYCAB.NS", "KEI.NS", "IRCTC.NS", "CONCOR.NS", "AMBUJACEM.NS", "ACC.NS",
    "DLF.NS", "GODREJPROP.NS", "OBERREALTY.NS", "PFC.NS", "RECLTD.NS", "GAIL.NS",
    "SAIL.NS", "NMDC.NS", "NATIONALUM.NS", "VEDL.NS", "HINDCOPPER.NS", "EXIDEIND.NS",
    "VOLTAS.NS", "BLUESTARCO.NS", "HAVELLS.NS", "CUMMINSIND.NS", "SIEMENS.NS",
    "ABB.NS", "CGPOWER.NS", "BOB.NS", "CANBK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",
    "BANDHANBNK.NS", "AUBANK.NS", "BIOCON.NS", "GLENMARK.NS", "LUPIN.NS", "AUROPHARMA.NS",
    "LAURUSLABS.NS", "DEEPAKNTR.NS", "SRF.NS", "TATACHEM.NS", "ASHOKLEY.NS",
    "BALRAMCHIN.NS", "BERGEPAINT.NS", "BHARATFORG.NS", "BOSCHLTD.NS", "CHAMBLFERT.NS",
    "COLPAL.NS", "COROMANDEL.NS", "CROMPTON.NS", "ESCORTS.NS", "FORTIS.NS",
    "GNFC.NS", "GODREJCP.NS", "GRANULES.NS", "HINDPETRO.NS", "IBULHSGFIN.NS",
    "INDIACEM.NS", "INDIAMART.NS", "INDIGO.NS", "IPCALAB.NS", "JINDALSTEL.NS",
    "JUBLFOOD.NS", "LICHSGFIN.NS", "M&MFIN.NS", "MANAPPURAM.NS", "MCX.NS",
    "METROPOLIS.NS", "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS", "NAVINFLUOR.NS",
    "PEL.NS", "PETRONET.NS", "PIDILITIND.NS", "SUNTV.NS", "SYNGENE.NS",
    "TATACOMM.NS", "TREN.NS", "TVSMOTOR.NS", "UBL.NS", "UPL.NS", "WHIRLPOOL.NS", "ZEEL.NS"
]

# Watchlist Setup Menu
st.markdown("### 🛠️ Watchlist Setup Menu")
universe_choice = st.radio("Choose Scanner Target Base:", ["Nifty 50 Large-Caps Only", "Full Expanded Pool Universe"], index=1)

selected_tickers = NIFTY_50_POOL.copy() if universe_choice == "Nifty 50 Large-Caps Only" else EXPANDED_POOL.copy()

custom_scrip = st.text_input("➕ Inject Custom Stock Ticker (e.g., CAMPUS, HUDCO):").strip().upper()
if custom_scrip:
    formatted_scrip = custom_scrip if custom_scrip.endswith(".NS") else f"{custom_scrip}.NS"
    if formatted_scrip not in selected_tickers:
        selected_tickers.append(formatted_scrip)
        st.success(f"Successfully added {formatted_scrip} to active execution loop array.")

st.caption(f"📊 Ready to scan: **{len(selected_tickers)} stocks** running concurrently.")
st.markdown("---")

# Options Chain Data Engine
def analyze_options_chain(ticker_obj):
    pcr_val = 0.85 
    oi_signal = "Neutral"
    try:
        if not hasattr(ticker_obj, 'options') or not ticker_obj.options:
            return pcr_val, oi_signal
            
        expirations = ticker_obj.options
        if len(expirations) == 0:
            return pcr_val, oi_signal
            
        near_expiry = expirations[0]
        chains = ticker_obj.option_chain(near_expiry)
        
        calls_df = chains.calls
        puts_df = chains.puts
        
        if calls_df.empty or puts_df.empty:
            return pcr_val, oi_signal
            
        if 'openInterest' not in calls_df.columns or 'openInterest' not in puts_df.columns:
            return pcr_val, oi_signal
            
        total_call_oi = calls_df['openInterest'].dropna().sum()
        total_put_oi = puts_df['openInterest'].dropna().sum()
        
        if total_call_oi > 0:
            pcr_val = float(total_put_oi / total_call_oi)
            if pcr_val <= 0.55: oi_signal = "🐂 Call Heavy"
            elif pcr_val >= 1.15: oi_signal = "🐻 Put Heavy"
    except:
        pass
    return pcr_val, oi_signal

# 5. Core Pipeline Matrix Screener
def run_broad_screener(tickers):
    complete_matrix = []
    
    with st.spinner("Downloading technical chart data matrix from Yahoo Finance..."):
        all_data = yf.download(tickers, period="35d", interval="1d", group_by="ticker", threads=True, progress=False)
        
    progress_text = st.empty()
    progress_bar = st.progress(0)
    total_tickers = len(tickers)
    
    for index, ticker in enumerate(tickers):
        clean_name = ticker.replace(".NS", "")
        percent_complete = int(((index + 1) / total_tickers) * 100)
        progress_bar.progress(percent_complete)
        progress_text.caption(f"🔄 Processing structural anomalies: {clean_name} ({index + 1}/{total_tickers})")
        
        try:
            # CRITICAL DEFENSIVE CHECK: Verify data frame is fully populated before running calculations
            if ticker not in all_data.columns.get_level_values(0): continue
            df = all_data[ticker].dropna()
            if df.empty or len(df) < 22: continue
                
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            prev_2_row = df.iloc[-3]
            
            close_val = float(last_row['Close'])
            high_val = float(last_row['High'])
            low_val = float(last_row['Low'])
            
            avg_vol_20 = float(df.iloc[:-1]['Volume'].tail(20).mean())
            candle_range = high_val - low_val
            if candle_range == 0 or avg_vol_20 == 0: continue
                
            close_position_pct = ((close_val - low_val) / candle_range) * 100
            vol_multiplier = float(last_row['Volume']) / avg_vol_20
            
            is_nr7 = (high_val - low_val) == (df['High'] - df['Low']).tail(7).min()
            setup_status = "⚡ NR7" if is_nr7 else "Normal"
            
            is_higher_lows = (float(last_row['Low']) > float(prev_row['Low'])) and (float(prev_row['Low']) > float(prev_2_row['Low']))
            is_inside_bar = (float(last_row['High']) < float(prev_row['High'])) and (float(last_row['Low']) > float(prev_row['Low']))
            chart_shape = "Inside Sqz" if is_inside_bar else ("Higher Lows" if is_higher_lows else "Normal")
            
            complete_matrix.append({
                "Symbol": clean_name, "Price": f"₹{close_val:.2f}", "Vol Surge": vol_multiplier,
                "Close Pos %": close_position_pct, "Pattern": setup_status, "Chart Shape": chart_shape,
                "TickerObj": ticker, "RawClose": close_val, "IsNR7
