import streamlit as st
import dashscope
import datetime

# ==========================================
# 🔒 智能安全配置：云端与本地双兼容模式
try:
    # 尝试从云端的安全保险箱 (Secrets) 中读取 Key
    DASHSCOPE_API_KEY = st.secrets["DASHSCOPE_API_KEY"]
except Exception:
    # ⚠️ 如果是本地运行，找不到保险箱时，会默认使用这里的 Key：
    # 请在下方引号内填入您的真实 API Key（仅供本地测试，上传 GitHub 时记得删掉真实 Key！）
    DASHSCOPE_API_KEY = ""

# 配置 DashScope API Key
dashscope.api_key = DASHSCOPE_API_KEY


# ==========================================

def get_tour_info_with_status(college_name):
    """使用状态容器实时展示 Agent 工作进度"""

    today = datetime.datetime.now()
    current_date_str = today.strftime("%Y年%m月%d日")

    # 创建一个精美的状态容器
    with st.status(f"✨ 正在为您筹备 {college_name} 访校方案...", expanded=True) as status:
        st.write("🔍 正在接入美国教育专线网络...")

        # 1. 构建提示词
        prompt = f"""
        你现在的身份是「美国顶尖名校访校智能顾问(Agent)」。今天是 {current_date_str}。
        请帮我联网深度检索 "{college_name}" 官方本科招生访校(Campus Tour)的最新动态。

        请务必提取并总结以下信息（用中文回答，语气要像一位资深、贴心、鼓励学生的升学导师）：

        1. 🎯 官方直达通道：提供访校预约官网的最直接链接。
        2. 📅 未来三个月排期表：
           请以 Markdown 表格的形式，列出从 {current_date_str} 起，未来三个月内该校官网已公布的访校参观时间。
           - 表格表头：| 目标月份 | 开放频次 / 具体可选日期 | 抢票与备注说明 |
        3. 📝 独家预约攻略（规则解读）：提前多久放票、是否必须注册、候补规则等。

        注意：严禁编造日期。查不到请指引官网步骤。
        """

        st.write(f"🌐 正在深度扫描 {college_name} Admissions 官方数据库...")

        # 2. 调用大模型
        try:
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                enable_search=True  # 开启联网
            )

            if response.status_code == 200:
                st.write("📊 正在提取关键日期并生成排期表...")
                status.update(label="✅ 访校攻略生成完毕！", state="complete", expanded=False)
                return response.output.text
            else:
                status.update(label="❌ 检索遇到一点小麻烦", state="error")
                return f"⚠️ 搜索服务响应异常，请稍后再试或检查 API Key。错误码：{response.code}"

        except Exception as e:
            status.update(label="❌ 系统连接超时", state="error")
            return f"⚠️ 抱歉，Agent 在连接官网时超时了，建议您刷新页面重试一次。"


# ==========================================
# 页面配置与精美 UI 设计
# ==========================================
st.set_page_config(page_title="Top 50 访校规划智能体", page_icon="🎓", layout="wide")

# 注入 CSS
st.markdown("""
<style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1550152145-66170d9bd6bb?auto=format&fit=crop&w=2070&q=80");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(12px);
        padding: 3rem; border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        margin-top: 2rem;
    }
    h1 { color: #A31F34 !important; text-align: center; font-weight: 800; }
    .agent-desc { text-align: center; color: #444; margin-bottom: 2rem; font-size: 1.1rem; }
    .stButton>button {
        background-color: #A31F34; color: white; width: 100%;
        border-radius: 10px; font-weight: bold; height: 3.5rem;
        font-size: 1.2rem; transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #8a1a2c;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

st.title(f"🎓 筑梦名校 · 全美 Top 50 访校规划顾问2026版")
st.markdown('<div class="agent-desc">已为您加载最新的 U.S. News 排名前 50 高校名单，一键开启您的名校探索之旅。</div>',
            unsafe_allow_html=True)

# 完整的 2026 美国综合性大学 Top 50 名单
top_50_colleges = [
    "Princeton University", "Massachusetts Institute of Technology (MIT)",
    "Harvard University", "Stanford University", "Yale University",
    "University of Pennsylvania", "California Institute of Technology (Caltech)",
    "Duke University", "Brown University", "Johns Hopkins University",
    "Northwestern University", "Columbia University", "Cornell University",
    "University of Chicago", "University of California, Berkeley",
    "University of California, Los Angeles (UCLA)", "Rice University",
    "Dartmouth College", "Vanderbilt University", "University of Notre Dame",
    "University of Michigan--Ann Arbor", "Georgetown University",
    "Washington University in St. Louis", "Emory University",
    "University of Virginia", "Carnegie Mellon University",
    "University of Southern California (USC)", "University of California, San Diego",
    "University of Florida", "University of North Carolina at Chapel Hill",
    "Wake Forest University", "Tufts University", "University of California, Santa Barbara",
    "University of California, Irvine", "University of Rochester",
    "Boston College", "Georgia Institute of Technology (Georgia Tech)",
    "University of California, Davis", "William & Mary",
    "University of Texas at Austin", "Boston University",
    "University of Illinois Urbana-Champaign", "University of Wisconsin-Madison",
    "Case Western Reserve University", "University of Georgia",
    "Ohio State University--Columbus", "Purdue University--Main Campus",
    "Santa Clara University", "Lehigh University", "Pepperdine University"
]

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_college = st.selectbox("📌 请选择目标大学 (Top 50)：", top_50_colleges)
    start_search = st.button("🚀 召唤 Agent，生成专属访校攻略")

if start_search:
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "在此处粘贴您的_DASHSCOPE_API_KEY":
        st.error("⚠️ Agent 未激活：请在代码第13行配置您的 API Key，或检查云端 Secrets。")
    else:
        result = get_tour_info_with_status(selected_college)
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 8px solid #A31F34; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 25px;">
            {result}
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.info(
            "💡 **顾问贴士**：热门院校的名额常在几分钟内抢光，建议通过上方官网链接订阅该校的 Admissions Newsletter 获得第一手提醒。"
        "🐷本AI Agent由doctorquan编写，任何问题请致信doctorquan@126.com，祝您马年马到成功🐎")
