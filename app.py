import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

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
    .global-card { padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px; }
    /* Tighten data tables for clean scannability on mobile */
    .stDataFrame div { font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⚡ Auto-Regime Advanced Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Filters: Global Cues + Vol Surge + Sector + Room + Shapes + Catalysts</p>", unsafe_allow_html=True)

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
            nifty_date = nifty_df.index[-1].strftime('%d-%b-%Y')
            synopsis['NIFTY'] = {"val": nifty_close, "pct": nifty_pct, "date": nifty_date}
            
        sp_df = yf.download("^GSPC", period="5d", interval="1d", progress=False, multi_level_index=False)
        if not sp_df.empty and len(sp_df) >= 2:
            last_sp = sp_df.iloc[-1]
            sp_close = float(last_sp['Close'])
            sp_prev = float(sp_df.iloc[-2]['Close'])
            sp_pct = ((sp_close - sp_prev) / sp_prev) * 100
            sp_date = sp_df.index[-1].strftime('%d-%b-%Y')
            synopsis['SP500'] = {"val": sp_close, "pct": sp_pct, "date": sp_date}
    except:
        pass
    return synopsis

global_metrics = fetch_global_synopsis()
if global_metrics:
    st.markdown("### 🌍 Global Market Synopsis")
    col1, col2 = st.columns(2)
    with col1:
        n_data = global_metrics.get('NIFTY', {"val": 0, "pct": 0, "date": "N/A"})
        n_color = "#D1FAE5" if n_data['pct'] >= 0 else "#FEE2E2"
        st.markdown(f'<div class="global-card" style="background-color: {n_color}; color: #065F46;">GIFT / NIFTY 50<br><span style="font-size: 18px;">{n_data["val"]:.2f}</span> ({n_data["pct"]:.2f}%)</div>', unsafe_allow_html=True)
    with col2:
        s_data = global_metrics.get('SP500', {"val": 0, "pct": 0, "date": "N/A"})
        s_color = "#D1FAE5" if s_data['pct'] >= 0 else "#FEE2E2"
        st.markdown(f'<div class="global-card" style="background-color: {s_color}; color: #065F46;">US S&P 500<br><span style="font-size: 18px;">{s_data["val"]:.2f}</span> ({s_data["pct"]:.2f}%)</div>', unsafe_allow_html=True)

# 3. Market Regime Detector Engine
def detect_market_regime():
    try:
        nifty = yf.download("^NSEI", period="5d", interval="1d", progress=False, multi_level_index=False)
        last_row = nifty.iloc[-1]
        nifty_change = abs((float(last_row['Close']) - float(last_row['Open'])) / float(last_row['Open'])) * 100
        if nifty_change >= 0.95:
            return 2.0, 12, f"Trending Market ({nifty_change:.2f}%). Strict filters applied."
        else:
            return 1.3, 20, f"Quiet Market ({nifty_change:.2f}%). Relaxed parameters applied."
    except:
        return 1.5, 15, "Standard operational baseline applied."

if "vol_default" not in st.session_state:
    v, c, msg = detect_market_regime()
    st.session_state.vol_default = v
    st.session_state.close_default = c
    st.session_state.regime_msg = msg

st.info(st.session_state.regime_msg)

# 4. Filters Configuration
vol_threshold = st.slider("Min Volume Surge Multiplier", 1.0, 3.0, st.session_state.vol_default, 0.1)
close_percentile = st.slider("Candle Close Proximity (Top/Bottom %)", 10, 25, st.session_state.close_default, 1)
top_cutoff = 1 - (close_percentile / 100)
bottom_cutoff = close_percentile / 100

# 5. Asset Pool Setup with Sector Mapping
SECTOR_MAP = {
    "BANKING/FIN": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "BAJFINANCE.NS", "RECLTD.NS", "PFC.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "INFRA/POWER": ["RELIANCE.NS", "LT.NS", "NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS", "SUZLON.NS", "IRFC.NS"],
    "AUTO/METALS": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS"],
    "CONSUMER/PHARMA": ["ITC.NS", "SUNPHARMA.NS", "TITAN.NS", "HINDUNILVR.NS", "ZOMATO.NS", "JIOFIN.NS"]
}
TICKERS_POOL = [ticker for sublist in SECTOR_MAP.values() for ticker in sublist]

def safe_format_vol(val):
    try: return f"{float(val):.2f}x"
    except: return str(val)

# Helper: Analyst Target and News Scraper
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
            for item in news_list[:3]:
                title = item.get('title', '').lower()
                if any(kw in title for kw in ['earning', 'profit', 'dividend', 'acquisition', 'order', 'deal', 'fda']):
                    catalyst = "📰 News Highlight"
                    break
    except:
        pass
    return target_headroom, catalyst

# 6. Advanced Core Scanner Logic
def run_advanced_scan(tickers):
    raw_candidates = []
    sector_performance = {sec: 0 for sec in SECTOR_MAP.keys()}
    
    with st.spinner("Downloading technical chart data..."):
        all_data = yf.download(tickers, period="35d", interval="1d", group_by="ticker", threads=True, progress=False)
        
    for ticker in tickers:
        clean_name = ticker.replace(".NS", "")
        assigned_sector = next((k for k, v in SECTOR_MAP.items() if ticker in v), "MISC")
        
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
                
            close_position = (close_val - low_val) / candle_range
            vol_multiplier = vol_val / avg_vol_20
            
            # --- FEATURE A: VOLATILITY COMPRESSION (NR7) ---
            all_ranges = df['High'] - df['Low']
            is_nr7 = all_ranges.tail(7).iloc[-1] == all_ranges.tail(7).min()
            setup_status = "⚡ NR7" if is_nr7 else "Normal"
            
            # --- FEATURE B: GEOMETRIC CHART SHAPES ---
            is_higher_lows = (float(last_row['Low']) > float(prev_row['Low'])) and (float(prev_row['Low']) > float(prev_2_row['Low']))
            is_inside_bar = (float(last_row['High']) < float(prev_row['High'])) and (float(last_row['Low']) > float(prev_row['Low']))
            
            if is_inside_bar:
                chart_shape = "🔍 Inside Squeeze"
            elif is_higher_lows:
                chart_shape = "📈 Higher Lows"
            else:
                chart_shape = "Horizontal"
                
            # Room to Move (Resistance/Support margins)
            recent_closes = df.iloc[:-1]['Close'].tail(20)
            highest_res = float(recent_closes.max())
            lowest_sup = float(recent_closes.min())
            distance_to_res = ((highest_res - close_val) / close_val) * 100
            distance_to_sup = ((close_val - lowest_sup) / close_val) * 100
            
            if vol_multiplier >= vol_threshold:
                # Lazy-load structural news scrapers only for pre-filtered targets
                ticker_obj = yf.Ticker(ticker)
                headroom, catalyst_tag = analyze_catalysts(ticker_obj, close_val)
                
                if close_position >= top_cutoff:
                    if close_val < highest_res and distance_to_res < 1.0: continue
                    raw_candidates.append({
                        "Symbol": clean_name, "Close": close_val, "Vol Multi": vol_multiplier,
                        "Direction": "BULLISH", "Sector": assigned_sector, "Setup": setup_status,
                        "Shape": chart_shape, "Headroom": headroom, "Catalyst": catalyst_tag
                    })
                    sector_performance[assigned_sector] += 1
                elif close_position <= bottom_cutoff:
                    if close_val > lowest_sup and distance_to_sup < 1.0: continue
                    raw_candidates.append({
                        "Symbol": clean_name, "Close": close_val, "Vol Multi": vol_multiplier,
                        "Direction": "BEARISH", "Sector": assigned_sector, "Setup": setup_status,
                        "Shape": chart_shape, "Headroom": headroom, "Catalyst": catalyst_tag
                    })
                    sector_performance[assigned_sector] -= 1
        except:
            continue

    final_bullish = []
    final_bearish = []
    for item in raw_candidates:
        sec = item["Sector"]
        if item["Direction"] == "BULLISH" and sector_performance[sec] >= 0:
            final_bullish.append({"Symbol": item["Symbol"], "Close": f"₹{item['Close']:.2f}", "Vol Multi": item["Vol Multi"], "Setup": item["Setup"], "Chart Shape": item["Shape"], "Analyst Target": item["Headroom"], "Catalyst": item["Catalyst"]})
        elif item["Direction"] == "BEARISH" and sector_performance[sec] <= 0:
            final_bearish.append({"Symbol": item["Symbol"], "Close": f"₹{item['Close']:.2f}", "Vol Multi": item["Vol Multi"], "Setup": item["Setup"], "Chart Shape": item["Shape"], "Analyst Target": item["Headroom"], "Catalyst": item["Catalyst"]})
            
    return pd.DataFrame(final_bullish), pd.DataFrame(final_bearish)

# 7. UI Processing Execution Button
if st.button("🚀 Run Auto-Regime Selection Scan"):
    bullish_df, bearish_df = run_advanced_scan(TICKERS_POOL)
    
    st.markdown("### 🔥 Confluent Bullish Watchlist")
    if not bullish_df.empty:
        bullish_df = bullish_df.sort_values(by="Vol Multi", ascending=False)
        bullish_df["Vol Multi"] = bullish_df["Vol Multi"].apply(safe_format_vol)
        st.dataframe(bullish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bullish structural trends detected under current parameter settings.")
        
    st.markdown("### ❄️ Confluent Bearish Watchlist")
    if not bearish_df.empty:
        bearish_df = bearish_df.sort_values(by="Vol Multi", ascending=False)
        bearish_df["Vol Multi"] = bearish_df["Vol Multi"].apply(safe_format_vol)
        st.dataframe(bearish_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No bearish structural trends detected under current parameter settings.")
        
    st.success("Advanced multi-factor scanning complete!")
