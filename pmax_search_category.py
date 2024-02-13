import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
st.set_page_config(layout="wide")
@st.cache_data(ttl=2400)
def load_and_process_data():
    # 创建连接
    ads_url = 'https://docs.google.com/spreadsheets/d/1mGC0dzOrTjp9m2K-EB7TIVe-MPLKwP3JVx4HRpJtx4k/edit#gid=0'
    conn = st.connection("gsheets", type=GSheetsConnection)
    days30_soure = conn.read(spreadsheet=ads_url, ttl="25m", worksheet=0)
    days30 = pd.DataFrame(days30_soure)
    days30 = days30.dropna(subset=['search category'], how='all')
    compare_days30_soure = conn.read(spreadsheet=ads_url, ttl="25m", worksheet=927351613)
    compare_days30 = pd.DataFrame(compare_days30_soure)
    compare_days30 = compare_days30.dropna(subset=['search category'], how='all')
    days7_soure = conn.read(spreadsheet=ads_url, ttl="25m", worksheet=892918692)
    days7 = pd.DataFrame(days7_soure)
    days7 = days7.dropna(subset=['search category'], how='all')
    compare_days7_soure = conn.read(spreadsheet=ads_url, ttl="25m", worksheet=597205253)
    compare_days7 = pd.DataFrame(compare_days7_soure)
    compare_days7 = compare_days7.dropna(subset=['search category'], how='all')
    return days30,days7,compare_days30,compare_days7

@st.cache_data(ttl=2400)
def data_process_ads(df):
    df.loc[df['currency'] == 'HKD', 'value'] *= 0.127
    df = df.drop(columns=['currency'])
    return df

def calculate_percentage_difference(current, previous):
    if previous == 0:
        return float(0) if current != 0 else 0
    else:
        return (current - previous) / previous * 100

def create_data_compare_data(df,now_metrics,previous_metrics):
    df = df.apply(lambda x: calculate_percentage_difference(x[now_metrics], x[previous_metrics]), axis=1)
    return df

@st.cache_data(ttl=2400)
def create_dynamic_column_setting(raw_select_df, avoid_list, barlist,percentage_list,int_list):
    column_config = {}
    for column in raw_select_df.columns:
        if column in avoid_list:
            continue
        elif column in percentage_list:  # 百分比格式
            raw_select_df[column] = raw_select_df[column]
            if raw_select_df[column].empty:
                max_value = 100
            else:
                max_value = float(raw_select_df[column].max())
            column_config[column] = st.column_config.ProgressColumn(
                format='%.2f%%',  # 显示为百分比
                min_value=0,
                max_value=max_value,
                label=column,
                width = 'small'
            )
        elif column in barlist:
            if raw_select_df[column].empty:
                max_value = 1
            else:
                max_value = float(raw_select_df[column].max())
            column_config[column] = st.column_config.ProgressColumn(
                format='%.2f',
                min_value=0,
                max_value=max_value,
                label=column,
                width='small'
            )
        elif column in int_list:
            if raw_select_df[column].empty:
                max_value = 1
            else:
                max_value = float(raw_select_df[column].max())
            column_config[column] = st.column_config.ProgressColumn(
                format='%d',
                min_value=0,
                max_value=max_value,
                label=column,
                width='small'
            )
        else:  # 其它列的正常处理
            column_config[column] = st.column_config.BarChartColumn(
                width='small'
            )
    return column_config

days30,days7,compare_days30,compare_days7 = load_and_process_data()
process_days30 = data_process_ads(days30)
process_days7 = data_process_ads(days7)
process_compare_days30 = data_process_ads(compare_days30)
process_compare_days7 = data_process_ads(compare_days7)
process_days30 = process_days30.rename(columns={'impression': '30day_impression', 'click': '30day_click',
                'conversion': '30day_conversion','value': '30day_value'})
process_days7 = process_days7.rename(columns={'impression': '7day_impression', 'click': '7day_click',
                'conversion': '7day_conversion','value': '7day_value'})
process_compare_days30 = process_compare_days30.rename(columns={'impression': 'previous_30day_impression', 'click': 'previous_30day_click',
                'conversion': 'previous_30day_conversion','value': 'previous_30day_value'})
process_compare_days7 = process_compare_days7 .rename(columns={'impression': 'previous_7day_impression', 'click': 'previous_7day_click',
                'conversion': 'previous_7day_conversion','value': 'previous_7day_value'})
