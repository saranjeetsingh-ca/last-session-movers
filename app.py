import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
st.markdown("<p class='sub'>Pure Technical Engine (Segfault-Protected Chunking)</p>", unsafe_allow_html=True)

# --- PARAMETER GUIDELINES & WEIGHTAGE BLOCK ---
with st.expander("📚 Technical Scoring Matrix & Guide"):
    st.markdown("""
    ### 🧮 Algorithmic Technical Score (100 Points Total)
    * **Close Position % (40 Points):** Points are awarded based on how close the stock closed to its absolute high of the day. A 100% close gets max points.
    * **Volume Surge (40 Points):** Points scale up as today's volume exceeds the 20-day average. Max points are awarded at a 2.0x volume multiplier.
    * **Pattern / Chart Shape (20 Points):** 20 points for an *Inside Bar Squeeze* or *NR7* coil. 10 points for a *Higher Lows* trend. 5 points for a standard flat shape.

    ### 📊 Column Definitions
    * **1D Change:** The exact percentage difference between today's close and yesterday's close.
    * **Trend:** Indicates if the current price is trading above (🟢 Bullish) or below (🔴 Bearish) its 20-day moving average.
    * **Vol Surge:** Today's volume divided by the 20-day average. Anything above 1.50x indicates strong institutional footprint.
    * **Chart Shape:** "Higher Lows" means buyers are stepping up early. "Inside Sqz" indicates a coiled spring (volatility contraction).
    * **Pattern:** Identifies explosive setup states like NR7 (narrowest range of 7 days) or normal regimes.
    """)

# --- ENTERPRISE ANTI-RATE-LIMIT SESSION ---
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# 2. Hardcoded Core Ticker Pools
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
    "GMRAIRPORT.NS", "IDEA.NS", "YESBANK.NS", "PNB.NS", "HUDCO.NS", "NBCC.NS", "SJVN.NS",
    "NHPC.NS", "OIL.NS", "HAL.NS", "TATAPOWER.NS", "ADANIPOWER.NS", "DELHIVERY.NS",
    "PAYTM.NS", "NYKAA.NS", "UNIONBANK.NS", "IOB.NS", "CUB.NS", "ZENTEC.NS",
    "TATAELXSI.NS", "KPITTECH.NS", "COFORGE.NS", "PERSISTENT.NS", "DIXON.NS",
    "POLYCAB.NS", "KEI.NS", "IRCTC.NS", "CONCOR.NS", "AMBUJACEM.NS", "ACC.NS",
    "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PFC.NS", "RECLTD.NS", "GAIL.NS",
    "SAIL.NS", "NMDC.NS", "NATIONALUM.NS", "VEDL.NS", "HINDCOPPER.NS", "EXIDEIND.NS",
    "VOLTAS.NS", "BLUESTARCO.NS", "HAVELLS.NS", "CUMMINSIND.NS", "SIEMENS.NS",
    "ABB.NS", "CGPOWER.NS", "BANKBARODA.NS", "CANBK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",
    "BANDHANBNK.NS", "AUBANK.NS", "BIOCON.NS", "GLENMARK.NS", "LUPIN.NS", "AUROPHARMA.NS",
    "LAURUSLABS.NS", "DEEPAKNTR.NS", "SRF.NS", "TATACHEM.NS", "ASHOKLEY.NS",
    "BALRAMCHIN.NS", "BERGEPAINT.NS", "BHARATFORG.NS", "BOSCHLTD.NS", "CHAMBLFERT.NS",
    "COLPAL.NS", "COROMANDEL.NS", "CROMPTON.NS", "ESCORTS.NS", "FORTIS.NS",
    "GNFC.NS", "GODREJCP.NS", "GRANULES.NS", "HINDPETRO.NS", "SAMAMBA.NS",
    "INDIACEM.NS", "INDIAMART.NS", "INDIGO.NS", "IPCALAB.NS", "JINDALSTEL.NS",
    "JUBLFOOD.NS", "LICHSGFIN.NS", "M&MFIN.NS", "MANAPPURAM.NS", "MCX.NS",
    "METROPOLIS.NS", "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS", "NAVINFLUOR.NS",
    "PETRONET.NS", "PIDILITIND.NS", "SUNTV.NS", "SYNGENE.NS",
    "TATACOMM.NS", "TRENT.NS", "TVSMOTOR.NS", "UBL.NS", "UPL.NS", "WHIRLPOOL.NS", "ZEEL.NS"
]

