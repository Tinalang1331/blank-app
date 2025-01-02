import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# 設定應用標題
st.title("處理生物出現資料：檢查格式及視覺化")

# 格式化學名的函數
def standardize_species(scientific_name):
    if pd.notna(scientific_name):
        return scientific_name.strip().title()
    return scientific_name

# 處理日期格式的函數
def extract_year_month(eventDate):
    if pd.isna(eventDate):
        return None, None
    
   # 支援的日期格式
    formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%Y.%m.%d']
    
    for fmt in formats:
        try:
            # 嘗試用指定格式解析日期
            date_obj = datetime.strptime(str(eventDate), fmt)
            
            # 返回標準化的日期格式 (%Y-%m-%d)
            standardized_date = date_obj.strftime('%Y-%m-%d')
            return date_obj.year, date_obj.month    
        except ValueError:
            continue
    
    # 如果所有格式都無法匹配，返回 None
    return None, None

# 上傳檔案元件
uploaded_file = st.file_uploader("請上傳 CSV 檔案", type="csv")

error = False

if uploaded_file is not None:
    # 讀取 CSV 檔案內容
    df = pd.read_csv(uploaded_file)
    
    # 格式化學名
    df['scientificName'] = df['scientificName'].apply(standardize_species)

    # empty轉換為空字串
    df.replace("", np.nan, inplace=True)

    # 移除ScientificName=None的rows
    df = df[df['scientificName'].notnull()]
    df['year'] = df['year'].apply(lambda x: str(int(x)) if pd.notna(x) else x)
    st.write(df)

    # 處理沒有eventDate的資料
    if df['eventDate'].isnull().any():
        st.warning("eventDate 欄位有空值，請檢查資料是否完整!")         
        error = True
        if 'year' in df.columns and 'month' in df.columns and 'day' in df.columns:
            if df['year'].isnull().any() or df['month'].isnull().any() or df['day'].isnull().any():
                st.warning("請確認每筆資料是否有日期欄位且無缺漏值!")         
                error = True

            elif df['year'].notna().all() and df['month'].notna().all() and df['day'].notna().all():
                df['eventDate'] = df['year'].astype(str) + '-' + df['month'].astype(str) + '-'+ df['day'].astype(str)
                df.drop(columns=['year', 'month', 'day'], inplace=True)
        else:
             # 如果 year, month, day 欄位缺少任何一個
            st.warning("缺少年、月或日欄位，無法建立 eventDate，請確保年、月、日欄位不是空值!")
            error = True

     # # 如果有無效值，提示錯誤訊息
    # if not invalid_dates.empty:
    #     st.warning("以下日期格式有誤，請確認日期格式是否正確：")
    #     st.dataframe(invalid_dates[['eventDate']])
    #     st.error("提示：正確的日期格式應該為 'YYYY.MM.DD', 'YYYY/MM/DD' 或 'YYYYMMDD'。")
    # else:
    #     st.success("所有日期均已正確解析！")

    if not error:
        # 處理日期
        # df['year'], df['month'] = zip(*df['eventDate'].apply(extract_year_month))
        
        # 確保日期欄位為字串並取出年份
        df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')
        df['year'] = df['eventDate'].dt.year

        # 計算每個年份的出現次數
        yearly_counts = df['year'].value_counts().sort_index()

        # 建立長條圖
        st.title("Event Yearly Data Visualization")
        st.write("每年數據累計圖:") # Yearly Count

        # 使用Plotly繪製長條圖
        # 使用 Plotly 繪製長條圖
        fig = px.bar(
            x=yearly_counts.index,
            y=yearly_counts.values,
            labels={'x': 'Year', 'y': 'Number of Records'},
            title='Yearly Data Counts',
            text=yearly_counts.values  # 在每個柱上顯示數值
        )
        
        # 移除鼠標的文字顯示
        fig.update_traces(
            hovertemplate = 'Year=%{x}<br>Number of Records=%{y}<extra></extra>'
        )

        # 設定 X 軸和 Y 軸刻度為正整數
        fig.update_xaxes(type='category')  # X 軸：顯示年份
        fig.update_yaxes(
            dtick=int(max(yearly_counts.values)/10) if max(yearly_counts.values)>10 else 1,  # Y 軸：正整數刻度，從零開始
            rangemode = 'tozero'  # Y 軸：從零開始
        )# Y 軸：根據數據範圍計算合理的刻度間隔
        
        # 設定長條圖寬度一致
        fig.update_layout(
            bargap=0.2, # 長條間隙，值越小，長條越寬（0.2 為適中間隔）
            bargroupgap=0 # 長條組間無間隙
        )

        # 顯示圖表
        st.plotly_chart(fig)

        # 顯示數據表
        st.write("數據表:")
        st.dataframe(yearly_counts)


    # 確保 individualCount 是數字，並填補缺失值
    # df['individualCount'] = pd.to_numeric(df['individualCount'], errors='coerce').fillna(0)
    
    # 檢查是否有無效值
    # invalid_dates = df[df['year'].isna()]

    # 確保 year 和 month 欄位以整數表示（處理無效值）
    # df['year'] = df['year'].apply(lambda x: int(x) if pd.notna(x) else None)
    # df['month'] = df['month'].apply(lambda x: int(x) if pd.notna(x) else None)


   
    # # 顯示原始資料
    # st.write("原始資料：")
    # st.dataframe(df)

    # # 選擇要修改的行與欄
    # row_to_edit = st.selectbox("選擇要修改的行", df.index)
    # column_to_edit = st.selectbox("選擇要修改的欄", df.columns)
    
    # # 提供修改介面
    # new_value = st.text_input("重新命名學名", value=df.loc[row_to_edit, column_to_edit])

    # # 更新資料
    # if st.button("更新資料"):
    #     df.loc[row_to_edit, column_to_edit] = new_value
    #     st.success("資料已更新!")

    # # 顯示更新後的資料
    # st.subheader("更新後的資料：")
    # st.dataframe(df)

    # 根據 scientificName 分組並繪製圖表
    #grouped = df.groupby("scientificName")
    
