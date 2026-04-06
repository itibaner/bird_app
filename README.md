鸟类迁徙空间分析雷达是一个基于 Python 和 Streamlit 构建的轻量级交互式 Web 应用。它通过对接全球生物多样性信息网络 (GBIF) 的开放 API，帮助观鸟爱好者、生态学者及自然摄影师快速分析特定地理区域内目标鸟类的历史活跃规律，并智能推算最佳观测期。

在线体验 (Live Demo)
无需安装任何环境，直接在浏览器中访问使用：
https://birdapp-itibaner.streamlit.app/

核心功能
交互式空间选点：告别死板的下拉菜单，直接在 Folium 地图上点击目标区域作为分析中心。
自定义探测半径：支持设定 10km 到 200km 的动态搜索半径，精准圈定分析范围。
活跃期智能预测：自动拉取多年历史记录，利用季节性分布算法推算该区域的“最高发月份”与“最佳综合观测期”。
热点地点挖掘：自动清洗底层数据，提取并推荐该范围内排名前列的具体目击地名 (Hotspots)。
可视化图表：直观展示 1到12月活跃度柱状分布图及具体目击坐标热力图。

本地运行指南
如果你想在本地机器上运行此项目：

克隆本仓库到本地。

安装所需依赖，在命令行输入：pip install -r requirements.txt

启动 Streamlit 服务，在命令行输入：streamlit run bird_app.py

Bird Migration Spatial Radar is a lightweight, interactive web application built with Python and Streamlit. By integrating with the Global Biodiversity Information Facility (GBIF) API, it helps birdwatchers, ecologists, and nature photographers quickly analyze the historical activity patterns of target bird species in specific geographic areas and intelligently predict the best observation periods.

Live Demo
No installation required. Access the application directly in your browser:
https://birdapp-itibaner.streamlit.app/

Key Features
Interactive Spatial Selection: Click directly on the Folium map to set your target analysis center.
Custom Search Radius: Dynamically adjust the search radius from 10km to 200km for precise localized analysis.
Active Period Prediction: Automatically fetches historical occurrence data and calculates the "Peak Month" and "Best Observation Period" based on seasonal distribution algorithms.
Hotspot Detection: Cleans occurrence data to extract and recommend the top specific observation localities (Hotspots) within the selected range.
Data Visualization: Intuitive 1-12 month activity bar charts and historical sighting heatmaps.

How to Run Locally
If you want to run this project on your local machine:

Clone this repository.

Install the required dependencies by running: pip install -r requirements.txt

Run the Streamlit app by running: streamlit run bird_app.py