# Watchlist Setup Menu
st.markdown("### 🛠️ Watchlist Setup Menu")
universe_choice = st.radio("Choose Scanner Target Base:", ["Nifty 50 Large-Caps Only", "Full Expanded Pool Universe"], index=1)

selected_tickers = NIFTY_50_POOL.copy() if universe_choice == "Nifty 50 Large-Caps Only" else EXPANDED_POOL.copy()

# --- MOBILE FIX: Session State & Form ---
if "custom_additions" not in st.session_state:
    st.session_state.custom_additions = []

with st.form(key="ticker_injector", clear_on_submit=True):
    custom_scrip = st.text_input("➕ Inject Custom Stock Ticker (e.g., CAMPUS, HUDCO):")
    add_btn = st.form_submit_button("Add to Scanner")

if add_btn and custom_scrip:
    clean_scrip = custom_scrip.strip().upper()
    formatted_scrip = clean_scrip if clean_scrip.endswith(".NS") else f"{clean_scrip}.NS"
    
    if formatted_scrip not in selected_tickers and formatted_scrip not in st.session_state.custom_additions:
        st.session_state.custom_additions.append(formatted_scrip)
        st.success(f"Successfully locked {formatted_scrip} into the matrix!")

selected_tickers.extend(st.session_state.custom_additions)

if st.session_state.custom_additions:
    st.caption(f"📝 Custom Injections Active: **{', '.join(st.session_state.custom_additions)}**")

st.caption(f"📊 Ready to scan: **{len(selected_tickers)} stocks** running in stable batches.")
st.markdown("---")

# Safe Core Pipeline Matrix Screener
def run_broad_screener(tickers):
    complete_matrix = []
    st.info("📡 Establishing secure connection. Fetching price-action data in stable batches...")
    
    # Split tickers into chunks of 20 to completely prevent C-Engine Memory Segfaults
    chunk_size = 20
    ticker_chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    
    progress_text = st.empty()
    progress_bar = st.progress(0)
    total_tickers = len(tickers)
    processed_count = 0
    
    for chunk in ticker_chunks:
        try:
            # Enforce threads=False to completely eliminate the segmentation fault risk
            all_data = yf.download(
                chunk, 
                period="35d", 
                interval="1d", 
                group_by="ticker", 
                threads=False, 
                progress=False, 
                session=session
            )
        except Exception as e:
            continue # If a single batch fails, keep moving to protect the scan execution
            
        if all_data.empty:
            continue
            
        for ticker in chunk:
            processed_count += 1
            clean_name = ticker.replace(".NS", "")
            percent_complete = min(100, int((processed_count / total_tickers) * 100))
            progress_bar.progress(percent_complete)
            progress_text.caption(f"🔄 Processing technical arrays: {clean_name} ({processed_count}/{total_tickers})")
            
            try:
                # Handle single vs multi-ticker dataframe structural outputs safely
                if len(chunk) == 1:
                    df = all_data.dropna()
                else:
                    if ticker not in all_data.columns.get_level_values(0): continue
                    df = all_data[ticker].dropna()
                    
                if df.empty or len(df) < 22: continue
                    
                last_row = df.iloc[-1]
                prev_row = df.iloc[-2]
                prev_2_row = df.iloc[-3]
                
                close_val = float(last_row['Close'])
                prev_close = float(prev_row['Close'])
                high_val = float(last_row['High'])
                low_val = float(last_row['Low'])
                
                # Baseline Calculations
                avg_vol_20 = float(df.iloc[:-1]['Volume'].tail(20).mean())
                sma_20 = float(df['Close'].tail(20).mean())
                
                # 1D Percentage Change
                pct_change = ((close_val - prev_close) / prev_close) * 100
                
                candle_range = high_val - low_val
                if candle_range == 0 or avg_vol_20 == 0: continue
                    
                close_position_pct = ((close_val - low_val) / candle_range) * 100
                vol_multiplier = float(last_row['Volume']) / avg_vol_20
                
                # Pattern Logic
                is_nr7 = (high_val - low_val) == (df['High'] - df['Low']).tail(7).min()
                setup_status = "⚡ NR7" if is_nr7 else "Normal"
                
                is_higher_lows = (float(last_row['Low']) > float(prev_row['Low'])) and (float(prev_row['Low']) > float(prev_2_row['Low']))
                is_inside_bar = (float(last_row['High']) < float(prev_row['High'])) and (float(last_row['Low']) > float(prev_row['Low']))
                chart_shape = "Inside Sqz" if is_inside_bar else ("Higher Lows" if is_higher_lows else "Normal")
                
                # Trend Logic
                trend_status = "🟢 Bullish" if close_val > sma_20 else "🔴 Bearish"
                
                complete_matrix.append({
                    "Symbol": clean_name, 
                    "Price": f"₹{close_val:.2f}",
                    "1D Change": f"{pct_change:+.2f}%", 
                    "Trend": trend_status, 
                    "Vol Surge": vol_multiplier, 
                    "Close Pos %": close_position_pct, 
                    "Pattern": setup_status, 
                    "Chart Shape": chart_shape,
                    "RawClose": close_val, "IsNR7": is_nr7, "IsInside": is_inside_bar, "IsHL": is_higher_lows
                })
            except: continue
            
    progress_bar.empty()
    progress_text.empty()
    return pd.DataFrame(complete_matrix)

