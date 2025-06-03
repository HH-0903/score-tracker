import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ========== 配置路径与文件 ==========
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
SCORE_FILE = os.path.join(DATA_DIR, "score_log_streamlit.csv")

# ========== 加分项与扣分项 ==========
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

# ========== 初始化 CSV 文件 ==========
def init_log():
    if not os.path.exists(SCORE_FILE):
        df = pd.DataFrame(columns=["日期", "加分项", "扣分项", "总得分", "累计得分"])
        df.to_csv(SCORE_FILE, index=False)

# ========== 读取前一日累计积分 ==========
def get_last_total():
    if os.path.exists(SCORE_FILE):
        df = pd.read_csv(SCORE_FILE)
        if not df.empty:
            return df.iloc[-1]["累计得分"]
    return 0

# ========== 写入 / 更新当日记录 ==========
def update_or_append_score(today, rewards, penalties, total, cumulative):
    if os.path.exists(SCORE_FILE):
        df = pd.read_csv(SCORE_FILE)
    else:
        df = pd.DataFrame(columns=["日期", "加分项", "扣分项", "总得分", "累计得分"])

    if today in df["日期"].values:
        idx = df[df["日期"] == today].index[-1]
        df.at[idx, "加分项"] += "，" + "，".join(rewards)
        df.at[idx, "扣分项"] += "，" + "，".join(penalties)
        df.at[idx, "总得分"] += total
        df.at[idx, "累计得分"] = cumulative
    else:
        new_row = {
            "日期": today,
            "加分项": "，".join(rewards),
            "扣分项": "，".join(penalties),
            "总得分": total,
            "累计得分": cumulative
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(SCORE_FILE, index=False)

# ========== 绘制趋势图 ==========
def plot_trend():
    df = pd.read_csv(SCORE_FILE)
    if df.empty:
        st.warning("暂无数据用于可视化")
        return
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["日期"], df["总得分"], marker='o', label="每日得分", color='orange')
    ax.plot(df["日期"], df["累计得分"], marker='o', label="累计得分", color='blue')
    ax.set_title("📈 每日得分与累计得分趋势图")
    ax.set_xlabel("日期")
    ax.set_ylabel("得分")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# ========== 主程序 ==========
st.set_page_config(page_title="狗狗考研积分记录系统", layout="wide")
st.title("📘 狗狗考研积分记录系统")
st.markdown("### 💖 欢迎老婆大人登录系统 💖")

init_log()
today = datetime.today().strftime("%Y-%m-%d")
st.markdown(f"**📅 今日日期：** {today}")
st.markdown(f"**💚 当前累计积分：** {get_last_total()} 分")

# 选择项
st.subheader("✅ 加分项")
reward_selected = st.multiselect("请选择完成的加分项：", list(reward_data.keys()))

st.subheader("❌ 扣分项")
penalty_selected = st.multiselect("请选择触发的扣分项：", list(penalty_data.keys()))

# 提交记录
if st.button("📥 提交记录"):
    total = sum(reward_data[r] for r in reward_selected) + sum(penalty_data[p] for p in penalty_selected)
    cumulative = get_last_total() + total
    update_or_append_score(today, reward_selected, penalty_selected, total, cumulative)

    df_all = pd.read_csv(SCORE_FILE)
    history_total = df_all["总得分"].sum()

    st.success(f"✅ 今日得分：{total} 分 | 🧮 今日前累计：{cumulative - total} 分 | 📊 当前累计积分：{cumulative} 分")
    st.info(f"📌 所有历史总得分（含今日）：{history_total} 分")

# 图表
st.markdown("---")
st.subheader("📊 每日与累计积分趋势图")
plot_trend()
