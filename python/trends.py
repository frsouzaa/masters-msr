from pytrends_modern import TrendReq

pytrends = TrendReq(hl='pt-BR', tz=360)
pytrends.build_payload(
    kw_list=['react'],
    timeframe='today 5-y',
    geo='',
    cat=1227,
)

interest_df = pytrends.interest_over_time()

interest_df.to_csv('interest_over_time.csv')