# 3. UI Execution Trigger Block
if st.button("🚀 Run Technical Master Scan"):
    try:
        st.markdown("### 🌍 Live Market Cues")
        nifty_df = yf.download("^NSEI", period="2d", interval="1d", progress=False, multi_level_index=False, session=session, threads=False)
        sp_df = yf.download("^GSPC", period="2d", interval="1d", progress=False, multi_level_index=False, session=session, threads=False)
        
        col1, col2 = st.columns(2)
        with col1:
            if not nifty_df.empty and len(nifty_df) >= 2:
                n_pct = ((float(nifty_df.iloc[-1]['Close']) - float(nifty_df.iloc[-2]['Close'])) / float(nifty_df.iloc[-2]['Close'])) * 100
                st.markdown(f'<div class="global-card" style="background-color: {"#D1FAE5" if n_pct >= 0 else "#FEE2E2"}; color: #065F46;">NIFTY 50: {float(nifty_df.iloc[-1]["Close"]):.2f} ({n_pct:.2f}%)</div>', unsafe_allow_html=True)
        with col2:
            if not sp_df.empty and len(sp_df) >= 2:
                s_pct = ((float(sp_df.iloc[-1]['Close']) - float(sp_df.iloc[-2]['Close'])) / float(sp_df.iloc[-2]['Close'])) * 100
                st.markdown(f'<div class="global-card" style="background-color: {"#D1FAE5" if s_pct >= 0 else "#FEE2E2"}; color: #065F46;">US S&P 500: {float(sp_df.iloc[-1]["Close"]):.2f} ({s_pct:.2f}%)</div>', unsafe_allow_html=True)
    except:
        st.warning("📊 Global market cue widget skipped due to external server rate restrictions.")

    raw_df = run_broad_screener(selected_tickers)
    
    if not raw_df.empty:
        # 1. PURE TECHNICAL SCORING ENGINE (Max 100 Points)
        scores = []
        for _, row in raw_df.iterrows():
            pos = row['Close Pos %']
            pos_score = 40 * (pos / 100) if pos >= 50 else 40 * ((100 - pos) / 100)
            vol_score = min(40.0, (row['Vol Surge'] / 2.0) * 40.0)
            pattern_score = 20 if (row['IsNR7'] or row['IsInside']) else (10 if row['IsHL'] else 5)
            
            final_score = int(pos_score + vol_score + pattern_score)
            scores.append(min(100, final_score))
            
        raw_df["Tech Score"] = scores
        raw_df = raw_df.sort_values(by="Tech Score", ascending=False)
        
        # 2. CLEAN UP FORMATTING FOR UI DISPLAY
        raw_df["Vol Surge"] = raw_df["Vol Surge"].map(lambda x: f"{x:.2f}x")
        raw_df["Close Pos %"] = raw_df["Close Pos %"].map(lambda x: f"{x:.0f}%")

        # Select Columns for Display (Now includes "1D Change")
        final_raw_directory = raw_df[["Tech Score", "Symbol", "Price", "1D Change", "Trend", "Vol Surge", "Close Pos %", "Pattern", "Chart Shape"]]

        # 3. FINAL RENDER
        st.markdown("### 📋 Complete Technical Market Directory")
        st.dataframe(final_raw_directory, width="stretch", hide_index=True)
        st.success("Scan complete! Pure technical institutional momentum isolated successfully.")
    else:
        st.error("Screener dataset is empty. Please wait a moment and try running the scan again.")
