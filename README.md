
# we_trade - capstone

## Command to Run the Pipeline

```bash
cd sprint-04-analytics-etl
pip install -e .
python -m analytics_etl.extractTransformLoad.pipeline
```

## Command to check if rows are loaded to duckdb
```bash
# install duckdb cli if you don't have it
pip install duckdb

# then from sprint-04-analytics-etl/
python -c "
import duckdb
con = duckdb.connect('data/analytics.duckdb')
print(con.sql('SELECT * FROM staging.candles LIMIT 10'))
print(con.sql('SELECT COUNT(*) FROM staging.candles'))
con.close()
"
```

## Command to view the duckdb ui
```
#  From sprint-04-analytics-etl/
python -c "import duckdb; con=duckdb.connect('data/analytics.duckdb'); con.execute('CALL start_ui()'); input('Press Enter to stop...')"
```

## Date Range
Add date range in the .env file


## Symbol Universe

The five symbols were selected to provide a diverse and analytically useful dataset covering both Indian and US equity markets.

**RELIANCE.NS – Reliance Industries:**
Reliance Industries was selected as a major Indian large-cap company with significant market activity and a diversified business across areas such as energy, telecommunications and retail. It provides a strong representation of the Indian market and is useful for analysing price movements, trading volume and traded value.

**INFY.NS – Infosys:**
Infosys was selected to represent the Indian information technology sector. It is a well-established and actively traded company, making it suitable for analysing historical price and volume data. Its inclusion also allows comparison between the IT sector and other Indian sectors.

**HDFCBANK.NS – HDFC Bank:**
HDFC Bank was selected to represent India's banking and financial-services sector. Including a major bank adds sector diversity to the dataset and allows comparisons between financial services, IT and diversified businesses within the Indian market.

**AAPL – Apple:**
Apple was selected as a major US technology company with extensive historical market data and high trading activity. It provides a useful US-market comparison against the three Indian companies and allows analysis of price performance, volume and traded value.

**NVDA – NVIDIA:**
NVIDIA was selected to represent the US semiconductor and artificial-intelligence sector. Its business differs from Apple's despite both being technology-related companies, providing an interesting comparison of price movements, trading volume and volatility within the US market.

**Overall, these five symbols were chosen because they provide coverage of two markets, multiple sectors and established, actively traded companies. This makes the dataset suitable for analysing daily returns, trading volume, traded value, price ranges, price performance and differences between Indian and US equities.**

