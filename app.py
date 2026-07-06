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