unique_camapign = process_days7['campaign'].unique()
campaign_options = st.multiselect(
    '广告系列',
    unique_camapign
)

campaign_selected_days7_df = process_days7[process_days7['campaign'].isin(campaign_options)]
compare_campaign_selected_days7_df = process_compare_days7[process_compare_days7['campaign'].isin(campaign_options)]
campaign_selected_days30_df = process_days30[process_days30['campaign'].isin(campaign_options)]
compare_campaign_selected_days30_df = process_compare_days30[process_compare_days30['campaign'].isin(campaign_options)]
combine_campaign_selected_days7_df = pd.merge(campaign_selected_days7_df,compare_campaign_selected_days7_df[['campaign','search category','previous_7day_impression','previous_7day_click','previous_7day_conversion','previous_7day_value']],on=['campaign','search category'],how='left')
combine_campaign_selected_days30_df = pd.merge(campaign_selected_days30_df,compare_campaign_selected_days30_df[['campaign','search category','previous_30day_impression','previous_30day_click','previous_30day_conversion','previous_30day_value']],on=['campaign','search category'],how='left')


combine_campaign_selected_days7_df['impression_diff_7day_percentage']  = create_data_compare_data(combine_campaign_selected_days7_df,'7day_impression','previous_7day_impression')
combine_campaign_selected_days7_df['click_diff_7day_percentage']  = create_data_compare_data(combine_campaign_selected_days7_df,'7day_click','previous_7day_click')
combine_campaign_selected_days7_df['conversion_diff_7day_percentage']  = create_data_compare_data(combine_campaign_selected_days7_df,'7day_conversion','previous_7day_conversion')
combine_campaign_selected_days7_df['value_diff_7day_percentage']  = create_data_compare_data(combine_campaign_selected_days7_df,'7day_value','previous_7day_value')
combine_campaign_selected_days7_df = combine_campaign_selected_days7_df.fillna(0)

combine_campaign_selected_days30_df['impression_diff_30day_percentage']  = create_data_compare_data(combine_campaign_selected_days30_df,'30day_impression','previous_30day_impression')
combine_campaign_selected_days30_df['click_diff_30day_percentage']  = create_data_compare_data(combine_campaign_selected_days30_df,'30day_click','previous_30day_click')
combine_campaign_selected_days30_df['conversion_diff_30day_percentage']  = create_data_compare_data(combine_campaign_selected_days30_df,'30day_conversion','previous_30day_conversion')
combine_campaign_selected_days30_df['value_diff_30day_percentage']  = create_data_compare_data(combine_campaign_selected_days30_df,'30day_value','previous_30day_value')
combine_campaign_selected_days30_df = combine_campaign_selected_days30_df.fillna(0)

column_config_7days  = create_dynamic_column_setting(combine_campaign_selected_days7_df, ['campaign','search category'],['7day_conversion','previous_7day_conversion','7day_value','previous_7day_value'],
                                               ['impression_diff_7day_percentage','click_diff_7day_percentage','conversion_diff_7day_percentage','value_diff_7day_percentage'],['7day_impression','previous_7day_impression','7day_click','previous_7day_click'])

column_config_30days  = create_dynamic_column_setting(combine_campaign_selected_days30_df, ['campaign','search category'],['30day_conversion','previous_30day_conversion','30day_value','previous_30day_value'],
                                               ['impression_diff_30day_percentage','click_diff_30day_percentage','conversion_diff_30day_percentage','value_diff_30day_percentage'],['30day_impression','previous_30day_impression','30day_click','previous_30day_click'])

st.subheader('7天趋势')
metrics_options_7days = st.multiselect(
    '选择维度',
    combine_campaign_selected_days7_df.columns,
    ['search category','7day_impression','previous_7day_impression','impression_diff_7day_percentage','click_diff_7day_percentage','conversion_diff_7day_percentage','value_diff_7day_percentage']
)
st.dataframe(combine_campaign_selected_days7_df[metrics_options_7days],
             column_config=column_config_7days,
             width=1600,height=400)

st.subheader('30天趋势')
metrics_options_30days = st.multiselect(
    '选择维度',
    combine_campaign_selected_days30_df.columns,
    ['search category','30day_impression','previous_30day_impression','impression_diff_30day_percentage','click_diff_30day_percentage','conversion_diff_30day_percentage','value_diff_30day_percentage']
)
st.dataframe(combine_campaign_selected_days30_df[metrics_options_30days],
             column_config=column_config_30days,
             width=1600,height=400)
