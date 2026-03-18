import streamlit as st
import pandas as pd
import os
from datetime import date

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="Triveni Enterprises", layout="wide")


# --- डेटा लोड और सेव करने के फंक्शन ---
def save_data(df, filename):
    df.to_csv(filename, index=False)


def load_data(filename, columns):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame(columns=columns)


# फाइल डेटाबेस
SALES_FILE = "triveni_sales.csv"
EXPENSE_FILE = "triveni_expenses.csv"

# डेटा लोड करना
sales_df = load_data(SALES_FILE, ["तारीख", "ग्राहक", "मोबाइल", "ब्लॉक_टाइप", "कुल_बिल", "जमा_राशि", "बकाया"])
expense_df = load_data(EXPENSE_FILE, ["तारीख", "विवरण", "श्रेणी", "रकम"])


# --- सुरक्षा: लॉगिन सिस्टम ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🏗️ त्रिवेणी एंटरप्राइजेज")
        st.subheader("सुरक्षित लॉगिन")
        user_pass = st.text_input("पासवर्ड दर्ज करें", type="password")

        if st.button("लॉगिन"):
            # यहाँ 'st.secrets' का उपयोग हो रहा है जो पासवर्ड को छुपा कर रखता है
            if user_pass == st.secrets["db_password"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ गलत पासवर्ड! कृपया सही पासवर्ड डालें।")
        return False
    return True


if check_password():
    # साइडबार मेन्यू
    st.sidebar.title("त्रिवेणी मेन्यू")
    menu = ["🏠 डैशबोर्ड", "💰 नई बिक्री & बिल", "📊 उधारी (Ledger)", "💸 खर्च दर्ज करें", "📜 रिकॉर्ड हिस्ट्री"]
    choice = st.sidebar.selectbox("विकल्प चुनें", menu)

    # लॉगआउट बटन
    if st.sidebar.button("लॉगआउट"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- 1. डैशबोर्ड ---
    if choice == "🏠 डैशबोर्ड":
        st.header("व्यापार की वर्तमान स्थिति")
        col1, col2, col3 = st.columns(3)

        total_income = sales_df["जमा_राशि"].sum()
        total_pending = sales_df["बकाया"].sum()
        total_expense = expense_df["रकम"].sum()

        col1.metric("कुल नकद आय", f"₹{total_income}")
        col2.metric("कुल मार्केट उधारी", f"₹{total_pending}", delta_color="inverse")
        col3.metric("कुल खर्च", f"₹{total_expense}")

    # --- 2. नई बिक्री और बिल ---
    elif choice == "💰 नई बिक्री & बिल":
        st.subheader("नया बिल और चालान एंट्री")
        with st.form("billing_form"):
            c1, c2 = st.columns(2)
            with c1:
                cust = st.text_input("ग्राहक का नाम")
                phone = st.text_input("मोबाइल नंबर")
                block = st.selectbox("ब्लॉक का प्रकार", ["Zig-Zag (60mm)", "I-Shape (80mm)", "Square", "Hexagon"])
            with c2:
                bill_amt = st.number_input("कुल बिल राशि (₹)", min_value=0.0)
                paid_amt = st.number_input("आज जमा की गई राशि (₹)", min_value=0.0)

            if st.form_submit_button("बिल सेव करें"):
                balance = bill_amt - paid_amt
                new_sale = pd.DataFrame([[date.today(), cust, phone, block, bill_amt, paid_amt, balance]],
                                        columns=sales_df.columns)
                sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
                save_data(sales_df, SALES_FILE)
                st.success(f"एंट्री सुरक्षित! {cust} का बकाया: ₹{balance}")

    # --- 3. उधारी (Ledger) ---
    elif choice == "📊 उधारी (Ledger)":
        st.subheader("ग्राहकों का बकाया हिसाब (उधार खाता)")
        pending_df = sales_df[sales_df["बकाया"] > 0]
        if not pending_df.empty:
            st.dataframe(pending_df[["तारीख", "ग्राहक", "मोबाइल", "कुल_बिल", "बकाया"]])
        else:
            st.success("कोई उधारी बकाया नहीं है!")

    # --- 4. खर्च दर्ज करें ---
    elif choice == "💸 खर्च दर्ज करें":
        st.subheader("फैक्ट्री के खर्चों का हिसाब")
        with st.form("exp_form"):
            desc = st.text_input("खर्च का विवरण (जैसे: लेबर पेमेंट, डीजल)")
            cat = st.selectbox("श्रेणी", ["कच्चा माल", "लेबर", "बिजली/डीजल", "अन्य"])
            amt = st.number_input("रकम (₹)", min_value=0.0)
            if st.form_submit_button("खर्च सुरक्षित करें"):
                new_exp = pd.DataFrame([[date.today(), desc, cat, amt]], columns=expense_df.columns)
                expense_df = pd.concat([expense_df, new_exp], ignore_index=True)
                save_data(expense_df, EXPENSE_FILE)
                st.warning("खर्चा दर्ज कर लिया गया है।")

    # --- 5. रिकॉर्ड हिस्ट्री ---
    elif choice == "📜 रिकॉर्ड हिस्ट्री":
        st.subheader("सभी पुराने लेन-देन")
        st.dataframe(sales_df)