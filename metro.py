import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

# تعريف خطوط المترو طبقاً للصورة الأخيرة
metro_lines = {
    "الخط الأول": [
        "حلوان", "عين حلوان", "جامعة حلوان", "وادي حوف", "حدائق حلوان", "المعصرة", "طرة الأسمنت", "كوتسيكا", "طره البلد",
        "ثكنات المعادي", "المعادي", "حدائق المعادي", "دار السلام", "الملك الصالح", "مار جرجس", "السيدة زينب",
        "سعد زغلول", "السادات", "ناصر", "الشهداء", "غمرة", "الدمرداش", "منشية الصدر", "كوبري القبة", "حمامات القبة",
        "سراي القبة", "حدائق الزيتون", "حلمية الزيتون", "المطرية", "عين شمس", "عزبة النخل", "المرج", "المرج الجديدة"
    ],
    "الخط الثاني": [
        "المنيب", "ساقية مكي", "أم المصريين", "الجيزة", "فيصل", "جامعة القاهرة", "البحوث", "الدقي", "الأوبرا",
        "السادات", "محمد نجيب", "العتبة", "الشهداء", "مسرة", "روض الفرج", "سانت تريزا", "الخلفاوي", "المظلات",
        "كلية الزراعة", "شبرا الخيمة"
    ],
    "الخط الثالث": [
        "عدلي منصور", "الهايكستب", "عمر بن الخطاب", "قباء", "هشام بركات", "النزهة", "نادي الشمس", "ألف مسكن",
        "هارون", "هليوبوليس", "كلية البنات", "الأهرام", "ميدان هليوبوليس", "أرض المعارض", "الاستاد", "عباس العقاد",
        "العباسية", "عبده باشا", "باب الشعرية", "العتبة"
    ]
}

# إنشاء الجراف وربط المحطات
G = nx.Graph()
station_to_lines = {}

for line, stations in metro_lines.items():
    for i in range(len(stations) - 1):
        G.add_edge(stations[i], stations[i + 1], line=line)
    for station in stations:
        station_to_lines.setdefault(station, set()).add(line)

all_stations = sorted(station_to_lines.keys())

# دالة إيجاد أفضل مسار
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

    # استخدام NetworkX
    try:
        path = nx.shortest_path(G, start, end)
    except nx.NetworkXNoPath:
        return None, "❌ لا يوجد مسار بين المحطتين."

    # بناء الوصف
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

# رسم المسار
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
st.title("🚇 دليل مترو القاهرة")

start = st.selectbox("اختر محطة البداية", all_stations)
end = st.selectbox("اختر محطة الوصول", all_stations)

if st.button("اعرض المسار"):
    path, desc = find_best_path(start, end)
    if path:
        st.text(desc)
        draw_path(path)
    else:
        st.error(desc)
