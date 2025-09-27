import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from collections import Counter
import re
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from wordcloud import WordCloud
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="형성평가 체크리스트",
    page_icon="✅",
    layout="wide"
)

# 한글 폰트 설정 (matplotlib용)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 세션 상태 초기화
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'learning_goals' not in st.session_state:
    st.session_state.learning_goals = [""] * 5
if 'current_class' not in st.session_state:
    st.session_state.current_class = ""

# CSS 스타일
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    .goal-checkbox {
        font-size: 18px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 - 교사 설정
with st.sidebar:
    st.header("🎯 교사 설정")
    
    # 수업 정보
    st.subheader("수업 정보")
    class_name = st.text_input("학급명", value=st.session_state.current_class)
    subject = st.text_input("과목/단원", "국어")
    
    # 학습 목표 설정
    st.subheader("학습 목표 설정")
    st.info("💡 학생들이 달성해야 할 목표를 5개 입력하세요")
    
    for i in range(5):
        goal = st.text_input(
            f"목표 {i+1}",
            value=st.session_state.learning_goals[i],
            key=f"goal_{i}",
            placeholder=f"예: 주제문을 찾을 수 있다"
        )
        st.session_state.learning_goals[i] = goal
    
    # 데이터 관리
    st.subheader("📊 데이터 관리")
    
    if st.button("🔄 응답 초기화"):
        st.session_state.responses = []
        st.success("응답이 초기화되었습니다!")
    
    # CSV 다운로드
    if len(st.session_state.responses) > 0:
        df = pd.DataFrame(st.session_state.responses)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f'형성평가_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv'
        )

# 메인 화면
tab1, tab2, tab3 = st.tabs(["✏️ 학생 입력", "📊 실시간 통계", "📈 상세 분석"])

with tab1:
    st.header("✅ 오늘의 학습 목표 체크리스트")
    st.markdown(f"**📚 {subject}** | **🏫 {class_name}** | **📅 {datetime.now().strftime('%Y년 %m월 %d일')}**")
    
    # 학생 정보
    col1, col2 = st.columns([1, 3])
    with col1:
        student_number = st.number_input("번호", min_value=1, max_value=50, step=1)
    
    st.markdown("---")
    
    # 학습 목표 체크리스트
    st.subheader("🎯 학습 목표 달성도")
    st.markdown("각 목표를 달성했다면 체크해주세요:")
    
    goal_checks = {}
    valid_goals = [g for g in st.session_state.learning_goals if g.strip()]
    
    if valid_goals:
        for i, goal in enumerate(valid_goals):
            goal_checks[f"goal_{i+1}"] = st.checkbox(
                f"✓ {goal}",
                key=f"check_{i}"
            )
    else:
        st.warning("⚠️ 선생님이 학습 목표를 설정하지 않았습니다. 사이드바에서 설정해주세요.")
    
    # 전체 이해도
    st.markdown("---")
    st.subheader("📊 전체 이해도")
    understanding = st.slider(
        "오늘 수업 내용을 얼마나 이해했나요?",
        min_value=1,
        max_value=5,
        value=3,
        format="%d점",
        help="1점: 매우 어려움, 5점: 완벽히 이해"
    )
    
    # 피드백
    st.markdown("---")
    st.subheader("💬 피드백 (선택사항)")
    
    col1, col2 = st.columns(2)
    with col1:
        difficult_part = st.text_area(
            "어려웠던 부분이 있다면 적어주세요",
            height=100,
            placeholder="예: 주제문과 뒷받침 문장 구분이 어려웠어요"
        )
    
    with col2:
        help_needed = st.selectbox(
            "도움이 필요한 부분",
            ["없음", "개념 이해", "문제 풀이", "응용", "전체적인 복습", "개별 상담 희망"]
        )
    
    # 제출 버튼
    if st.button("✅ 제출하기", type="primary"):
        if valid_goals:
            response = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "student_number": student_number,
                "understanding": understanding,
                "difficult_part": difficult_part,
                "help_needed": help_needed,
                "goals_achieved": sum(goal_checks.values()),
                "total_goals": len(valid_goals)
            }
            
            # 각 목표별 달성 여부 추가
            for key, value in goal_checks.items():
                response[key] = value
            
            st.session_state.responses.append(response)
            st.success("✅ 제출 완료! 수고했어요~ 😊")
            st.balloons()
        else:
            st.error("학습 목표를 먼저 설정해주세요!")

