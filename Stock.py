import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from functools import reduce

starttime = datetime.now()
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 1000)

selectValue = st.selectbox('Select a day', [0, 1, 2, 3])

today = (datetime.today()-timedelta(days=selectValue)).strftime('%Y%m%d')
minus60 = (datetime.today() - timedelta(days=100)).strftime('%Y%m%d')


def filter_alldata():
    word = '新能源|新能源汽车|人工智能|5G'

    pro = ts.pro_api('44fdd46cdf0f953ab7049a703a5b8c0b06347f085875788cb70c495c')

    gupiaoliebiao = pro.stock_basic(fields='ts_code, name, market')

    beiyongliebiao = pro.bak_basic(trade_date=today, fields='ts_code, pe, float_share, pb')

    rixianhangqing = pro.daily(trade_date=today, fields='ts_code, close')

    companyData = pro.stock_company(fields='ts_code, introduction, main_business, business_scope')

    mergelist = [gupiaoliebiao, beiyongliebiao, rixianhangqing, companyData]

    allData = reduce(lambda left, right: pd.merge(left, right, on='ts_code', how='inner'), mergelist)

    allData = allData[(allData['market'].isin(['主板', '中小板']))
                      & (allData['pe'] > 0)
                      & (allData['pb'] > 0)
                      & (allData['float_share'] < 30)
                      & (allData['close'] <= 10)
                      & ((allData['name'].str.contains('ST')) == False)
                      & ((allData['introduction'].str.contains(word))
                         | ((allData['business_scope'].str.contains(word)))
                         | ((allData['main_business'].str.contains(word))))]

    allData = allData.sort_values(by=['pe'], ascending=False)
    allData.columns.values[1] = 'stock_name'
    allData.reset_index(drop=True, inplace=True)
    return allData

pressed = st.button('Filter')

if pressed:
    filter_list = []
    for ts_code in filter_alldata()['ts_code']:
        ts.set_token('44fdd46cdf0f953ab7049a703a5b8c0b06347f085875788cb70c495c')
        df = ts.pro_bar(ts_code=ts_code, start_date=minus60, end_date=today, ma=[5, 10, 20, 30, 60])
        if (df.loc[df.index[0], 'ma5'] >= df.loc[df.index[0], 'ma10']) and (df.loc[df.index[1], 'ma5'] < df.loc[df.index[1], 'ma10']):
            # print(allData.loc[allData['ts_code'] == ts_code, 'name'].values[0])
            filter_list.append(ts_code)
    st.dataframe(filter_alldata()[filter_alldata()['ts_code'].isin(filter_list)])
else:
    st.write(filter_alldata())

st.write(f'Time use: {datetime.now() - starttime}')
