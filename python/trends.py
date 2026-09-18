from pytrends_modern import TrendReq

pytrends = TrendReq(hl='pt-BR', tz=360)
suggs = pytrends.suggestions("pydriller")
print(suggs)

pytrends.build_payload(
    kw_list=['/g/11tj6xz8v1'],
    timeframe='all'
)

interest_df = pytrends.interest_over_time()

interest_df.to_csv('outputs/interestFinal.csv')