with tab2:
    st.header("📊 실시간 학급 통계")
    
    if len(st.session_state.responses) > 0:
        df = pd.DataFrame(st.session_state.responses)
        
        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_understanding = df['understanding'].mean()
            st.metric(
                "평균 이해도",
                f"{avg_understanding:.1f}점",
                delta=f"{avg_understanding - 3:.1f}"
            )
        
        with col2:
            total_students = len(df)
            st.metric("참여 학생", f"{total_students}명")
        
        with col3:
            if 'goals_achieved' in df.columns and 'total_goals' in df.columns:
                avg_achievement = (df['goals_achieved'].sum() / (df['total_goals'].sum() if df['total_goals'].sum() > 0 else 1)) * 100
                st.metric("평균 달성률", f"{avg_achievement:.0f}%")
        
        with col4:
            help_count = len(df[df['help_needed'] != '없음'])
            st.metric("도움 요청", f"{help_count}명")
        
        st.markdown("---")
        
        # 목표별 달성률 그래프
        st.subheader("🎯 학습 목표별 달성률")
        
        valid_goals = [g for g in st.session_state.learning_goals if g.strip()]
        if valid_goals:
            goal_data = []
            for i, goal in enumerate(valid_goals):
                goal_col = f"goal_{i+1}"
                if goal_col in df.columns:
                    achievement_rate = df[goal_col].sum() / len(df) * 100
                    goal_data.append({
                        "목표": f"목표{i+1}: {goal[:20]}..." if len(goal) > 20 else f"목표{i+1}: {goal}",
                        "달성률": achievement_rate
                    })
            
            if goal_data:
                goal_df = pd.DataFrame(goal_data)
                fig = px.bar(
                    goal_df,
                    x="달성률",
                    y="목표",
                    orientation='h',
                    color="달성률",
                    color_continuous_scale="RdYlGn",
                    range_color=[0, 100]
                )
                fig.update_layout(
                    height=300,
                    xaxis_title="달성률 (%)",
                    yaxis_title="",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 이해도 분포
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 이해도 분포")
            understanding_dist = df['understanding'].value_counts().sort_index()
            fig = px.bar(
                x=understanding_dist.index,
                y=understanding_dist.values,
                labels={'x': '이해도 점수', 'y': '학생 수'},
                color=understanding_dist.values,
                color_continuous_scale="Blues"
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🆘 도움 요청 분야")
            help_dist = df['help_needed'].value_counts()
            fig = px.pie(
                values=help_dist.values,
                names=help_dist.index,
                hole=0.3
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # 어려웠던 부분 워드클라우드
        st.markdown("---")
        st.subheader("☁️ 어려웠던 부분 (워드클라우드)")
        
        difficult_texts = ' '.join(df[df['difficult_part'].notna()]['difficult_part'].tolist())
        
        if difficult_texts.strip():
            # 간단한 텍스트 기반 워드클라우드 (한글 처리 포함)
            words = re.findall(r'[가-힣]+', difficult_texts)
            word_counts = Counter(words)
            
            if word_counts:
                # 상위 20개 단어만 표시
                top_words = dict(word_counts.most_common(20))
                
                # Plotly로 간단한 막대 그래프로 표시 (워드클라우드 대체)
                fig = px.bar(
                    x=list(top_words.values()),
                    y=list(top_words.keys()),
                    orientation='h',
                    labels={'x': '빈도', 'y': '단어'},
                    color=list(top_words.values()),
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("아직 피드백이 없습니다.")
    
    else:
        st.info("📝 아직 제출된 응답이 없습니다. 학생들의 응답을 기다려주세요.")

with tab3:
    st.header("📈 상세 분석 및 리포트")
    
    if len(st.session_state.responses) > 0:
        df = pd.DataFrame(st.session_state.responses)
        
        # 개인별 상세 현황
        st.subheader("👥 개인별 현황")
        
        # 데이터 정리
        display_df = df[['student_number', 'understanding', 'goals_achieved', 'total_goals', 'help_needed']].copy()
        display_df['달성률'] = (display_df['goals_achieved'] / display_df['total_goals'] * 100).round(0).astype(int)
        display_df = display_df.rename(columns={
            'student_number': '번호',
            'understanding': '이해도',
            'goals_achieved': '달성 목표',
            'total_goals': '전체 목표',
            'help_needed': '도움 필요'
        })
        
        st.dataframe(
            display_df[['번호', '이해도', '달성 목표', '전체 목표', '달성률', '도움 필요']],
            use_container_width=True,
            hide_index=True
        )
        
        # 시간대별 제출 현황
        st.subheader("⏰ 시간대별 제출 현황")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        
        time_dist = df.groupby(['hour', 'minute']).size().reset_index(name='count')
        fig = px.scatter(
            time_dist,
            x='minute',
            y='hour',
            size='count',
            labels={'minute': '분', 'hour': '시', 'count': '제출 수'},
            title="제출 시간 분포"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # PDF 리포트 생성
        st.markdown("---")
        st.subheader("📄 PDF 리포트 생성")
        
        if st.button("📥 PDF 리포트 다운로드"):
            # PDF 생성을 위한 HTML 내용
            html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Malgun Gothic', sans-serif; margin: 20px; }}
                    h1 {{ color: #2E86AB; text-align: center; }}
                    h2 {{ color: #A23B72; margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                    th {{ background-color: #f2f2f2; }}
                    .stat {{ background-color: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>형성평가 결과 리포트</h1>
                <div class="stat">
                    <p><strong>학급:</strong> {class_name}</p>
                    <p><strong>과목:</strong> {subject}</p>
                    <p><strong>일시:</strong> {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
                    <p><strong>참여 학생:</strong> {len(df)}명</p>
                    <p><strong>평균 이해도:</strong> {df['understanding'].mean():.1f}점 / 5점</p>
                </div>
                
                <h2>학습 목표별 달성률</h2>
                <table>
                    <tr>
                        <th>학습 목표</th>
                        <th>달성률</th>
                    </tr>
            """
            
            valid_goals = [g for g in st.session_state.learning_goals if g.strip()]
            for i, goal in enumerate(valid_goals):
                goal_col = f"goal_{i+1}"
                if goal_col in df.columns:
                    achievement_rate = df[goal_col].sum() / len(df) * 100
                    html_content += f"""
                    <tr>
                        <td>{goal}</td>
                        <td>{achievement_rate:.1f}%</td>
                    </tr>
                    """
            
            html_content += """
                </table>
                
                <h2>개인별 현황</h2>
                <table>
                    <tr>
                        <th>번호</th>
                        <th>이해도</th>
                        <th>달성 목표</th>
                        <th>달성률</th>
                        <th>도움 필요</th>
                    </tr>
            """
            
            for _, row in display_df.iterrows():
                html_content += f"""
                <tr>
                    <td>{int(row['번호'])}</td>
                    <td>{int(row['이해도'])}</td>
                    <td>{int(row['달성 목표'])}/{int(row['전체 목표'])}</td>
                    <td>{int(row['달성률'])}%</td>
                    <td>{row['도움 필요']}</td>
                </tr>
                """
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            # HTML을 다운로드 가능한 형태로 제공 (PDF 변환은 별도 라이브러리 필요)
            st.download_button(
                label="📄 HTML 리포트 다운로드 (PDF로 인쇄 가능)",
                data=html_content,
                file_name=f"형성평가_리포트_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html"
            )
            
            st.info("💡 다운로드한 HTML 파일을 브라우저에서 열고 인쇄(Ctrl+P) → PDF로 저장을 선택하세요.")
    
    else:
        st.info("📝 분석할 데이터가 없습니다. 학생들의 응답을 기다려주세요.")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p>🎯 형성평가 체크리스트 v1.0 | 제작: 국어교사를 위한 도구</p>
        <p>💡 Tip: 학생들에게 QR코드로 링크를 공유하면 더 빠르게 접속할 수 있어요!</p>
    </div>
    """,
    unsafe_allow_html=True
)import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from collections import Counter
import re
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from wordcloud import WordCloud
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="형성평가 체크리스트",
    page_icon="✅",
    layout="wide"
)

# 한글 폰트 설정 (matplotlib용)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 세션 상태 초기화
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'learning_goals' not in st.session_state:
    st.session_state.learning_goals = [""] * 5
if 'current_class' not in st.session_state:
    st.session_state.current_class = ""

# CSS 스타일
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    .goal-checkbox {
        font-size: 18px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 - 교사 설정
with st.sidebar:
    st.header("🎯 교사 설정")
    
    # 수업 정보
    st.subheader("수업 정보")
    class_name = st.text_input("학급명", value=st.session_state.current_class)
    subject = st.text_input("과목/단원", "국어")
    
    # 학습 목표 설정
    st.subheader("학습 목표 설정")
    st.info("💡 학생들이 달성해야 할 목표를 5개 입력하세요")
    
    for i in range(5):
        goal = st.text_input(
            f"목표 {i+1}",
            value=st.session_state.learning_goals[i],
            key=f"goal_{i}",
            placeholder=f"예: 주제문을 찾을 수 있다"
        )
        st.session_state.learning_goals[i] = goal
    
    # 데이터 관리
    st.subheader("📊 데이터 관리")
    
    if st.button("🔄 응답 초기화"):
        st.session_state.responses = []
        st.success("응답이 초기화되었습니다!")
    
    # CSV 다운로드
    if len(st.session_state.responses) > 0:
        df = pd.DataFrame(st.session_state.responses)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f'형성평가_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv'
        )

# 메인 화면
tab1, tab2, tab3 = st.tabs(["✏️ 학생 입력", "📊 실시간 통계", "📈 상세 분석"])

with tab1:
    st.header("✅ 오늘의 학습 목표 체크리스트")
    st.markdown(f"**📚 {subject}** | **🏫 {class_name}** | **📅 {datetime.now().strftime('%Y년 %m월 %d일')}**")
    
    # 학생 정보
    col1, col2 = st.columns([1, 3])
    with col1:
        student_number = st.number_input("번호", min_value=1, max_value=50, step=1)
    
    st.markdown("---")
    
    # 학습 목표 체크리스트
    st.subheader("🎯 학습 목표 달성도")
    st.markdown("각 목표를 달성했다면 체크해주세요:")
    
    goal_checks = {}
    valid_goals = [g for g in st.session_state.learning_goals if g.strip()]
    
    if valid_goals:
        for i, goal in enumerate(valid_goals):
            goal_checks[f"goal_{i+1}"] = st.checkbox(
                f"✓ {goal}",
                key=f"check_{i}"
            )
    else:
        st.warning("⚠️ 선생님이 학습 목표를 설정하지 않았습니다. 사이드바에서 설정해주세요.")
    
    # 전체 이해도
    st.markdown("---")
    st.subheader("📊 전체 이해도")
    understanding = st.slider(
        "오늘 수업 내용을 얼마나 이해했나요?",
        min_value=1,
        max_value=5,
        value=3,
        format="%d점",
        help="1점: 매우 어려움, 5점: 완벽히 이해"
    )
    
    # 피드백
    st.markdown("---")
    st.subheader("💬 피드백 (선택사항)")
    
    col1, col2 = st.columns(2)
    with col1:
        difficult_part = st.text_area(
            "어려웠던 부분이 있다면 적어주세요",
            height=100,
            placeholder="예: 주제문과 뒷받침 문장 구분이 어려웠어요"
        )
    
    with col2:
        help_needed = st.selectbox(
            "도움이 필요한 부분",
            ["없음", "개념 이해", "문제 풀이", "응용", "전체적인 복습", "개별 상담 희망"]
        )
    
    # 제출 버튼
    if st.button("✅ 제출하기", type="primary"):
        if valid_goals:
            response = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "student_number": student_number,
                "understanding": understanding,
                "difficult_part": difficult_part,
                "help_needed": help_needed,
                "goals_achieved": sum(goal_checks.values()),
                "total_goals": len(valid_goals)
            }
            
            # 각 목표별 달성 여부 추가
            for key, value in goal_checks.items():
                response[key] = value
            
            st.session_state.responses.append(response)
            st.success("✅ 제출 완료! 수고했어요~ 😊")
            st.balloons()
        else:
            st.error("학습 목표를 먼저 설정해주세요!")

with tab2:
    st.header("📊 실시간 학급 통계")
    
    if len(st.session_state.responses) > 0:
        df = pd.DataFrame(st.session_state.responses)
        
        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_understanding = df['understanding'].mean()
            st.metric(
                "평균 이해도",
                f"{avg_understanding:.1f}점",
                delta=f"{avg_understanding - 3:.1f}"
            )
        
        with col2:
            total_students = len(df)
            st.metric("참여 학생", f"{total_students}명")
        
        with col3:
            if 'goals_achieved' in df.columns and 'total_goals' in df.columns:
                avg_achievement = (df['goals_achieved'].sum() / (df['total_goals'].sum() if df['total_goals'].sum() > 0 else 1)) * 100
                st.metric("평균 달성률", f"{avg_achievement:.0f}%")
        
        with col4:
            help_count = len(df[df['help_needed'] != '없음'])
            st.metric("도움 요청", f"{help_count}명")
        
        st.markdown("---")
        
        # 목표별 달성률 그래프
        st.subheader("🎯 학습 목표별 달성률")
        
        valid_goals = [g for g in st.session_state.learning_goals if g.strip()]
        if valid_goals:
            goal_data = []
            for i, goal in enumerate(valid_goals):
                goal_col = f"goal_{i+1}"
                if goal_col in df.columns:
                    achievement_rate = df[goal_col].sum() / len(df) * 100
                    goal_data.append({
                        "목표": f"목표{i+1}: {goal[:20]}..." if len(goal) > 20 else f"목표{i+1}: {goal}",
                        "달성률": achievement_rate
                    })
            
            if goal_data:
                goal_df = pd.DataFrame(goal_data)
                fig = px.bar(
                    goal_df,
                    x="달성률",
                    y="목표",
                    orientation='h',
                    color="달성률",
                    color_continuous_scale="RdYlGn",
                    range_color=[0, 100]
                )
                fig.update_layout(
                    height=300,
                    xaxis_title="달성률 (%)",
                    yaxis_title="",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 이해도 분포
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 이해도 분포")
            understanding_dist = df['understanding'].value_counts().sort_index()
            fig = px.bar(
                x=understanding_dist.index,
                y=understanding_dist.values,
                labels={'x': '이해도 점수', 'y': '학생 수'},
                color=understanding_dist.values,
                color_continuous_scale="Blues"
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🆘 도움 요청 분야")
            help_dist = df['help_needed'].value_counts()
            fig = px.pie(
                values=help_dist.values,
                names=help_dist.index,
                hole=0.3
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # 어려웠던 부분 워드클라우드
        st.markdown("---")
        st.subheader("☁️ 어려웠던 부분 (워드클라우드)")
        
        difficult_texts = ' '.join(df[df['difficult_part'].notna()]['difficult_part'].tolist())
        
        if difficult_texts.strip():
            # 간단한 텍스트 기반 워드클라우드 (한글 처리 포함)
            words = re.findall(r'[가-힣]+', difficult_texts)
            word_counts = Counter(words)
            
            if word_counts:
                # 상위 20개 단어만 표시
                top_words = dict(word_counts.most_common(20))
                
                # Plotly로 간단한 막대 그래프로 표시 (워드클라우드 대체)
                fig = px.bar(
                    x=list(top_words.values()),
                    y=list(top_words.keys()),
                    orientation='h',
                    labels={'x': '빈도', 'y': '단어'},
                    color=list(top_words.values()),
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("아직 피드백이 없습니다.")
    
    else:
        st.info("📝 아직 제출된 응답이 없습니다. 학생들의 응답을 기다려주세요.")

with tab3:
    st.header("📈 상세 분석 및 리포트")
    
    if len(st.session_state.responses) > 0:
        df = pd.DataFrame(st.session_state.responses)
        
        # 개인별 상세 현황
        st.subheader("👥 개인별 현황")
        
        # 데이터 정리
        display_df = df[['student_number', 'understanding', 'goals_achieved', 'total_goals', 'help_needed']].copy()
        display_df['달성률'] = (display_df['goals_achieved'] / display_df['total_goals'] * 100).round(0).astype(int)
        display_df = display_df.rename(columns={
            'student_number': '번호',
            'understanding': '이해도',
            'goals_achieved': '달성 목표',
            'total_goals': '전체 목표',
            'help_needed': '도움 필요'
        })
        
        st.dataframe(
            display_df[['번호', '이해도', '달성 목표', '전체 목표', '달성률', '도움 필요']],
            use_container_width=True,
            hide_index=True
        )
        
        # 시간대별 제출 현황
        st.subheader("⏰ 시간대별 제출 현황")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        
        time_dist = df.groupby(['hour', 'minute']).size().reset_index(name='count')
        fig = px.scatter(
            time_dist,
            x='minute',
            y='hour',
            size='count',
            labels={'minute': '분', 'hour': '시', 'count': '제출 수'},
            title="제출 시간 분포"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # PDF 리포트 생성
        st.markdown("---")
        st.subheader("📄 PDF 리포트 생성")
        
        if st.button("📥 PDF 리포트 다운로드"):
            # PDF 생성을 위한 HTML 내용
            html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Malgun Gothic', sans-serif; margin: 20px; }}
                    h1 {{ color: #2E86AB; text-align: center; }}
                    h2 {{ color: #A23B72; margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                    th {{ background-color: #f2f2f2; }}
                    .stat {{ background-color: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>형성평가 결과 리포트</h1>
                <div class="stat">
                    <p><strong>학급:</strong> {class_name}</p>
                    <p><strong>과목:</strong> {subject}</p>
                    <p><strong>일시:</strong> {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
                    <p><strong>참여 학생:</strong> {len(df)}명</p>
                    <p><strong>평균 이해도:</strong> {df['understanding'].mean():.1f}점 / 5점</p>
                </div>
                
                <h2>학습 목표별 달성률</h2>
                <table>
                    <tr>
                        <th>학습 목표</th>
                        <th>달성률</th>
                    </tr>
            """
            
            valid_goals = [g for g in st.session_state.learning_goals if g.strip()]
            for i, goal in enumerate(valid_goals):
                goal_col = f"goal_{i+1}"
                if goal_col in df.columns:
                    achievement_rate = df[goal_col].sum() / len(df) * 100
                    html_content += f"""
                    <tr>
                        <td>{goal}</td>
                        <td>{achievement_rate:.1f}%</td>
                    </tr>
                    """
            
            html_content += """
                </table>
                
                <h2>개인별 현황</h2>
                <table>
                    <tr>
                        <th>번호</th>
                        <th>이해도</th>
                        <th>달성 목표</th>
                        <th>달성률</th>
                        <th>도움 필요</th>
                    </tr>
            """
            
            for _, row in display_df.iterrows():
                html_content += f"""
                <tr>
                    <td>{int(row['번호'])}</td>
                    <td>{int(row['이해도'])}</td>
                    <td>{int(row['달성 목표'])}/{int(row['전체 목표'])}</td>
                    <td>{int(row['달성률'])}%</td>
                    <td>{row['도움 필요']}</td>
                </tr>
                """
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            # HTML을 다운로드 가능한 형태로 제공 (PDF 변환은 별도 라이브러리 필요)
            st.download_button(
                label="📄 HTML 리포트 다운로드 (PDF로 인쇄 가능)",
                data=html_content,
                file_name=f"형성평가_리포트_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html"
            )
            
            st.info("💡 다운로드한 HTML 파일을 브라우저에서 열고 인쇄(Ctrl+P) → PDF로 저장을 선택하세요.")
    
    else:
        st.info("📝 분석할 데이터가 없습니다. 학생들의 응답을 기다려주세요.")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p>🎯 형성평가 체크리스트 v1.0 | 제작: 국어교사를 위한 도구</p>
        <p>💡 Tip: 학생들에게 QR코드로 링크를 공유하면 더 빠르게 접속할 수 있어요!</p>
    </div>
    """,
    unsafe_allow_html=True
)