#     for name, group in df:
#         if not group.empty:
#              # 補充缺失月份（1-12）
#             all_months = pd.DataFrame({'year': range(1, 13)})
#             group = pd.merge(all_months, group, on='month', how='left').fillna(0)
            
#             # 樞紐表
#             pivot_table = group.pivot_table(
#                 index='month', 
#                 columns='year', 
#                 values='individualCount', 
#                 aggfunc='sum', 
#                 fill_value=0
#             )
#             st.write("檢查樞紐表：", pivot_table)

#             # 過濾掉年份為 0 的數據
#             pivot_table = pivot_table.drop(columns=[0], errors='ignore')  # 移除包含年份 0 的列

#             # 去除年份的小數點，確保年份為整數
#             pivot_table.columns = [int(col) for col in pivot_table.columns]

#             # 繪製長條圖
#             fig = px.bar(
#                 pivot_table,
#                 title=f"{name} 出現次數圖",
#                 labels={
#                     "value": "出現次數",
#                     "month": "月份",
#                     "variable": "年份"
#                 },
#                 barmode="stack"
#             )
#             # 設定 x 和 y 軸刻度格式
#             fig.update_layout(
#                 xaxis=dict(tickformat=".0f"),
#                 yaxis=dict(tickformat=".0f")
#             )
#             # 確保月份完整 (1-12 月份)
#             pivot_table = pivot_table.reindex(range(1, 13), fill_value=0)
            
#             print(group['individualCount'])  # 檢查 individualCount 內容
#             max_y = max(group['individualCount'])  # 找出最大值

#             # 設定 dtick 為 1、5 或 10 中的一個合適數值
#             if max_y > 50:
#                 dtick = 10
#             elif max_y > 15:
#                 dtick = 5
#             else:
#                 dtick = 1


#             # 避免月份重複，固定月份順序
#             fig.update_layout(
#                 xaxis=dict(
#                     fixedrange=True,  # 禁止縮放 X 軸範圍
#                     tickmode='array',
#                     tickvals=list(range(1, 13)),  # 固定 x 軸的刻度值
#                     ticktext=[str(i) for i in range(1, 13)],  # 以 1-12 作為月份標籤
#                     range=[0.5, 12.5],  # 固定 X 軸範圍為 1 到 12
#                     dtick=1,
#                 ),
#                 yaxis=dict(
#                     title="出現次數",
#                     dtick=dtick,  # 設定刻度間隔為 1，避免重複
#                     range=[0, max_y + (dtick - (max_y % dtick))],  # 動態範圍
                    
#                     #automargin=True,  # 自動調整邊距
#                     #autorange=True,   # 自動設定範圍
                   
#                 ),
#                 bargap=0.2,  # 控制條形之間的間距
#                 width=800,  # 圖表寬度
#                 height=600  # 圖表高度
                
#             )
            
#             # 更新圖例，移除不必要的項目
#             fig.for_each_trace(lambda t: t.update(name=str(int(t.name)) if t.name.isdigit() else t.name))
#             # 顯示圖表
#             st.plotly_chart(fig)
# else:
#     st.info("請上傳檔案以檢視內容。")



# # 建立 Tab
# tab1, tab2 = st.tabs(["上傳資料", "檢查格式及視覺化"])

# with tab1:
#     st.write("上傳資料")

# with tab2:
#     st.write("檢查格式及視覺化")

