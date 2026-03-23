import streamlit as st
import pandas as pd
import os
from datetime import date

# --- PAGE CONFIG ---
st.set_page_config(page_title="Triveni Enterprises", layout="wide", page_icon="🏗️")

# --- LANGUAGE SYSTEM ---
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

lang = st.sidebar.radio("🌐 Language / भाषा", ["EN", "HI"],
                        index=0 if st.session_state.lang == "EN" else 1)
st.session_state.lang = lang

# --- TRANSLATIONS ---
T = {
    "EN": {
        "title": "🏗️ Triveni Enterprises",
        "login": "Secure Login",
        "password": "Enter Password",
        "login_btn": "Login",
        "wrong_pass": "Wrong password!",
        "menu": "Menu",
        "dashboard": "🏠 Dashboard",
        "new_sale": "💰 New Sale & Billing",
        "ledger": "📊 Ledger",
        "expense": "💸 Add Expense",
        "logout": "Logout",
        "status": "Business Overview",
        "income": "Total Income",
        "pending": "Total Pending",
        "expense_total": "Total Expense",
        "cust_name": "Customer Name",
        "phone": "Phone Number",
        "bill": "Total Bill (₹)",
        "paid": "Paid Amount (₹)",
        "save_bill": "Save Bill",
        "ledger_title": "Pending Ledger",
        "no_pending": "No pending dues!",
        "expense_desc": "Expense Description",
        "category": "Category",
        "amount": "Amount",
        "save_exp": "Save Expense",
        "exp_saved": "Expense saved!",
        "sales_history": "📜 Sales History",
        "expense_history": "💸 Expense History"
    },
    "HI": {
        "title": "🏗️ त्रिवेणी एंटरप्राइजेज",
        "login": "सुरक्षित लॉगिन",
        "password": "पासवर्ड दर्ज करें",
        "login_btn": "लॉगिन",
        "wrong_pass": "गलत पासवर्ड!",
        "menu": "मेन्यू",
        "dashboard": "🏠 डैशबोर्ड",
        "new_sale": "💰 नई बिक्री & बिल",
        "ledger": "📊 उधारी",
        "expense": "💸 खर्च दर्ज करें",
        "logout": "लॉगआउट",
        "status": "व्यापार की स्थिति",
        "income": "कुल आय",
        "pending": "कुल उधारी",
        "expense_total": "कुल खर्च",
        "cust_name": "ग्राहक का नाम",
        "phone": "मोबाइल नंबर",
        "bill": "कुल बिल राशि (₹)",
        "paid": "जमा राशि (₹)",
        "save_bill": "बिल सेव करें",
        "ledger_title": "उधारी खाता",
        "no_pending": "कोई उधारी नहीं!",
        "expense_desc": "खर्च का विवरण",
        "category": "श्रेणी",
        "amount": "रकम",
        "save_exp": "खर्च सेव करें",
        "exp_saved": "खर्च सेव हो गया!",
        "sales_history": "📜 बिक्री हिस्ट्री",
        "expense_history": "💸 खर्च हिस्ट्री"
    }
}

def t(key):
    return T[st.session_state.lang][key]

# --- CATEGORY MAP ---
CATEGORY_MAP = {
    "EN": ["Raw Material", "Labor", "Electricity/Diesel", "Other"],
    "HI": ["कच्चा माल", "लेबर", "बिजली/डीजल", "अन्य"]
}

# --- DATA FUNCTIONS ---
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

sales_df = load_data(SALES_FILE, ["date", "customer", "phone", "block", "bill", "paid", "balance"])
expense_df = load_data(EXPENSE_FILE, ["date", "desc", "cat", "amt"])

# --- FIX OLD HINDI DATA ---
sales_df.rename(columns={
    "तारीख": "date",
    "ग्राहक": "customer",
    "मोबाइल": "phone",
    "ब्लॉक_टाइप": "block",
    "कुल_बिल": "bill",
    "जमा_राशि": "paid",
    "बकाया": "balance"
}, inplace=True)

expense_df.rename(columns={
    "तारीख": "date",
    "विवरण": "desc",
    "श्रेणी": "cat",
    "रकम": "amt"
}, inplace=True)

# Ensure numeric
sales_df["paid"] = pd.to_numeric(sales_df.get("paid"), errors="coerce").fillna(0)
sales_df["balance"] = pd.to_numeric(sales_df.get("balance"), errors="coerce").fillna(0)
expense_df["amt"] = pd.to_numeric(expense_df.get("amt"), errors="coerce").fillna(0)

# --- LOGIN ---
def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.title(t("title"))
        st.subheader(t("login"))

        # FORM → allows Enter key submission
        with st.form("login_form"):
            pwd = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("login_btn"))

            if submitted:
                if pwd == st.secrets["db_password"]:
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error(t("wrong_pass"))  # already translated

        st.stop()
    return True

# --- MAIN APP ---
if check_password():

    st.sidebar.title(t("menu"))

    menu = [
        t("dashboard"),
        t("new_sale"),
        t("ledger"),
        t("expense"),
        t("sales_history"),
        t("expense_history")
    ]

    choice = st.sidebar.selectbox("Select", menu)

    if st.sidebar.button(t("logout")):
        st.session_state.auth = False
        st.rerun()

    # --- DASHBOARD ---
    if choice == t("dashboard"):
        st.header(t("status"))

        col1, col2, col3 = st.columns(3)

        col1.metric(t("income"), f"₹{sales_df['paid'].sum():,.2f}")
        col2.metric(t("pending"), f"₹{sales_df['balance'].sum():,.2f}")
        col3.metric(t("expense_total"), f"₹{expense_df['amt'].sum():,.2f}")

    # --- NEW SALE ---
    elif choice == t("new_sale"):
        st.subheader(t("new_sale"))

        with st.form("sale"):
            cust = st.text_input(t("cust_name"))
            phone = st.text_input(t("phone"))
            bill = st.number_input(t("bill"), min_value=0.0)
            paid = st.number_input(t("paid"), min_value=0.0)

            if st.form_submit_button(t("save_bill")):
                if cust:
                    bal = bill - paid
                    new = pd.DataFrame([[date.today(), cust, phone, "", bill, paid, bal]],
                                       columns=sales_df.columns)
                    save_data(pd.concat([sales_df, new], ignore_index=True), SALES_FILE)
                    st.success("Saved!")
                else:
                    st.error("Enter name")

    # --- LEDGER ---
    elif choice == t("ledger"):
        st.subheader(t("ledger_title"))
        df = sales_df[sales_df["balance"] > 0]
        st.dataframe(df if not df.empty else pd.DataFrame())

    # --- EXPENSE ---
    elif choice == t("expense"):
        st.subheader(t("expense"))

        with st.form("exp"):
            desc = st.text_input(t("expense_desc"))
            cat = st.selectbox(t("category"), CATEGORY_MAP[st.session_state.lang])
            amt = st.number_input(t("amount"), min_value=0.0)

            if st.form_submit_button(t("save_exp")):
                if desc and amt > 0:
                    new = pd.DataFrame([[date.today(), desc, cat, amt]],
                                       columns=expense_df.columns)
                    save_data(pd.concat([expense_df, new], ignore_index=True), EXPENSE_FILE)
                    st.success(t("exp_saved"))

    # --- SALES HISTORY ---
    elif choice == t("sales_history"):
        st.subheader(t("sales_history"))
        st.dataframe(sales_df, use_container_width=True)

    # --- EXPENSE HISTORY ---
    elif choice == t("expense_history"):
        st.subheader(t("expense_history"))
        st.dataframe(expense_df, use_container_width=True)