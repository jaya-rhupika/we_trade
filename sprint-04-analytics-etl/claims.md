# Claims

The findings below use only DuckDB table `staging.candles`.

Analysis period:
2025-08-27 to 2026-08-27.

Selected universe:
- HDFC Bank (HDFCBANK.NS)
- Reliance Industries (RELIANCE.NS)
- Infosys (INFY.NS)
- Apple (AAPL)
- NVIDIA (NVDA)

The DuckDB table contains 1,307 rows from 2025-08-27 to 2026-08-27.
Intraday range is calculated as `(high - low) / close * 100`. Closing-price
change is calculated from the first and last available close for each company.
Daily-leadership claims use the 261 dates on which all five companies have a
row. Traded-value comparisons are omitted because the table does not retain
currency metadata for comparing INR and USD.

| # | Claim | Chart artefact |
|---|---|---|
| 1 | From 2025-08-27 to 2026-08-27, NVIDIA recorded 42,201,252,771 traded shares, representing 61.84% of the 68,239,252,165 traded shares recorded across the five selected companies. | `charts/analytics_dashboard.html#claim-1` |
| 2 | From 2025-08-27 to 2026-08-27, HDFC Bank had the lowest average intraday high-to-low range at 1.69%, below Reliance Industries at 1.70%, Apple at 2.09%, Infosys at 2.19%, and NVIDIA at 3.01%. | `charts/analytics_dashboard.html#claim-2` |
| 3 | From 2025-08-27 to 2026-08-27, Reliance Industries had the smallest closing-price decline, falling 5.37% from 1,385.90 to 1,311.42 in its reported price units. | `charts/analytics_dashboard.html#claim-3` |
| 4 | On 248 of the 261 common trading dates from 2025-08-27 to 2026-08-27, NVIDIA recorded the highest traded volume among the five selected companies. | `charts/analytics_dashboard.html#claim-4` |
| 5 | From 2025-08-27 to 2026-08-27, NVIDIA had the highest daily-return volatility at 2.31 percentage points, compared with Infosys at 1.93 and Apple at 1.63. | `charts/analytics_dashboard.html#claim-5` |
| 6 | On 45 of the 261 common trading dates from 2025-08-27 to 2026-08-27, Infosys had the largest intraday high-to-low range among the five selected companies. | `charts/analytics_dashboard.html#claim-6` |

## Notes

Prices are supplied analytical data and are not presented as real-world market
conclusions.

