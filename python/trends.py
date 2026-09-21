from pytrends_modern import TrendReq


def get_trends(output_file, term):    
    pytrends = TrendReq()
    kw = term
    for suggestion in pytrends.suggestions(term):
        if suggestion["title"] == term:
            kw = suggestion["mid"]
            break

    pytrends.build_payload(
        kw_list=[kw],
        timeframe='all'
    )

    df = pytrends.interest_over_time()
    df = df[df.isPartial == False]
    df.rename(columns={kw: "count"}, inplace=True)
    df.to_csv(output_file)
