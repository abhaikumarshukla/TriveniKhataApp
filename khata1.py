import streamlit as st
import pandas as pd
import os
from datetime import date

# --- 1. पेज कॉन्फ़िगरेशन (Page Config) ---
st.set_page_config(page_title="Triveni Enterprises", layout="wide", page_icon="🏗️")


# --- 2. डेटा लोड और सेव (Data Functions) ---
# NOTE: CSV files on Streamlit Cloud are temporary.
# Use Google Sheets for permanent storage in the future.
def save_data(df, filename):
    df.to_csv(filename, index=False)


def load_data(filename, columns):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)


SALES_FILE = "triveni_sales.csv"
EXPENSE_FILE = "triveni_expenses.csv"

sales_df = load_data(SALES_FILE, ["तारीख", "ग्राहक", "मोबाइल", "ब्लॉक_टाइप", "कुल_बिल", "जमा_राशि", "बकाया"])
expense_df = load_data(EXPENSE_FILE, ["तारीख", "विवरण", "श्रेणी", "रकम"])


# --- 3. लॉगिन सिस्टम (Secure Login System) ---
def check_password():
    """Returns True if the user had the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🏗️ त्रिवेणी एंटरप्राइजेज")
        st.subheader("सुरक्षित लॉगिन")

        # पासवर्ड इनपुट
        user_pass = st.text_input("पासवर्ड दर्ज करें", type="password")

        if st.button("लॉगिन"):
            # Streamlit Cloud के 'Settings > Secrets' में db_password सेट करें
            if user_pass == st.secrets["db_password"]:
                st.session_state["authenticated"] = True
                st.rerun()  # सही पासवर्ड पर एक बार रिफ्रेश करें
            else:
                st.error("❌ गलत पासवर्ड! कृपया सही पासवर्ड डालें।")

        # सबसे महत्वपूर्ण: अगर लॉग इन नहीं है, तो यहाँ कोड रोक दें
        st.stop()
        return False

    return True


# --- 4. मुख्य ऐप (Main App Logic) ---
if check_password():
    # साइडबार मेन्यू
    st.sidebar.title("त्रिवेणी मेन्यू")
    menu = ["🏠 डैशबोर्ड", "💰 नई बिक्री & बिल", "📊 उधारी (Ledger)", "💸 खर्च दर्ज करें", "📜 रिकॉर्ड हिस्ट्री"]
    choice = st.sidebar.selectbox("विकल्प चुनें", menu)

    # लॉगआउट बटन
    if st.sidebar.button("लॉगआउट"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- डैशबोर्ड ---
    if choice == "🏠 डैशबोर्ड":
        st.header("व्यापार की वर्तमान स्थिति")
        col1, col2, col3 = st.columns(3)

        # गणना (Calculations)
        total_income = pd.to_numeric(sales_df["जमा_राशि"], errors='coerce').sum()
        total_pending = pd.to_numeric(sales_df["बकाया"], errors='coerce').sum()
        total_expense = pd.to_numeric(expense_df["रकम"], errors='coerce').sum()

        col1.metric("कुल नकद आय", f"₹{total_income:,.2f}")
        col2.metric("कुल मार्केट उधारी", f"₹{total_pending:,.2f}", delta_color="inverse")
        col3.metric("कुल खर्च", f"₹{total_expense:,.2f}")

    # --- नई बिक्री और बिल ---
    elif choice == "💰 नई बिक्री & बिल":
        st.subheader("नया बिल और चालान एंट्री")
        with st.form("billing_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                cust = st.text_input("ग्राहक का नाम")
                phone = st.text_input("मोबाइल नंबर")
                block = st.selectbox("ब्लॉक का प्रकार", ["Zig-Zag (60mm)", "I-Shape (80mm)", "Square", "Hexagon"])
            with c2:
                bill_amt = st.number_input("कुल बिल राशि (₹)", min_value=0.0, step=1.0)
                paid_amt = st.number_input("आज जमा की गई राशि (₹)", min_value=0.0, step=1.0)

            if st.form_submit_button("बिल सेव करें"):
                if cust:
                    balance = bill_amt - paid_amt
                    new_sale = pd.DataFrame([[date.today(), cust, phone, block, bill_amt, paid_amt, balance]],
                                            columns=sales_df.columns)
                    updated_sales = pd.concat([sales_df, new_sale], ignore_index=True)
                    save_data(updated_sales, SALES_FILE)
                    st.success(f"एंट्री सुरक्षित! {cust} का बकाया: ₹{balance}")
                else:
                    st.error("कृपया ग्राहक का नाम भरें।")

    # --- उधारी (Ledger) ---
    elif choice == "📊 उधारी (Ledger)":
        st.subheader("ग्राहकों का बकाया हिसाब (उधार खाता)")
        pending_df = sales_df[pd.to_numeric(sales_df["बकाया"], errors='coerce') > 0]
        if not pending_df.empty:
            st.dataframe(pending_df[["तारीख", "ग्राहक", "मोबाइल", "कुल_बिल", "बकाया"]], use_container_width=True)
        else:
            st.success("कोई उधारी बकाया नहीं है!")

    # --- खर्च दर्ज करें ---
    elif choice == "💸 खर्च दर्ज करें":
        st.subheader("फैक्ट्री के खर्चों का हिसाब")
        with st.form("exp_form", clear_on_submit=True):
            desc = st.text_input("खर्च का विवरण (जैसे: लेबर पेमेंट, डीजल)")
            cat = st.selectbox("श्रेणी", ["कच्चा माल", "लेबर", "बिजली/डीजल", "अन्य"])
            amt = st.number_input("रकम (₹)", min_value=0.0, step=1.0)
            if st.form_submit_button("खर्च सुरक्षित करें"):
                if desc and amt > 0:
                    new_exp = pd.DataFrame([[date.today(), desc, cat, amt]], columns=expense_df.columns)
                    updated_expense = pd.concat([expense_df, new_exp], ignore_index=True)
                    save_data(updated_expense, EXPENSE_FILE)
                    st.info("खर्चा दर्ज कर लिया गया है।")
                else:
                    st.error("विवरण और रकम सही से भरें।")

    # --- रिकॉर्ड हिस्ट्री ---
    elif choice == "📜 रिकॉर्ड हिस्ट्री":
        st.subheader("सभी पुराने लेन-देन")
        st.dataframe(sales_df, use_container_width=True)