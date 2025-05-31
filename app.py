import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ========== 配置路径与规则 ==========
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
SCORE_FILE = os.path.join(DATA_DIR, "score_log_streamlit.csv")

reward_data = {
    "八点前起床": 2, "坚持背单词": 2, "写英语阅读": 2,
    "专业课学习": 1, "回顾昨日学习": 3, "每日学习6小时": 3,
    "每日学习7小时": 5, "每日学习8小时": 7, "每日学习10小时": 9,
    "每日学习12小时": 15, "三餐按规律吃": 3, "锻炼放松": 4,
    "小红书和抖音使用时间低于1.5小时": 8, "淘宝使用时间低于1小时": 2
}
penalty_data = {
    "12点之后睡觉": -5, "英语任务未达标": -2, "专业课任务没达标": -4,
    "没有回顾知识": -1, "总是学习焦虑": -4, "看剧超过1.5小时": -8,
    "每日学习时间低于3小时": -10, "自暴自弃": -20
}

# ========== 初始化与工具函数 ==========
def init_log():
    if not os.path.exists(SCORE_FILE):
        df = pd.DataFrame(columns=["日期", "加分项", "扣分项", "总得分", "累计得分"])
        df.to_csv(SCORE_FILE, index=False)

def get_last_total():
    if os.path.exists(SCORE_FILE):
        df = pd.read_csv(SCORE_FILE)
        if not df.empty:
            return df.iloc[-1]["累计得分"]
    return 0

def save_score(today, rewards, penalties, total, cumulative):
    row = {
        "日期": today,
        "加分项": "，".join(rewards),
        "扣分项": "，".join(penalties),
        "总得分": total,
        "累计得分": cumulative
    }
    df = pd.read_csv(SCORE_FILE)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(SCORE_FILE, index=False)

def plot_trend():
    df = pd.read_csv(SCORE_FILE)
    if df.empty:
        st.warning("暂无数据用于可视化")
        return
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["日期"], df["累计得分"], marker='o', color='blue')
    ax.set_title("📈 累计积分趋势图")
    ax.set_xlabel("日期")
    ax.set_ylabel("累计得分")
    ax.grid(True)
    st.pyplot(fig)

# ========== 主页面 ==========
st.set_page_config(page_title="狗狗考研积分记录系统", layout="wide")

# 欢迎语（居中 + 粉色）
st.markdown(
    "<h2 style='text-align:center; color:#ff69b4;'>🎉 欢迎老婆大人登录系统！</h2>",
    unsafe_allow_html=True
)

st.title("📘 狗狗考研积分记录系统")

init_log()
today = datetime.today().strftime("%Y-%m-%d")
st.markdown(f"**📅 今日日期：** {today}")
st.markdown(f"**💚 当前累计积分：** {get_last_total()} 分")

st.subheader("✅ 加分项")
reward_selected = st.multiselect("请选择完成的加分项：", list(reward_data.keys()))

st.subheader("❌ 扣分项")
penalty_selected = st.multiselect("请选择触发的扣分项：", list(penalty_data.keys()))

if st.button("📥 提交记录"):
    total = sum(reward_data[r] for r in reward_selected) + sum(penalty_data[p] for p in penalty_selected)
    cumulative = get_last_total() + total
    save_score(today, reward_selected, penalty_selected, total, cumulative)
    st.success(f"✅ 今日得分：{total} 分 | 📊 累计积分：{cumulative} 分")

st.markdown("---")
st.subheader("📊 累计积分趋势图")
plot_trend()
