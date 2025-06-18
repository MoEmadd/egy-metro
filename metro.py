import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

# تعريف خطوط المترو بناءً على الخريطة الرسمية
metro_lines = {
    "الخط الأول": [
        "المرج الجديدة", "المرج", "عزبة النخل", "عين شمس", "المطرية", "حلمية الزيتون", "حدائق الزيتون",
        "سراي القبة", "حمامات القبة", "كوبري القبة", "منشية الصدر", "الدمرداش", "غمرة", "الشهداء",
        "ناصر", "السادات", "سعد زغلول", "السيدة زينب", "المنيل", "مار جرجس", "الملك الصالح", "دار السلام",
        "حدائق المعادي", "المعادي", "ثكنات المعادي", "طره البلد", "كوتسيكا", "طرة الأسمنت", "المعصرة",
        "حدائق حلوان", "وادي حوف", "جامعة حلوان", "عين حلوان", "حلوان"
    ],
    "الخط الثاني": [
        "شبرا الخيمة", "كلية الزراعة", "المظلات", "الخلفاوي", "سانت تريزا", "روض الفرج", "مسرة",
        "الشهداء", "العتبة", "محمد نجيب", "السادات", "الأوبرا", "الدقي", "البحوث", "جامعة القاهرة",
        "فيصل", "الجيزة", "أم المصريين", "ساقية مكي", "المنيب"
    ],
    "الخط الثالث": [
        "عدلي منصور", "الهايكستب", "عمر بن الخطاب", "قباء", "هشام بركات", "النزهة", "نادي الشمس",
        "ألف مسكن", "هارون", "هليوبوليس", "كلية البنات", "الأهرام", "ميدان هليوبوليس", "أرض المعارض",
        "الاستاد", "عباس العقاد", "العباسية", "عبده باشا", "الجيش", "باب الشعرية", "العتبة",
        "ناصر", "السودان", "إمبابة", "البوهي", "القومية العربية", "الطريق الدائري", "محور روض الفرج"
    ]
}

# إنشاء الجراف
G = nx.Graph()
station_to_lines = {}

for line, stations in metro_lines.items():
    for i in range(len(stations) - 1):
        G.add_edge(stations[i], stations[i + 1], line=line)
    for station in stations:
        station_to_lines.setdefault(station, set()).add(line)

# ربط المحطات المشتركة بين الخطوط (محطات التحويل)
shared_stations = [
    ("الشهداء", ["الخط الأول", "الخط الثاني"]),
    ("السادات", ["الخط الأول", "الخط الثاني"]),
    ("العتبة", ["الخط الثاني", "الخط الثالث"]),
    ("ناصر", ["الخط الأول", "الخط الثالث"]),
]

# لا حاجة لتكرار العقد بل نكتفي بأن كل محطة واحدة مرتبطة بكل الخطوط
all_stations = sorted(station_to_lines.keys())

# دالة لإيجاد المسار
def find_best_path(start, end):
    if start == end:
        return [start], "أنت بالفعل في المحطة المطلوبة."

    # تحقق من وجود خط مباشر
    for line, stations in metro_lines.items():
        if start in stations and end in stations:
            i1, i2 = stations.index(start), stations.index(end)
            path = stations[i1:i2+1] if i1 < i2 else stations[i2:i1+1][::-1]
            desc = f"🚇 اركب {line} من {start} إلى {end}:\n" + " ← ".join(path[1:])
            return path, desc

    # أقصر مسار باستخدام NetworkX
    try:
        path = nx.shortest_path(G, start, end)
    except nx.NetworkXNoPath:
        return None, "❌ لا يوجد مسار بين المحطتين."

    # وصف المسار والتحويلات
    description = []
    current_line = None
    for i in range(len(path) - 1):
        edge_data = G.get_edge_data(path[i], path[i + 1])
        line = edge_data['line']
        if line != current_line:
            description.append(f"\n🚇 اركب {line} من {path[i]}")
            current_line = line
        description.append(f" ← {path[i + 1]}")
    return path, "".join(description)

# دالة لرسم المسار
def draw_path(path):
    pos = nx.spring_layout(G, seed=42)
    reshaped_labels = {n: get_display(arabic_reshaper.reshape(n)) for n in G.nodes}
    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw(G, pos, node_color="lightgray", node_size=100, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=reshaped_labels, font_size=9, ax=ax)
    if path:
        edges = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_color="lightblue", node_size=300, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="red", width=2, ax=ax)
    ax.set_title(get_display(arabic_reshaper.reshape("مسار المترو")))
    ax.axis("off")
    st.pyplot(fig)

# إعداد Streamlit
st.set_page_config(page_title="دليل مترو القاهرة", layout="centered")

st.markdown(
    "<h1 style='text-align: center;'>🚇دليل مترو القاهرة</h1>",
    unsafe_allow_html=True
)


start = st.selectbox("اختر محطة البداية", all_stations)
end = st.selectbox("اختر محطة الوصول", all_stations)

if st.button("اعرض المسار"):
    path, desc = find_best_path(start, end)
    if path:
        st.text(desc)
        draw_path(path)
    else:
        st.error(desc)
