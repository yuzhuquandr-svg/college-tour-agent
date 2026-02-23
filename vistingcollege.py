import streamlit as st
import dashscope
import datetime

# ==========================================
# 🔒 安全升级：从云端配置 (Secrets) 中读取 API Key，绝不在代码里明文暴露！
if "DASHSCOPE_API_KEY" in st.secrets:
    DASHSCOPE_API_KEY = st.secrets["DASHSCOPE_API_KEY"]
else:
    DASHSCOPE_API_KEY = ""  # 如果没配置，则留空，下方 UI 会提示报错

# 配置 DashScope API Key
dashscope.api_key = DASHSCOPE_API_KEY


# ==========================================

def get_tour_info(college_name):
    """直接调用通义千问原生自带的联网搜索功能，要求返回三个月内的表格排期"""

    # 自动获取当前的精确系统日期
    today = datetime.datetime.now()
    current_date_str = today.strftime("%Y年%m月%d日")

    # 1. 构建提示词，注入 Agent 人设并明确输出格式
    prompt = f"""
    你现在的身份是「美国顶尖名校访校智能顾问(Agent)」。今天是 {current_date_str}。
    请帮我联网深度检索 "{college_name}" 官方本科招生访校(Campus Tour)的最新动态。

    请务必提取并总结以下信息（用中文回答，语气要像一位资深、贴心、鼓励学生的升学导师，尽量使用最新的搜索结果）：

    1. 🎯 官方直达通道：提供访校预约官网的最直接链接。

    2. 📅 未来三个月排期表：
       请以 Markdown 表格的形式，详细列出从 {current_date_str} 起，未来三个月内该校官网已公布或常规开放的访校参观时间。
       - 表格表头必须为：| 目标月份 | 开放频次 / 具体可选日期 | 抢票与备注说明 |
       - 结合搜索结果，明确填入具体日期；若是滚动开放（如提前30天），请指导家长具体的“抢票日”推算；若未公布，请如实注明“暂未公布，建议持续关注”。

    3. 📝 独家预约攻略（规则解读）：
       例如：提前多久放票、名额紧张程度、是否必须学生本人注册账号、是否允许候补(Waitlist)、到访当天的 Check-in 要求等。

    注意：作为专业顾问，绝不可编造任何虚假日期。如果查不到确切排期，请安抚家长的焦虑，并明确给出官网查询的步骤指引。
    """

    # 2. 调用大模型 (接入阿里云 DashScope 通义千问)
    try:
        response = dashscope.Generation.call(
            model='qwen-plus',
            prompt=prompt,
            enable_search=True
        )

        if response.status_code == 200:
            return response.output.text
        else:
            return f"⚠️ API 请求异常: {response.code} - {response.message}"

    except Exception as e:
        return f"⚠️ 系统发生内部错误 ({str(e)})，请检查网络或 API Key 是否正确。"


# ==========================================
# 页面配置与精美 UI 设计 (Agent 视觉重构)
# ==========================================
st.set_page_config(
    page_title="Top 50 访校规划智能体",
    page_icon="🎓",
    layout="wide"
)

# 注入自定义 CSS：MIT 校园背景 + 毛玻璃面板 + MIT 枢机红主题色
custom_css = """
<style>
    /* 全局背景图：采用高质量的大学校园(类似MIT风格)图片 */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1550152145-66170d9bd6bb?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 毛玻璃效果的主内容区 */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.88); /* 88% 白色透明度 */
        backdrop-filter: blur(12px); /* 磨砂玻璃模糊度 */
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* 标题样式：使用 MIT 枢机红 (#A31F34) */
    h1 {
        color: #A31F34 !important;
        font-weight: 800 !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* 描述文字和副标题增强 */
    .agent-desc {
        text-align: center;
        font-size: 1.15rem;
        color: #333333;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    /* 优化下拉框和按钮 */
    .stSelectbox label {
        font-size: 1.1rem !important;
        font-weight: bold;
        color: #1a1a1a;
    }

    /* 查询按钮样式重写 */
    .stButton>button {
        background-color: #A31F34;
        color: white;
        font-size: 1.1rem;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #8a1a2c;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(163, 31, 52, 0.4);
    }

    /* 表格样式优化，使其更具可读性 */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    th {
        background-color: #A31F34 !important;
        color: white !important;
        text-align: left;
        padding: 12px;
    }
    td {
        padding: 12px;
        border-bottom: 1px solid #ddd;
    }
    tr:hover {
        background-color: #f5f5f5;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 页面内容与交互逻辑
# ==========================================

current_year = datetime.datetime.now().year
st.title(f"🎓 筑梦名校 · 访校规划智能顾问 ({current_year})")

st.markdown("""
<div class="agent-desc">
    欢迎来到您的专属升学规划站！本智能体(Agent)直连全网最新公开数据，<br>
    帮助家长和同学们告别信息差，<b>一键获取美国顶尖名校未来三个月的访校排期表与抢票攻略</b>。
</div>
""", unsafe_allow_html=True)

# US Top 50 示例列表
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

# 交互区设计
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    selected_college = st.selectbox("📌 请选择您心仪的目标大学：", top_50_colleges)

    st.write("")  # 增加一点空隙
    start_search = st.button("🚀 召唤 Agent，生成专属访校攻略")

# 执行搜索并展示结果
if start_search:
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "在此处粘贴您的_DASHSCOPE_API_KEY":
        st.error("⚠️ Agent 未激活：未检测到有效的 API Key。请在代码第7行填入您的 DashScope Key。")
    else:
        # 使用美化的加载提示
        with st.spinner(f"✨ 规划顾问正在全网为您整理 {selected_college} 的最新动态与排期表，请稍作等待..."):
            result = get_tour_info(selected_college)

            st.write("---")
            st.success(f"🎉 规划完成！以下是为您定制的 {selected_college} 访校指南：")

            # 使用 Markdown 容器包裹结果，提升阅读体验
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #A31F34; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                {result}
            </div>
            """, unsafe_allow_html=True)

            st.write("")

            st.info("💡 **顾问贴士**：访校名额通常非常紧俏，建议您参考上方排期表，调好闹钟提前在官网锁定行程！")
