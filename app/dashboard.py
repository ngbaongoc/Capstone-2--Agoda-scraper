import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import redis
import json
from sqlalchemy import create_engine

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Quản Lý Khách Sạn - Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. DATA ENGINE
# -----------------------------------------------------------------------------
DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:password123@localhost:5433/hotel_insights")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

@st.cache_resource
def get_db_engine():
    try: 
        return create_engine(DB_URL)
    except: 
        return None

@st.cache_resource
def get_redis_client():
    try:
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        client.ping()
        return client
    except: 
        return None

def load_data():
    """Load reviews data and overall statistics."""
    r = get_redis_client()
    CACHE_KEY = "hotel_reviews_refined_v1"
    
    # 1. Try Cache
    if r:
        try:
            cached = r.get(CACHE_KEY)
            if cached:
                df = pd.read_json(cached, orient='split')
                if 'review_date' in df.columns:
                    df['review_date'] = pd.to_datetime(df['review_date'])
                return df
        except: 
            pass
        
    # 2. Query DB
    engine = get_db_engine()
    
    if not engine:
        # --- MOCK DATA FALLBACK ---
        data = {
            "hotel_name": ["Ocean Haven Đà Nẵng"] * 5,
            "reviewer_name": ["Nguyễn Văn A", "David Smith", "Trần Thị B", "Lê Văn C", "Vasiliy"],
            "reviewer_score": [10.0, 8.8, 4.0, 9.2, 8.0],
            "review_title": [
                "Khách sạn tuyệt vời",
                "Very good place", 
                "Thất vọng hoàn toàn",
                "Trải nghiệm tốt",
                "Disappointing stay"
            ],
            "review_text": [
                "Tuyệt vời, nhân viên nhiệt tình. Phòng sạch sẽ, view đẹp. Sẽ quay lại lần sau.", 
                "Great value for money! The swimming pool is actually quite smaller than it appears on the photo. Staff was helpful. Breakfast was good.", 
                "Phòng quá hôi mùi ẩm mốc. Điều hòa kêu to cả đêm không ngủ được. Nhân viên thờ ơ. Rất thất vọng.", 
                "Sạch sẽ, ăn sáng hơi ít món nhưng chất lượng tốt. Nhân viên thân thiện.", 
                "Nhân viên lễ tân tốt nhưng dọn phòng quá ồn ào lúc 6h sáng. Phòng hôi, nệm cứng. Rất thất vọng với trải nghiệm này."
            ],
            "review_date": [datetime.now() - timedelta(days=x*7) for x in range(5)],
            "room_type": ["Deluxe City View", "Superior Double", "Suite Sea View", "Superior Twin", "Deluxe Sea View"],
            "country": ["Vietnam", "USA", "Vietnam", "Vietnam", "Russia"],
            "traveler_type": ["Cặp đôi", "Gia đình", "Công tác", "Gia đình", "Một mình"],
            "stay_duration": ["1 night", "2 nights", "1 night", "3 nights", "5 nights"],
            "nights": [1, 2, 1, 3, 5]
        }
        df = pd.DataFrame(data)
        df['review_date'] = pd.to_datetime(df['review_date'])
        # Normalize column name
      
    else:
        try:
            query = "SELECT * FROM reviews"
            df = pd.read_sql(query, engine)
            df['review_date'] = pd.to_datetime(df['review_date'])
            if 'nights' not in df.columns and 'stay_duration' in df.columns:
                df['nights'] = df['stay_duration'].str.extract(r'(\d+)').fillna(1).astype(int)
            if 'review_title' not in df.columns:
                df['review_title'] = "No title"
        except Exception as e:
            # st.error(f"Database error: {e}")
            # FALLBACK TO JSON
            JSON_FILE = os.path.join(os.path.dirname(__file__), "../data/agoda_reviews_cleaned.json")
            if os.path.exists(JSON_FILE):
                try:
                    with open(JSON_FILE, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    flattened = []
                    for hotel in json_data:
                        hotel_name = hotel.get('hotel_name', 'Unknown')
                        for r in hotel.get('reviews', []):
                            row = r.copy()
                            row['hotel_name'] = hotel_name
                            # Ensure columns match DB schema
                            if 'reviewer_country' in row and 'country' not in row:
                                row['country'] = row['reviewer_country']
                            flattened.append(row)
                    
                    df = pd.DataFrame(flattened)
                    if not df.empty:
                        df['review_date'] = pd.to_datetime(df['review_date'])
                        if 'nights' not in df.columns and 'stay_duration' in df.columns:
                            df['nights'] = df['stay_duration'].str.extract(r'(\d+)').fillna(1).astype(int)
                        if 'review_title' not in df.columns:
                            df['review_title'] = "No title"
                        st.info(f"ℹ️ Đang sử dụng dữ liệu từ file local: {len(df)} reviews.")
                        return df
                except Exception as json_e:
                    st.error(f"Lỗi khi đọc file JSON: {json_e}")
            
            return pd.DataFrame()

    if df.empty: 
        return pd.DataFrame()
    
            
    # 3. Process & Enrich
    def calc_sentiment(row):
        text = str(row['review_text']).lower() if row['review_text'] else ""
        neg_words = ['ồn', 'bẩn', 'tệ', 'hôi', 'chán', 'thất vọng', 'noisy', 'dirty', 'bad', 
                     'terrible', 'smell', 'rude', 'disappointing', 'uncomfortable', 'musty']
        neg_count = sum(1 for w in neg_words if w in text)
        base = float(row['reviewer_score']) / 10.0
        penalty = neg_count * 0.15
        return max(0.1, base - penalty)
        
    if 'ai_sentiment_score' not in df.columns:
        df['ai_sentiment_score'] = df.apply(calc_sentiment, axis=1)
        
    if 'ai_label' not in df.columns:
        df['ai_label'] = df['ai_sentiment_score'].apply(
            lambda x: 'Tích cực' if x >= 0.7 else ('Tiêu cực' if x <= 0.45 else 'Trung lập')
        )
        
    if 'is_conflict' not in df.columns:
        df['is_conflict'] = (df['reviewer_score'] >= 8.0) & (df['ai_sentiment_score'] < 0.5)

    # Cache result
    if r: 
        r.set(CACHE_KEY, df.to_json(orient='split', date_format='iso'), ex=300)
    
    return df

def load_overall_stats(reviews_df):
    """Generate overall statistics from reviews data."""
    if reviews_df.empty:
        return {
            'hotel_name': 'Unknown Hotel',
            'hotel_url': '#',
            'overall_score': 0,
            'overall_rating_text': 'N/A',
            'total_reviews': 0,
            'total_scraped': 0,
            'recent_ratings': []
        }
    
    hotel_name = reviews_df['hotel_name'].iloc[0] if 'hotel_name' in reviews_df.columns else 'Ocean Haven Đà Nẵng'
    
    return {
        'hotel_name': hotel_name,
        'hotel_url': 'https://www.agoda.com/ocean-haven-hotel/hotel/da-nang-vn.html',
        'overall_score': round(reviews_df['reviewer_score'].mean(), 1),
        'overall_rating_text': 'Excellent' if reviews_df['reviewer_score'].mean() >= 8 else 'Good',
        'total_reviews': 1100,  # This would come from API in production
        'total_scraped': len(reviews_df),
        'recent_ratings': reviews_df['reviewer_score'].tolist()
    }

def load_categories():
    """Load category scores - would come from API in production."""
    return pd.DataFrame([
        {"category_name": "Vị trí", "category_score": 9.3},
        {"category_name": "Dịch vụ", "category_score": 9.1},
        {"category_name": "Giá trị", "category_score": 9.0},
        {"category_name": "Vệ sinh", "category_score": 8.9},
        {"category_name": "Tiện nghi", "category_score": 8.8},
        {"category_name": "Phòng", "category_score": 7.0}
    ])

# Data will be loaded and filtered in sidebar

# -----------------------------------------------------------------------------
# 3. SIDEBAR
# -----------------------------------------------------------------------------
# Load all data first
all_reviews_df = load_data()

with st.sidebar:
    st.title("🏨 Quản Lý KS")
    st.caption("Dành cho Chủ/Quản lý")
    
    st.divider()
    
    st.subheader("CHI NHÁNH")
    
    # Get unique hotels
    hotel_options = all_reviews_df['hotel_name'].unique().tolist() if not all_reviews_df.empty else ['Unknown Hotel']
    
    selected_hotel = st.selectbox(
        "Chi nhánh", 
        hotel_options, 
        label_visibility="collapsed"
    )

    # Filter data by selected hotel immediately
    reviews_df = all_reviews_df.copy()
    if not reviews_df.empty and selected_hotel:
        reviews_df = reviews_df[reviews_df['hotel_name'] == selected_hotel]
    
    overall_stats = load_overall_stats(reviews_df)
    
    st.subheader("THỜI GIAN")
    min_date = reviews_df['review_date'].min() if not reviews_df.empty else datetime(2024, 1, 1)
    max_date = reviews_df['review_date'].max() if not reviews_df.empty else datetime.now()
    
    date_range = st.date_input(
        "Thời gian",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )
    
    # --- GLOBAL FILTERING CORE ---
    # 1. Filter by Hotel (Applied earlier or here if needed, but we do it above for UX)
    # The previous code block (lines 198+) already filters by hotel if selected.
    # Now we apply Date Filter.
    
    if not reviews_df.empty and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        reviews_df = reviews_df[
            (reviews_df['review_date'] >= start_date) & 
            (reviews_df['review_date'] <= end_date)
        ].copy() # Ensure copy to avoid settingwithcopy warning

    # 2. Recalculate stats based on FULLY FILTERED data
    overall_stats = load_overall_stats(reviews_df)  # Recalculate with date filter
    
    # 3. Dynamic Categories
    # We update load_categories to take the filtered DF
    def get_dynamic_categories(df):
        if df.empty:
            return pd.DataFrame([
                {"category_name": "Vị trí", "category_score": 0},
                {"category_name": "Dịch vụ", "category_score": 0},
                {"category_name": "Giá trị", "category_score": 0},
                {"category_name": "Vệ sinh", "category_score": 0},
                {"category_name": "Tiện nghi", "category_score": 0},
                {"category_name": "Phòng", "category_score": 0}
            ])
            
        # If real columns exist, use them. Otherwise simulate based on main score.
        # Simulation allows each hotel to look different based on its actual average.
        base_score = df['reviewer_score'].mean()
        
        # Add some variance based on hotel name hash or random to make it look realistic but consistent
        # For now, we'll just vary slightly around the mean
        cats = [
            ("Vị trí", 0.4), ("Dịch vụ", 0.2), ("Giá trị", 0.0), 
            ("Vệ sinh", -0.1), ("Tiện nghi", -0.2), ("Phòng", -0.3)
        ]
        
        data = []
        for name, offset in cats:
            # Clamp between 2 and 10
            score = max(2.0, min(10.0, base_score + offset))
            data.append({"category_name": name, "category_score": round(score, 1)})
            
        return pd.DataFrame(data)

    categories_df = get_dynamic_categories(reviews_df)
    # -----------------------------
    
    st.divider()
    
    st.subheader("BỘ LỌC")
    nav_selection = st.radio(
        "Xem theo",
        ["📋 Tất cả", "😤 Phàn Nàn", "🎭 Review Ảo"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Data coverage indicator
    if overall_stats['total_reviews'] > 0:
        coverage = (overall_stats['total_scraped'] / overall_stats['total_reviews']) * 100
    else:
        coverage = 0
        
    st.caption("📈 ĐỘ PHỦ DỮ LIỆU")
    st.progress(min(coverage / 100, 1.0))
    st.caption(f"{overall_stats['total_scraped']:,} / {overall_stats['total_reviews']:,} reviews ({coverage:.1f}%)")

# -----------------------------------------------------------------------------
# 4. MAIN CONTENT
# -----------------------------------------------------------------------------
# Check for empty data
if reviews_df.empty:
    st.warning("⚠️ Không có dữ liệu cho bộ lọc này.")
    st.stop()

# Filter based on navigation
filtered_df = reviews_df.copy()
if "Phàn Nàn" in nav_selection:
    filtered_df = filtered_df[filtered_df['ai_label'] == 'Tiêu cực']
elif "Review Ảo" in nav_selection:
    filtered_df = filtered_df[filtered_df['is_conflict'] == True]

# Header
col_head_1, col_head_2 = st.columns([3, 1])
with col_head_1:
    st.title(f"📋 {selected_hotel}")
    st.caption(f"🔗 [Xem trên Agoda]({overall_stats['hotel_url']}) • Cập nhật: **Vừa xong**")
with col_head_2:
    if st.button("🔄 Tải lại", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

st.divider()

# =============================================================================
# TIER 1: KEY METRICS
# =============================================================================
st.subheader("📊 Chỉ Số Chính")

m1, m2, m3, m4, m5 = st.columns(5)

avg_rating = filtered_df['reviewer_score'].mean() if not filtered_df.empty else 0
avg_sentiment = filtered_df['ai_sentiment_score'].mean() * 10 if not filtered_df.empty else 0
conflict_count = int(filtered_df['is_conflict'].sum()) if not filtered_df.empty else 0
neg_count = len(filtered_df[filtered_df['ai_label'] == 'Tiêu cực']) if not filtered_df.empty else 0
total_count = len(filtered_df)

with m1:
    st.metric(
        label="⭐ Điểm Agoda",
        value=f"{overall_stats['overall_score']}/10",
        delta=f"{overall_stats['overall_rating_text']}",
        delta_color="off"
    )

with m2:
    st.metric(
        label="📝 Điểm Mẫu",
        value=f"{avg_rating:.1f}/10",
        delta=f"{total_count} reviews",
        delta_color="off"
    )

with m3:
    st.metric(
        label="❤️ Sentiment",
        value=f"{avg_sentiment:.1f}/10",
        delta=f"{avg_sentiment - avg_rating:+.1f} vs sao",
        delta_color="inverse" if avg_sentiment < avg_rating else "normal"
    )

with m4:
    st.metric(
        label="⚠️ Rủi Ro Ẩn",
        value=conflict_count,
        delta="CẦN XỬ LÝ" if conflict_count > 0 else "OK",
        delta_color="inverse" if conflict_count > 0 else "normal"
    )

with m5:
    neg_ratio = (neg_count / total_count * 100) if total_count > 0 else 0
    st.metric(
        label="👎 Tiêu Cực",
        value=f"{neg_ratio:.0f}%",
        delta=f"{neg_count} reviews",
        delta_color="inverse" if neg_ratio > 20 else "normal"
    )

st.divider()

# =============================================================================
# TIER 2: CATEGORY ANALYSIS + WORD CLOUD
# =============================================================================
st.subheader("🎯 Phân Tích Theo Hạng Mục")

cat_col1, cat_col2 = st.columns([1, 1])

with cat_col1:
    fig_radar = go.Figure()
    
    categories = categories_df['category_name'].tolist()
    scores = categories_df['category_score'].tolist()
    categories_closed = categories + [categories[0]]
    scores_closed = scores + [scores[0]]
    
    fig_radar.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#3b82f6', width=2),
        name='Điểm hiện tại'
    ))
    
    fig_radar.add_trace(go.Scatterpolar(
        r=[8.5] * len(categories_closed),
        theta=categories_closed,
        line=dict(color='#ef4444', width=1, dash='dot'),
        name='Mục tiêu (8.5)'
    ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=30, b=30, l=30, r=30),
        height=350
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    weakest = categories_df.loc[categories_df['category_score'].idxmin()]
    st.error(f"⚠️ **Cần cải thiện:** {weakest['category_name']} ({weakest['category_score']}/10)")

with cat_col2:
    st.caption("**☁️ Khách hàng nói gì về chúng ta?**")
    
    # Combine all review texts
    all_text = " ".join(reviews_df['review_text'].dropna().tolist())
    
    if all_text.strip():
        # Stopwords (English + Vietnamese)
        stopwords = set([
            # English
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought',
            'used', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'if', 'because',
            'until', 'while', 'about', 'against', 'between', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out',
            'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now',
            'my', 'also', 'really', 'quite', 'actually', 'hotel', 'room', 'stay',
            # Vietnamese
            'và', 'của', 'là', 'có', 'được', 'cho', 'không', 'này', 'đã', 'với',
            'các', 'một', 'những', 'trong', 'để', 'còn', 'khi', 'thì', 'mà', 'như',
            'tôi', 'bạn', 'rất', 'nhiều', 'nên', 'vì', 'từ', 'đến', 'ra', 'vào',
            'cũng', 'nhưng', 'nếu', 'hay', 'hoặc', 'sẽ', 'đây', 'đó', 'ở', 'về'
        ])
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=stopwords,
            max_words=80,
            colormap='Blues',
            collocations=False,
            min_font_size=12,
            max_font_size=80,
            prefer_horizontal=0.7
        ).generate(all_text)
        
        # Display
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout(pad=0)
        
        st.pyplot(fig)
        plt.close(fig)  # Close to free memory
        
        # Top keywords summary
        word_freq = wordcloud.words_
        top_words = list(word_freq.keys())[:5]
        st.caption(f"🔑 **Từ khóa nổi bật:** {', '.join(top_words)}")
    else:
        st.info("Chưa có đủ dữ liệu để tạo Word Cloud.")

st.divider()

# =============================================================================
# TIER 3: GUEST DEMOGRAPHICS
# =============================================================================
st.subheader("👥 Phân Tích Khách Hàng")

demo_col1, demo_col2, demo_col3 = st.columns(3)

with demo_col1:
    st.caption("**Theo Loại Khách**")
    traveler_counts = reviews_df['traveler_type'].value_counts().reset_index()
    traveler_counts.columns = ['Loại khách', 'Số lượng']
    
    fig_traveler = px.pie(
        traveler_counts, 
        values='Số lượng', 
        names='Loại khách',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    fig_traveler.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=250,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1)
    )
    st.plotly_chart(fig_traveler, use_container_width=True)

with demo_col2:
    st.caption("**Theo Quốc Gia**")
    country_counts = reviews_df['country'].value_counts().reset_index()
    country_counts.columns = ['Quốc gia', 'Số lượng']
    
    fig_country = px.bar(
        country_counts,
        x='Số lượng',
        y='Quốc gia',
        orientation='h',
        color='Số lượng',
        color_continuous_scale='Blues'
    )
    fig_country.update_layout(
        plot_bgcolor="white",
        height=250,
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_country, use_container_width=True)

with demo_col3:
    st.caption("**Theo Số Đêm**")
    nights_counts = reviews_df['nights'].value_counts().sort_index().reset_index()
    nights_counts.columns = ['Số đêm', 'Số lượng']
    
    fig_nights = px.bar(
        nights_counts,
        x='Số đêm',
        y='Số lượng',
        color_discrete_sequence=['#8b5cf6']
    )
    fig_nights.update_layout(
        plot_bgcolor="white",
        height=250,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )
    st.plotly_chart(fig_nights, use_container_width=True)

st.divider()

# =============================================================================
# TIER 4: ACTION CENTER
# =============================================================================
st.subheader("⚡ Việc khẩn cấp cần xử lí")

# Priority calculation
def calc_priority(row):
    base = (1.0 - row['ai_sentiment_score']) * 100
    if row['is_conflict']: 
        base += 50
    if row['ai_label'] == 'Tiêu cực': 
        base += 30
    return base

action_df = reviews_df.copy()
action_df['priority'] = action_df.apply(calc_priority, axis=1)
top_actions = action_df.sort_values('priority', ascending=False).head(3)

# Summary stats
urgent_count = len(action_df[action_df['priority'] >= 80])
warning_count = len(action_df[(action_df['priority'] >= 50) & (action_df['priority'] < 80)])
pending_count = len(action_df[action_df['priority'] < 50])

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric("🔥 Khẩn cấp", urgent_count, help="Priority >= 80")
with stat_col2:
    st.metric("⚠️ Cần chú ý", warning_count, help="Priority 50-79")
with stat_col3:
    st.metric("📌 Theo dõi", pending_count, help="Priority < 50")
with stat_col4:
    st.metric("✅ Đã xử lý", 0, help="Đã phản hồi")

st.divider()

# Tabs for filtering
tab_all, tab_urgent, tab_warning = st.tabs([
    f"📋 Tất cả ({len(top_actions)})", 
    f"🔥 Khẩn cấp ({urgent_count})", 
    f"⚠️ Cần chú ý ({warning_count})"
])

def render_action_card(row, idx):
    """Render a single action card."""
    p_score = int(row['priority'])
    
    with st.container(border=True):
        # Header
        h_col1, h_col2 = st.columns([4, 1])
        
        with h_col1:
            st.markdown(f"### {row['reviewer_name']}")
            st.caption(f"🌍 {row['country']} • 👤 {row['traveler_type']} • 🛏️ {row['nights']} đêm")
        
        with h_col2:
            if p_score >= 80:
                st.error(f"🔥 **{p_score}**")
            elif p_score >= 50:
                st.warning(f"⚠️ **{p_score}**")
            else:
                st.info(f"📌 **{p_score}**")
        
        # Info row
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.caption("**Loại phòng**")
            st.write(row['room_type'])
        
        with info_col2:
            st.caption("**Điểm Agoda**")
            score_icon = "🟢" if row['reviewer_score'] >= 8 else ("🟡" if row['reviewer_score'] >= 6 else "🔴")
            st.write(f"{score_icon} {row['reviewer_score']}/10")
        
        with info_col3:
            st.caption("**Sentiment AI**")
            sent_score = row['ai_sentiment_score'] * 10
            sent_icon = "🟢" if sent_score >= 7 else ("🟡" if sent_score >= 5 else "🔴")
            st.write(f"{sent_icon} {sent_score:.1f}/10")
        
        st.divider()
        
        # Conflict warning
        if row['is_conflict']:
            st.error("⚠️ **CẢNH BÁO:** Điểm cao nhưng nội dung tiêu cực!")
        
        # Review content
        review_title = row.get('review_title', 'No title')
        st.caption(f"**📝 Tiêu đề:** {review_title}")
        
        review_text = str(row['review_text'])
        if len(review_text) > 200:
            st.write(f"*\"{review_text[:200]}...\"*")
            with st.expander("📖 Xem đầy đủ"):
                st.write(review_text)
        else:
            st.write(f"*\"{review_text}\"*")
        
        st.divider()
        
        # Action buttons
        btn1, btn2, btn3, btn4 = st.columns(4)
        
        with btn1:
            if st.button("✉️ Soạn Mail", key=f"mail_{idx}", use_container_width=True):
                st.session_state[f'show_mail_{idx}'] = not st.session_state.get(f'show_mail_{idx}', False)
        
        with btn2:
            st.button("🎁 Voucher", key=f"voucher_{idx}", use_container_width=True)
        
        with btn3:
            st.button("📝 Ghi Chú", key=f"note_{idx}", use_container_width=True)
        
        with btn4:
            if st.button("✅ Xong", key=f"done_{idx}", use_container_width=True):
                st.toast(f"✅ Đã đánh dấu: {row['reviewer_name']}")
        
        # Email composer
        if st.session_state.get(f'show_mail_{idx}', False):
            st.divider()
            st.caption("**✉️ Soạn Email Phản Hồi**")
            
            email_template = f"""Kính gửi Quý khách {row['reviewer_name']},

Thay mặt {selected_hotel}, chúng tôi xin gửi lời cảm ơn chân thành đến Quý khách.

Chúng tôi đã nhận được phản hồi và rất tiếc về những trải nghiệm chưa tốt.

[Nội dung phản hồi cụ thể]

Trân trọng,
Ban Quản lý {selected_hotel}"""
            
            st.text_area("Nội dung:", value=email_template, height=200, key=f"email_{idx}")
            
            mail_btn1, mail_btn2 = st.columns(2)
            with mail_btn1:
                if st.button("📤 Gửi", key=f"send_{idx}", type="primary", use_container_width=True):
                    st.success("✅ Đã gửi email!")
                    st.session_state[f'show_mail_{idx}'] = False
            with mail_btn2:
                if st.button("❌ Hủy", key=f"cancel_{idx}", use_container_width=True):
                    st.session_state[f'show_mail_{idx}'] = False
                    st.rerun()

# Render in tabs
with tab_all:
    for idx, row in top_actions.iterrows():
        render_action_card(row, f"all_{idx}")

with tab_urgent:
    urgent_df = top_actions[top_actions['priority'] >= 80]
    if urgent_df.empty:
        st.success("🎉 Không có vấn đề khẩn cấp!")
    else:
        for idx, row in urgent_df.iterrows():
            render_action_card(row, f"urg_{idx}")

with tab_warning:
    warning_df = top_actions[(top_actions['priority'] >= 50) & (top_actions['priority'] < 80)]
    if warning_df.empty:
        st.info("Không có vấn đề cần chú ý.")
    else:
        for idx, row in warning_df.iterrows():
            render_action_card(row, f"warn_{idx}")

st.divider()

# =============================================================================
# TIER 5: SEARCH
# =============================================================================
st.subheader("🔍 Tra Cứu Review")

search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    query = st.text_input(
        "Tìm kiếm",
        placeholder="Gõ từ khóa: ồn, bể bơi, ăn sáng, nhân viên...",
        label_visibility="collapsed"
    )

with search_col2:
    st.caption("**Gợi ý:**")
    quick_terms = ["ồn", "sạch", "nhân viên", "ăn sáng"]
    selected_quick = st.selectbox("Quick", quick_terms, label_visibility="collapsed")

search_query = query if query else None

if search_query:
    # Search in both review_text and review_title
    mask = reviews_df['review_text'].str.contains(search_query, case=False, na=False)
    if 'review_title' in reviews_df.columns:
        mask = mask | reviews_df['review_title'].str.contains(search_query, case=False, na=False)
    
    hits = reviews_df[mask]
    
    if not hits.empty:
        st.caption(f"Tìm thấy **{len(hits)}** kết quả cho '{search_query}':")
        for idx, hit in hits.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{hit['reviewer_name']}** • {hit['country']} • {hit['traveler_type']}")
                with col2:
                    st.write(f"⭐ **{hit['reviewer_score']}/10**")
                
                st.caption(f"📍 {hit['room_type']} • {hit['review_date'].strftime('%d/%m/%Y')}")
                
                review_title = hit.get('review_title', '')
                if review_title:
                    st.info(f"**{review_title}**\n\n{hit['review_text']}")
                else:
                    st.info(hit['review_text'])
    else:
        st.warning(f"Không tìm thấy kết quả cho '{search_query}'")

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption("© 2025 Hotel Insights Dashboard • Powered by AI Sentiment Analysis")