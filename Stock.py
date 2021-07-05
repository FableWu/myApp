import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# st.set_page_config(layout='wide')
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 1000)

today = (datetime.today()-timedelta(days=2)).strftime('%Y%m%d')
minus60 = (datetime.today() - timedelta(days=100)).strftime('%Y%m%d')

starttime = datetime.now()


def filter_alldata():
    word = '新能源|新能源汽车|人工智能|5G'

    pro = ts.pro_api('44fdd46cdf0f953ab7049a703a5b8c0b06347f085875788cb70c495c')

    currentTradeData = pro.daily(trade_date=today)

    stockBasic = pro.stock_basic(fields='ts_code, name, fullname, area, industry, market, exchange, list_status, list_date, delist_date')

    companyData = pro.stock_company(fields='ts_code, manager, reg_capital, setup_date, province, city, introduction, employees, main_business, business_scope')

    bak_basic = pro.bak_basic(trade_date=today, fields='pe, float_share, total_share, total_assets, liquid_assets, fixed_assets, reserved, reserved_pershare,'
                                                       'eps, bvps, pb, undp, per_undp, rev_yoy, profit_yoy, gpr, npr, holder_num')


    basicInfo = pd.merge(stockBasic, companyData, on='ts_code', how='outer')

    allData = pd.merge(currentTradeData, basicInfo, on='ts_code', how='left')

    allData = allData[(allData['market'].isin(['主板']))
                      & (allData['list_status'] == 'L')
                      & (allData['close'] <= 5)
                      & ((allData['name'].str.contains('ST')) == False)
                      & ((allData['introduction'].str.contains(word))
                      | ((allData['business_scope'].str.contains(word)))
                      | ((allData['main_business'].str.contains(word))))]

    allData = allData.sort_values(by=['change'], ascending=False)
    allData.reset_index(drop=True, inplace=True)
    return allData
# allData.to_excel(f'Stock_{today}.xlsx', index=False)

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
    st.table(filter_alldata()[filter_alldata()['ts_code'].isin(filter_list)]['name'].str.strip())
else:
    st.write(filter_alldata())

st.write(f'Time use: {datetime.now() - starttime}')

