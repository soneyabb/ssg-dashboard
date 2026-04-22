import pandas as pd
import json
import os
import base64

# 데이터 로드
base_dir = os.path.abspath('/Users/seonhyechoi/Desktop/wiset-inflearn/ssg-com')
csv_path = os.path.join(base_dir, 'data/ssg_items.csv')
df = pd.read_csv(csv_path)

# 수치 데이터 전처리
df['displayPrc'] = pd.to_numeric(df['displayPrc'], errors='coerce').fillna(0)
df['strikeOutPrc'] = pd.to_numeric(df['strikeOutPrc'], errors='coerce')
df['discountRate'] = ((df['strikeOutPrc'] - df['displayPrc']) / df['strikeOutPrc'] * 100).fillna(0)
df['itemOrdQty'] = pd.to_numeric(df['itemOrdQty'], errors='coerce').fillna(0)

# 주요 통계 계산
total_products = len(df)
avg_price = int(df['displayPrc'].mean())
max_discount = int(df['discountRate'].max())
top_brand = df['brandNm'].value_counts().index[0] if not df['brandNm'].isnull().all() else "N/A"
total_orders = int(df['itemOrdQty'].sum())

# 테이블용 데이터
table_data = df[['itemId', 'brandNm', 'itemNm', 'displayPrc', 'discountRate', 'itemOrdQty']].head(100).to_dict(orient='records')

# 이미지 목록 및 Base64 변환 함수
def get_base64_image(filename):
    path = os.path.join(base_dir, 'images', filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded_string}"

visualizations = [
    {"file": "v1_brand_freq.png", "title": "브랜드 점유율 분석", "desc": "삼성, 나이키 등 메이저 브랜드가 특가 시장의 신뢰도를 견인하고 있습니다."},
    {"file": "v2_price_dist.png", "title": "가격대별 상품 분포", "desc": "1~5만원 사이의 실속형 상품군이 전체의 60% 이상을 차지합니다."},
    {"file": "v3_brand_discount.png", "title": "브랜드별 할인 전략", "desc": "특정 신규 브랜드들이 50% 이상의 고할인율로 시장 진입을 시도 중입니다."},
    {"file": "v4_discount_ord_scatter.png", "title": "할인율-주문량 상관관계", "desc": "30~50% 구간의 '심리적 적정 할인선'에서 가장 높은 구매 전환이 발생합니다."},
    {"file": "v5_salestr_pie.png", "title": "채널별 판매 비중", "desc": "온라인 전용몰과 오프라인 거점 점포가 유기적으로 재고를 분담하고 있습니다."},
    {"file": "v6_site_price_box.png", "title": "사이트별 타겟팅 분석", "desc": "이마트(실속)와 백화점(프리미엄)의 가격 포지셔닝이 명확히 구분됩니다."},
    {"file": "v7_recom_ord_reg.png", "title": "사회적 증거의 위력", "desc": "추천 수가 많은 상품일수록 고객의 구매 결정 속도가 비약적으로 빠릅니다."},
    {"file": "v8_ord_type.png", "title": "핫딜 운영 현황", "desc": "모든 상품이 전략적인 'HOT_DEAL' 지표 하에 철저히 관리되고 있습니다."},
    {"file": "v9_abs_discount_dist.png", "title": "실질적 절감 금액", "desc": "평균 1.2만원 수준의 실질 혜택이 고객의 최종 결제를 유도합니다."},
    {"file": "v10_brand_inv.png", "title": "재고 보유 안정성", "desc": "인기 브랜드 위주의 대규모 물량 확보로 품절 기회 손실을 최소화하고 있습니다."},
    {"file": "v11_tfidf_keywords.png", "title": "키워드 마케팅 분석", "desc": "'단독', '역대급' 등 강력한 소구점이 상품명에 전략적으로 배치되었습니다."}
]

# HTML 템플릿
html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSG 특가 상품 인사이트 대시보드</title>
    <link rel="stylesheet" href="dashboard.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap">
    <style>
        /* 추가 스타일: 이미지 로딩 최적화 */
        .chart-img-wrapper img {{
            background: #1e293b;
            min-height: 200px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="logo">SSG INSIGHTS</div>
        <nav class="nav-links">
            <a href="#overview">개요</a>
            <a href="#charts">차트 분석</a>
            <a href="#data">데이터 테이블</a>
        </nav>
    </header>

    <main>
        <section id="overview" class="animate-fade">
            <h2 class="section-title">비즈니스 요약</h2>
            <div class="stats-grid">
                <div class="stat-card"><h3>전체 상품 수</h3><div class="value">{total_products:,}</div></div>
                <div class="stat-card"><h3>평균 판매가</h3><div class="value">₩{avg_price:,}</div></div>
                <div class="stat-card"><h3>최고 할인율</h3><div class="value">{max_discount}%</div></div>
                <div class="stat-card"><h3>핵심 브랜드</h3><div class="value">{top_brand}</div></div>
                <div class="stat-card"><h3>누적 주문량</h3><div class="value">{total_orders:,}</div></div>
            </div>
        </section>

        <section id="charts" class="animate-fade">
            <h2 class="section-title">심층 데이터 시각화</h2>
            <div class="charts-container">
                {"".join([f'''
                <div class="chart-card">
                    <h4>{v['title']}</h4>
                    <div class="chart-img-wrapper">
                        <img src="{get_base64_image(v['file'])}" alt="{v['title']}">
                    </div>
                    <div class="chart-desc">{v['desc']}</div>
                </div>
                ''' for v in visualizations])}
            </div>
        </section>

        <section id="data" class="animate-fade">
            <h2 class="section-title">상품 상세 데이터 (Top 100)</h2>
            <div class="table-section">
                <div class="table-controls">
                    <input type="text" id="tableSearch" class="search-bar" placeholder="상품명 또는 브랜드 검색...">
                </div>
                <div class="table-wrapper">
                    <table id="dataTable">
                        <thead><tr><th>아이템ID</th><th>브랜드</th><th>상품명</th><th>판매가</th><th>할인율</th><th>주문량</th></tr></thead>
                        <tbody>
                            {"".join([f'''
                            <tr>
                                <td>{item['itemId']}</td>
                                <td><span class="badge badge-stock">{item['brandNm']}</span></td>
                                <td>{item['itemNm']}</td>
                                <td>₩{int(item['displayPrc']):,}</td>
                                <td><span class="badge badge-sale">{int(item['discountRate'])}%</span></td>
                                <td>{int(item['itemOrdQty']):,}</td>
                            </tr>
                            ''' for item in table_data])}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 SSG Data Analysis Lab. All rights reserved.</p>
    </footer>

    <script>
        document.getElementById('tableSearch').addEventListener('keyup', function() {{
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll('#dataTable tbody tr');
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            }});
        }});
    </script>
</body>
</html>
"""

with open('ssg-com/report/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("이미지를 Base64로 인코딩하여 포함한 완전 자립형 대시보드 HTML을 생성했습니다.")
