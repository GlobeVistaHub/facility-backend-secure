import streamlit as st
import sqlite3
import pandas as pd
from ai_agent import analyze_maintenance_request # Importing your AI Brain

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="GlobeVistaHub | Maintenance AI", page_icon="🛠️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-title { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1E3A8A; text-align: right; }
    .stDataFrame { direction: rtl; } 
    .stTextInput>div>div>input { direction: rtl; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🛠️ نظام إدارة البلاغات الذكي (AI Dashboard)</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- DATABASE FUNCTIONS ---
def load_data():
    conn = sqlite3.connect('tickets.db')
    query = "SELECT ticket_number as 'رقم الطلب', phone_number as 'رقم الهاتف', category as 'التصنيف', description as 'الوصف', status as 'الحالة', timestamp as 'وقت التسجيل' FROM tickets ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def save_ticket(phone, category, description):
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    # Generate a simple ticket number
    cursor.execute("SELECT COUNT(*) FROM tickets")
    count = cursor.fetchone()[0]
    ticket_num = f"TKT-{1000 + count + 1}"
    
    cursor.execute('''
        INSERT INTO tickets (ticket_number, phone_number, category, description, status)
        VALUES (?, ?, ?, ?, 'جديد')
    ''', (ticket_num, phone, category, description))
    conn.commit()
    conn.close()
    return ticket_num

# --- THE SIMULATOR (Input Section) ---
st.subheader("🤖 محاكي استلام البلاغات (WhatsApp Simulator)")
with st.form("new_ticket_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 3])
    with col1:
        phone_input = st.text_input("رقم هاتف العميل (Phone)", value="+201012345678")
    with col2:
        msg_input = st.text_input("رسالة العميل (Customer Message)", placeholder="اكتب مشكلة العميل هنا (مثال: التكييف مش شغال)...")
    
    submitted = st.form_submit_button("إرسال للذكاء الاصطناعي (Send to AI)")

# --- PROCESS THE MESSAGE ---
if submitted and msg_input:
    with st.spinner("جاري التحليل... (AI is thinking...)"):
        # 1. Send the message to Gemini
        ai_response_text = analyze_maintenance_request(msg_input)
        
        try:
            import json
            # Clean the response just in case
            clean_text = ai_response_text.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(clean_text)
            
            category = ai_data.get('category', 'أخرى')
            description = ai_data.get('description', msg_input)
            
            # 2. Save it to the database
            new_ticket = save_ticket(phone_input, category, description)
            
            st.success(f"تم تسجيل البلاغ بنجاح! رقم الطلب: {new_ticket} | التصنيف: {category}")
        except Exception as e:
            st.error(f"حدث خطأ في تحليل البيانات. (Error parsing AI response: {e})")

st.markdown("---")

# --- THE DASHBOARD (Output Section) ---
data = load_data()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("إجمالي البلاغات", len(data))
col2.metric("تكييف (AC)", len(data[data['التصنيف'] == 'تكييف']))
col3.metric("كهرباء (Electrical)", len(data[data['التصنيف'] == 'كهرباء']))
col4.metric("سباكة (Plumbing)", len(data[data['التصنيف'] == 'سباكة']))
col5.metric("أخرى (Other)", len(data[data['التصنيف'] == 'أخرى']))

st.subheader("📋 سجل البلاغات (Ticket Log)")
if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)