import streamlit as st
import pandas as pd
import requests
import numpy as np
import folium
from streamlit_folium import st_folium
import math

# ==========================================
# 页面基础设置
# ==========================================
st.set_page_config(page_title="GBIF 鸟类迁徙预测雷达", page_icon="🌍", layout="wide")
st.title("🌍 鸟类迁徙交互式空间雷达 (基于 GBIF)")

# ==========================================
# 1. 侧边栏：鸟种选择与半径设置
# ==========================================
st.sidebar.header("⚙️ 目标设置")

birds = {
    "黑尾鸥 (Larus crassirostris)": "Larus crassirostris",
    "红嘴鸥 (Chroicocephalus ridibundus)": "Chroicocephalus ridibundus",
    "遗鸥 (Ichthyaetus relictus)": "Ichthyaetus relictus",
    "银鸥 (Larus argentatus)": "Larus argentatus",
    "苍鹭 (Ardea cinerea)": "Ardea cinerea",
    "大白鹭 (Ardea alba)": "Ardea alba",
    "绿头鸭 (Anas platyrhynchos)": "Anas platyrhynchos",
    "戴胜 (Upupa epops)": "Upupa epops",
    "喜鹊 (Pica pica)": "Pica pica",
    "✨ 自定义输入拉丁文学名...": "custom"
}
selected_bird_name = st.sidebar.selectbox("🦅 选择目标鸟种", list(birds.keys()))

if birds[selected_bird_name] == "custom":
    scientific_name = st.sidebar.text_input("✏️ 请输入鸟类拉丁文学名", "Passer montanus")
    display_bird_name = scientific_name
else:
    scientific_name = birds[selected_bird_name]
    display_bird_name = selected_bird_name

# 新增：自定义搜索半径
radius_km = st.sidebar.slider("🎯 搜索半径 (公里)", min_value=10, max_value=200, value=50, step=10)

st.sidebar.info("💡 请在右侧的地图上**点击任意位置**来设定搜索中心点！")

# ==========================================
# 2. 核心分析函数：包含空间计算与深度分析
# ==========================================
@st.cache_data(ttl=3600)
def analyze_bird_data(lat, lon, radius, scientific_name):
    # 根据半径 (km) 近似计算经纬度的范围 (1纬度度数约等于111km)
    lat_offset = radius / 111.0
    lon_offset = radius / (111.0 * math.cos(math.radians(lat)))
    
    lat_min, lat_max = lat - lat_offset, lat + lat_offset
    lon_min, lon_max = lon - lon_offset, lon + lon_offset 
    
    url = "https://api.gbif.org/v1/occurrence/search"
    params = {
        "scientificName": scientific_name,
        "decimalLatitude": f"{lat_min},{lat_max}",
        "decimalLongitude": f"{lon_min},{lon_max}",
        "hasCoordinate": "true",
        "limit": 500 # 提高上限以支持更精准的分析
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, "API 请求失败，请检查网络。"
    
    data = response.json().get('results', [])
    if not data:
        return None, f"在选定点周围 {radius}km 范围内，没有找到 {scientific_name} 的记录。"
        
    cleaned_data = []
    for item in data:
        if 'eventDate' in item and 'decimalLatitude' in item and 'decimalLongitude' in item:
            count = item.get('individualCount', 1) 
            cleaned_data.append({
                'Date': str(item['eventDate'])[:10],
                'lat': item['decimalLatitude'],
                'lon': item['decimalLongitude'],
                'howMany': count,
                # 尽量获取具体的地点名称，若无则标记为空
                'locality': item.get('locality', '').strip() 
            })
            
    df = pd.DataFrame(cleaned_data)
    if df.empty:
        return None, "获取到的数据缺乏有效的日期信息。"

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    if df.empty:
         return None, "经过清洗，没有找到包含完整日期的有效记录。"

    # --- 深度分析模块 ---
    df['Month'] = df['Date'].dt.month
    monthly_counts = df.groupby('Month')['howMany'].sum().reindex(range(1, 13), fill_value=0)
    
    peak_month = int(monthly_counts.idxmax())
    peak_count = monthly_counts.max()
    threshold = peak_count * 0.2
    best_months_list = monthly_counts[monthly_counts >= threshold].index.tolist()
    best_period_str = "、".join([f"{m}月" for m in best_months_list]) if best_months_list else "暂无明显规律"
    
    total_count = df['howMany'].sum()
    
    # 推荐观测地点分析 (过滤掉空字符串和无意义的词)
    valid_localities = df[df['locality'] != '']
    if not valid_localities.empty:
        # 按照出现次数排行
        top_spots = valid_localities['locality'].value_counts().head(3).index.tolist()
        top_spots_str = " \n ".join([f"📍 {spot}" for spot in top_spots])
    else:
        top_spots_str = "该区域的历史记录未提供具体的坐标地名，建议参考右侧热力图。"
    
    return {
        "raw_data": df,
        "peak_month": f"{peak_month}月",
        "best_period": best_period_str,
        "total_count": int(total_count),
        "top_spots": top_spots_str,
        "monthly_chart_data": monthly_counts
    }, "success"

# ==========================================
# 3. 主界面布局：交互式地图 + 结果分析
# ==========================================
col_map_input, col_results = st.columns([1, 1.2])

with col_map_input:
    st.write("### 📌 第 1 步：在地图上选择中心点")
    # 初始化地图，默认中心设在中国中部
    m = folium.Map(location=[35.0, 105.0], zoom_start=4)
    # 开启地图点击获取坐标功能
    m.add_child(folium.LatLngPopup())
    
    # 渲染地图并捕获用户的点击动作
    map_data = st_folium(m, width=500, height=400)
    
    # 获取用户点击的坐标
    if map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]
        st.success(f"已锁定坐标: 纬度 {clicked_lat:.4f}, 经度 {clicked_lon:.4f}")
    else:
        clicked_lat, clicked_lon = None, None
        st.info("👆 请点击上方地图中的任意位置。")

with col_results:
    st.write("### 📊 第 2 步：深度分析结果")
    
    if clicked_lat and clicked_lon:
        if st.button("🚀 开始扫描该区域", type="primary", use_container_width=True):
            with st.spinner(f"正在扫描坐标周边 {radius_km}km 范围..."):
                result, status = analyze_bird_data(clicked_lat, clicked_lon, radius_km, scientific_name)
                
                if status == "success":
                    # --- 核心数据指标卡片 ---
                    c1, c2 = st.columns(2)
                    c1.metric("🦅 范围内历史总记录", f"{result['total_count']} 只")
                    c2.metric("🔥 观测最高发月份", result["peak_month"])
                    
                    st.info(f"**🗓️ 综合推荐观测期：** {result['best_period']}")
                    
                    # --- 智能推荐地点 ---
                    st.write("**🏆 基于大数据的绝佳观测点 (Hotspots)：**")
                    st.markdown(result["top_spots"])
                    
                    st.divider()
                    
                    # --- 历史数据可视化 ---
                    st.write(f"**📈 {display_bird_name} 1-12月活跃度曲线**")
                    st.bar_chart(result["monthly_chart_data"])
                    
                    # 在结果区再画一个小图展示具体的散点
                    st.write("**📍 范围内具体目击分布**")
                    st.map(result["raw_data"][['lat', 'lon']].dropna(), zoom=9)
                else:
                    st.error(status)
    else:
        st.warning("等待地图选点...")