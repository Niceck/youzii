import tushare as ts
import pandas as pd
import os
import streamlit as st
import base64

# 设置页面配置
st.set_page_config(page_title="Stock Analysis App", layout="wide")

# 将本地图片转换为 base64 编码
image_path = "yinhe.png"
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# CSS 设置背景图片
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 100vh;
    }}
    </style>
    """, unsafe_allow_html=True
)

# 显示标题
st.title("恢恢数据库")

# 你可以在这里继续添加其他内容，例如数据展示、图表等


# 设置 Pandas 显示选项，确保 '接受机构' 列完全显示
pd.set_option('display.max_colwidth', None)

# 从 secrets.toml 文件中读取 Tushare API Token，使用默认值避免 KeyError
tushare_token = st.secrets.get("api_keys", {}).get("tushare_token", "your_default_token_here")

# 设置 Tushare API Token
ts.set_token(tushare_token)
pro = ts.pro_api()

# 拉取数据
def fetch_data(trade_date, ts_code, hm_name, start_date, end_date, limit, offset=0):
    df = pro.hm_detail(
        trade_date=trade_date,
        ts_code=ts_code,
        hm_name=hm_name,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        fields=["trade_date", "ts_code", "ts_name", "buy_amount", "sell_amount", "net_amount", "hm_name"]
    )
    return df

def main():
    # 用户输入 - 在左侧栏设置输入框
    st.sidebar.title("参数设置")
    trade_date = st.sidebar.text_input("交易日期", "")
    ts_code = st.sidebar.text_input("股票代码", "")
    hm_name = st.sidebar.text_input("游资名称", "")
    start_date = st.sidebar.text_input("开始日期", "")
    end_date = st.sidebar.text_input("结束日期", "")
    limit = st.sidebar.number_input("查询的最大数据条数", min_value=1, value=100)  # 用户输入 limit

    # 查询按钮
    if st.sidebar.button('查询数据'):
        # 拉取数据
        df = fetch_data(trade_date, ts_code, hm_name, start_date, end_date, limit)

        # 检查是否成功获取数据
        if df.empty:
            st.warning("未获取到任何数据。请检查输入参数或网络连接。")
        else:
            # 转换买入金额、卖出金额、净买入金额为单位万（不保留小数）
            df['buy_amount'] = df['buy_amount'] // 10000
            df['sell_amount'] = df['sell_amount'] // 10000
            df['net_amount'] = df['net_amount'] // 10000

            # 重命名列为中文
            df.rename(columns={
                'trade_date': '交易日期',
                'ts_code': '股票代码',
                'ts_name': '股票名称',
                'buy_amount': '买入金额(万)',
                'sell_amount': '卖出金额(万)',
                'net_amount': '净买入金额(万)',
                'hm_name': '游资名称'
            }, inplace=True)

            # 显示数据表格
            st.write("### 游资数据")
            st.dataframe(df, use_container_width=True, hide_index=True)

# 确保脚本以 main() 函数执行
if __name__ == "__main__":
    main()
