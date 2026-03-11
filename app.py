import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Operations Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0f14 !important;
    color: #ffffff !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stHeader"] { background: #0d0f14 !important; }
[data-testid="stSidebar"] { background: #141720 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #141720;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #252a3a;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #9ca3af !important;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 14px;
}
.stTabs [aria-selected="true"] {
    background: #3b82f6 !important;
    color: #ffffff !important;
}

/* Metric cards */
.metric-card {
    background: #141720;
    border: 1px solid #252a3a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-card .label {
    color: #9ca3af;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.metric-card .value {
    color: #ffffff;
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
}
.metric-card .sub {
    color: #9ca3af;
    font-size: 12px;
    margin-top: 4px;
}
.metric-accent { border-top: 3px solid #3b82f6 !important; }
.metric-warn   { border-top: 3px solid #f59e0b !important; }
.metric-danger { border-top: 3px solid #ef4444 !important; }
.metric-success{ border-top: 3px solid #22c55e !important; }

/* Alert panel */
.alert-critical {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.4);
    border-left: 4px solid #ef4444;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #fca5a5;
    font-size: 14px;
}
.alert-warning {
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.4);
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #fde68a;
    font-size: 14px;
}
.alert-info {
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.4);
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #93c5fd;
    font-size: 14px;
}

/* Section headings */
.section-title {
    color: #9ca3af;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 28px 0 12px 0;
    border-bottom: 1px solid #252a3a;
    padding-bottom: 8px;
}

/* Form */
[data-testid="stForm"] {
    background: #141720;
    border: 1px solid #252a3a;
    border-radius: 12px;
    padding: 24px;
}
.stSelectbox label, .stNumberInput label, .stDateInput label,
.stMultiSelect label, .stTextInput label {
    color: #9ca3af !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] > div > div > input,
[data-testid="stDateInput"] > div > div > input {
    background: #0d0f14 !important;
    border: 1px solid #252a3a !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}

/* Buttons */
.stButton > button {
    background: #3b82f6 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    transition: background 0.2s;
}
.stButton > button:hover { background: #2563eb !important; }

/* Download button */
.stDownloadButton > button {
    background: #141720 !important;
    color: #3b82f6 !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* DataFrame tables */
[data-testid="stDataFrame"] { background: #141720; border-radius: 10px; }
.dataframe { background: #141720 !important; color: #ffffff !important; }
thead tr th { background: #0d0f14 !important; color: #9ca3af !important; font-size: 12px !important; }
tbody tr td { color: #ffffff !important; font-size: 13px !important; }
tbody tr:hover td { background: #1e2333 !important; }

/* Divider */
hr { border-color: #252a3a !important; }

/* Success/error messages */
.stSuccess { background: rgba(34,197,94,0.12) !important; color: #86efac !important; border-radius: 8px !important; }
.stError   { background: rgba(239,68,68,0.12) !important; color: #fca5a5 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
CSV_PATH = "operations_data.csv"

SELLERS = sorted([
    "swastiks","sapphire_dry_nuts","vrd_masale","bolas","hugs","candyfun",
    "bakemate","zoff_foods","suruchi_spices","kesarco","chuk_de","somnath",
    "go_desi","z_magnetism","sugandh","kirana_bazaar","farmkin","archita",
    "charliee","sanjeevani","meera_foods","tata","nutraj","annai","apsara_tea",
    "pansari","chaivik","cookme","soothe","sarkar_spices","upl","mangalam",
    "savour","daylight_fargo_manpasand","maharani","tattvam_luxury_incense",
    "vimaan","kc_punji_rewards","kiranaclub_loyalty_rewards","mantra","harnik",
    "rsb_super_stockist","hansha","hans","parimal","gongloo","yumms",
    "karnavati_tea_company","blg","derby","continental_coffee","broomify",
    "milan_supari","dnv","pickwick","famis_spices","desik","ruby","chotiwale",
    "mona","klaw","kalbavi","rasna",
])

COURIERS = ["DelhiveryOne", "Ekart", "Shiprocket"]
SR_COURIERS = ["Ekart_SR", "Delhivery_SR", "Xpressbees_SR", "DTDC_SR"]
UNDISPATCHED_REASONS = [
    "Courier pickup did not happen",
    "Pickup happened but shipments were handed over partially",
    "Shipments were not ready at the seller",
    "Courier Scanning issue",
]
PARTIAL_REASONS = ["Vehicle space constraints", "Seller handed over shipments partially"]
PACKING_DELAY_REASONS = [
    "Seller has not packed the orders",
    "Manpower issue",
    "Warehouse closed",
]
FAULT_TYPES = ["Seller Fault", "3PL Fault"]

COLUMNS = [
    "date","seller","orders_pending_packing","orders_packed",
    "orders_ready_dispatch","orders_picked_up","orders_not_packed_on_time",
    "orders_not_dispatched_on_time","undispatched_reason","courier",
    "sub_courier","partial_handover_reason","packing_delay_reason",
    "fault_type","orders_impacted","backlog_previous_day",
]

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df["date"] = pd.to_datetime(df["date"])
        return df
    return pd.DataFrame(columns=COLUMNS)


def save_row(row: dict):
    df_new = pd.DataFrame([row])
    if os.path.exists(CSV_PATH):
        df_new.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else:
        df_new.to_csv(CSV_PATH, mode="w", header=True, index=False)


def metric_card(label: str, value, sub: str = "", variant: str = "accent") -> str:
    return f"""
    <div class="metric-card metric-{variant}">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {"<div class='sub'>" + sub + "</div>" if sub else ""}
    </div>"""


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
  <div style="font-size:28px;">🚚</div>
  <div>
    <div style="font-size:22px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
      Logistics Operations Control Tower
    </div>
    <div style="font-size:13px;color:#9ca3af;">
      Real-time dispatch & packing operations monitoring
    </div>
  </div>
</div>
<hr style="margin:12px 0 20px 0;">
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📋 Daily Data Entry",
    "📊 Operations Dashboard",
    "🗂 Previous Entries"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA ENTRY
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📝 Submit Daily Operational Metrics</div>', unsafe_allow_html=True)

    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("Date", value=date.today())
        with col2:
            seller = st.selectbox("Seller", SELLERS)

        st.markdown('<div class="section-title">📦 Order Flow</div>', unsafe_allow_html=True)
     
    c1, c2, c3 = st.columns(3)
with c1:
    orders_pending_packing     = st.number_input("Orders Pending for Packing", min_value=0, value=0)
    orders_packed              = st.number_input("Orders Packed",               min_value=0, value=0)
with c2:
    orders_ready_dispatch      = st.number_input("Orders Ready for Dispatch",   min_value=0, value=0)
    orders_picked_up           = st.number_input("Orders Picked Up",            min_value=0, value=0)
with c3:
    orders_not_packed_on_time      = st.number_input("Orders Not Packed On Time",      min_value=0, value=0)
    orders_not_dispatched_on_time  = st.number_input("Orders Not Dispatched On Time",  min_value=0, value=0)

        backlog_previous_day = st.number_input("Backlog from Previous Day", min_value=0, value=0,
                                               help="Carry-forward orders from yesterday")

        st.markdown('<div class="section-title">🚛 Undispatched Reason</div>', unsafe_allow_html=True)
        undispatched_reason = st.selectbox("Why were orders not dispatched?",
                                           ["— Select —"] + UNDISPATCHED_REASONS)

        courier = sub_courier = partial_handover_reason = ""

        if undispatched_reason == "Courier pickup did not happen":
            courier = st.selectbox("Courier", COURIERS)
            if courier == "Shiprocket":
                sub_courier = st.selectbox("Shiprocket Sub-Courier", SR_COURIERS)

        elif undispatched_reason == "Pickup happened but shipments were handed over partially":
            partial_handover_reason = st.selectbox("Partial Handover Reason", PARTIAL_REASONS)

        st.markdown('<div class="section-title">⏱ Packing Delay</div>', unsafe_allow_html=True)
        packing_delay_reason = ""
        if orders_pending_packing > 0:
            packing_delay_reason = st.selectbox("Packing Delay Reason", PACKING_DELAY_REASONS)

        st.markdown('<div class="section-title">⚖️ Fault & Impact</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            fault_type = st.selectbox("Fault Type", FAULT_TYPES)
        with fc2:
            orders_impacted = st.number_input("Orders Impacted", min_value=0, value=0)

        submitted = st.form_submit_button("✅  Submit Entry", use_container_width=True)

    if submitted:
        row = {
            "date": str(entry_date),
            "seller": seller,
            "orders_pending_packing": orders_pending_packing,
            "orders_packed": orders_packed,
            "orders_ready_dispatch": orders_ready_dispatch,
            "orders_picked_up": orders_picked_up,
            "orders_not_packed_on_time": orders_not_packed_on_time,
            "orders_not_dispatched_on_time": orders_not_dispatched_on_time,
            "undispatched_reason": undispatched_reason if undispatched_reason != "— Select —" else "",
            "courier": courier,
            "sub_courier": sub_courier,
            "partial_handover_reason": partial_handover_reason,
            "packing_delay_reason": packing_delay_reason,
            "fault_type": fault_type,
            "orders_impacted": orders_impacted,
            "backlog_previous_day": backlog_previous_day,
        }
        save_row(row)
        st.success(f"✅ Entry saved for **{seller}** on **{entry_date}**")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    df = load_data()

    if df.empty:
        st.info("No data yet. Submit entries in the Daily Data Entry tab to populate the dashboard.")
        st.stop()

    # ── Filters ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        date_from = st.date_input("From Date", value=min_date, key="df")
    with f2:
        date_to = st.date_input("To Date", value=max_date, key="dt")
    with f3:
        sel_sellers = st.multiselect("Seller", sorted(df["seller"].unique()), default=[])
    with f4:
        couriers_in_data = [c for c in df["courier"].unique() if c and c != ""]
        sel_couriers = st.multiselect("Courier", sorted(couriers_in_data), default=[])

    # Apply filters
    mask = (df["date"].dt.date >= date_from) & (df["date"].dt.date <= date_to)
    if sel_sellers:
        mask &= df["seller"].isin(sel_sellers)
    if sel_couriers:
        mask &= df["courier"].isin(sel_couriers)
    fdf = df[mask].copy()

    if fdf.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    today_str = str(date.today())
    today_df = fdf[fdf["date"].dt.date == date.today()]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 KPI Summary</div>', unsafe_allow_html=True)

    total_pending    = int(fdf["orders_pending_packing"].sum())
    total_packed     = int(fdf["orders_packed"].sum())
    total_ready      = int(fdf["orders_ready_dispatch"].sum())
    total_pickup     = int(fdf["orders_picked_up"].sum())
    total_not_disp   = int(fdf["orders_not_dispatched_on_time"].sum())
    total_not_packed = int(fdf["orders_not_packed_on_time"].sum())
    total_impacted   = int(fdf["orders_impacted"].sum())
    pickup_rate      = (total_pickup / total_ready * 100) if total_ready > 0 else 0

    cols = st.columns(4)
    cards = [
        ("Pending Packing",       total_pending,    "orders", "warn"),
        ("Packed",                total_packed,     "orders", "success"),
        ("Ready for Dispatch",    total_ready,      "orders", "accent"),
        ("Picked Up",             total_pickup,     "orders", "success"),
        ("Not Dispatched On Time",total_not_disp,   "orders", "danger"),
        ("Not Packed On Time",    total_not_packed, "orders", "warn"),
        ("Total Orders Impacted", total_impacted,   "orders", "danger"),
        (f"Pickup Success Rate",  f"{pickup_rate:.1f}%", "orders picked / ready", "success" if pickup_rate >= 90 else "warn"),
    ]
    for i, (label, val, sub, variant) in enumerate(cards):
        with cols[i % 4]:
            st.markdown(metric_card(label, val, sub, variant), unsafe_allow_html=True)

    # ── Alerts ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🚨 Operations Alert Panel</div>', unsafe_allow_html=True)
    alerts = []

    # Seller with highest packing delays today
    if not today_df.empty:
        top_delay = today_df.groupby("seller")["orders_not_packed_on_time"].sum().idxmax()
        top_delay_val = today_df.groupby("seller")["orders_not_packed_on_time"].sum().max()
        if top_delay_val > 0:
            alerts.append(("critical", f"⚠️ <b>Packing Alert (Today):</b> <b>{top_delay}</b> has the highest packing delays today — <b>{top_delay_val}</b> orders not packed on time."))

        # Courier with missed pickups today
        missed_today = today_df[today_df["undispatched_reason"] == "Courier pickup did not happen"]
        if not missed_today.empty:
            top_courier = missed_today.groupby("courier")["orders_impacted"].sum().idxmax()
            top_courier_val = missed_today.groupby("courier")["orders_impacted"].sum().max()
            alerts.append(("critical", f"🚛 <b>Courier Failure (Today):</b> <b>{top_courier}</b> missed pickups today — <b>{top_courier_val}</b> orders impacted."))

    # Critical: >100 orders impacted
    critical_rows = fdf[fdf["orders_impacted"] > 100]
    if not critical_rows.empty:
        for _, row in critical_rows.iterrows():
            alerts.append(("critical", f"🔴 <b>Critical Issue:</b> <b>{row['seller']}</b> on <b>{row['date'].date()}</b> — <b>{int(row['orders_impacted'])}</b> orders impacted. Fault: {row['fault_type']}."))

    # Low pickup rate
    if pickup_rate < 80 and total_ready > 0:
        alerts.append(("warning", f"📉 <b>Low Pickup Rate:</b> Overall pickup success is <b>{pickup_rate:.1f}%</b> — below 80% threshold."))

    if not alerts:
        st.markdown('<div class="alert-info">✅ No critical alerts. Operations appear normal for the selected period.</div>', unsafe_allow_html=True)
    else:
        for atype, msg in alerts[:8]:
            cls = "alert-critical" if atype == "critical" else "alert-warning"
            st.markdown(f'<div class="{cls}">{msg}</div>', unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    chart_bg = "#141720"
    chart_font = "#9ca3af"
    grid_color = "#252a3a"

    def styled_fig(fig):
        fig.update_layout(
            paper_bgcolor=chart_bg, plot_bgcolor=chart_bg,
            font=dict(color=chart_font, size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(bgcolor=chart_bg, bordercolor=grid_color),
        )
        fig.update_xaxes(gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=chart_font))
        fig.update_yaxes(gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=chart_font))
        return fig

    st.markdown('<div class="section-title">📈 Charts</div>', unsafe_allow_html=True)

    row1c1, row1c2 = st.columns(2)

    with row1c1:
        seller_pending = fdf.groupby("seller")["orders_pending_packing"].sum().reset_index()
        seller_pending = seller_pending[seller_pending["orders_pending_packing"] > 0].sort_values("orders_pending_packing", ascending=True).tail(15)
        if not seller_pending.empty:
            fig = px.bar(seller_pending, x="orders_pending_packing", y="seller", orientation="h",
                         title="Seller-wise Pending Packing", color_discrete_sequence=["#f59e0b"])
            st.plotly_chart(styled_fig(fig), use_container_width=True)
        else:
            st.info("No pending packing data.")

    with row1c2:
        courier_fail = fdf[fdf["undispatched_reason"] == "Courier pickup did not happen"]
        if not courier_fail.empty:
            cf_grp = courier_fail.groupby("courier")["orders_impacted"].sum().reset_index()
            cf_grp.columns = ["Courier", "Orders Impacted"]
            fig = px.bar(cf_grp, x="Courier", y="Orders Impacted",
                         title="Courier Pickup Failures (Orders Impacted)",
                         color_discrete_sequence=["#ef4444"])
            st.plotly_chart(styled_fig(fig), use_container_width=True)
        else:
            st.info("No courier pickup failures in selected range.")

    row2c1, row2c2 = st.columns(2)

    with row2c1:
        pd_df = fdf[fdf["packing_delay_reason"] != ""].groupby("packing_delay_reason")["orders_impacted"].sum().reset_index()
        if not pd_df.empty:
            fig = px.pie(pd_df, names="packing_delay_reason", values="orders_impacted",
                         title="Packing Delay Reasons Breakdown",
                         color_discrete_sequence=["#f59e0b","#ef4444","#3b82f6"])
            fig.update_traces(textfont_color="#ffffff")
            st.plotly_chart(styled_fig(fig), use_container_width=True)
        else:
            st.info("No packing delay data.")

    with row2c2:
        ph_df = fdf[fdf["partial_handover_reason"] != ""].groupby("partial_handover_reason")["orders_impacted"].sum().reset_index()
        if not ph_df.empty:
            fig = px.pie(ph_df, names="partial_handover_reason", values="orders_impacted",
                         title="Partial Handover Reasons",
                         color_discrete_sequence=["#3b82f6","#22c55e"])
            fig.update_traces(textfont_color="#ffffff")
            st.plotly_chart(styled_fig(fig), use_container_width=True)
        else:
            st.info("No partial handover data.")

    row3c1, row3c2 = st.columns(2)

    with row3c1:
        daily_undisp = fdf.groupby(fdf["date"].dt.date)["orders_not_dispatched_on_time"].sum().reset_index()
        daily_undisp.columns = ["date", "Not Dispatched On Time"]
        fig = px.line(daily_undisp, x="date", y="Not Dispatched On Time",
                      title="Daily Undispatched Orders Trend",
                      color_discrete_sequence=["#ef4444"], markers=True)
        fig.update_traces(line_width=2)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with row3c2:
        daily_rate = fdf.groupby(fdf["date"].dt.date).agg(
            picked=("orders_picked_up","sum"),
            ready=("orders_ready_dispatch","sum")
        ).reset_index()
        daily_rate["Pickup Rate %"] = (daily_rate["picked"] / daily_rate["ready"].replace(0, float("nan")) * 100).round(1)
        fig = px.line(daily_rate, x="date", y="Pickup Rate %",
                      title="Daily Pickup Success Rate Trend",
                      color_discrete_sequence=["#22c55e"], markers=True)
        fig.update_traces(line_width=2)
        fig.add_hline(y=90, line_dash="dash", line_color="#f59e0b",
                      annotation_text="90% target", annotation_font_color="#f59e0b")
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    # ── Tables ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Seller Performance Table</div>', unsafe_allow_html=True)
    seller_tbl = fdf.groupby("seller").agg(
        Pending_Packing=("orders_pending_packing","sum"),
        Packed=("orders_packed","sum"),
        Ready_for_Dispatch=("orders_ready_dispatch","sum"),
        Picked_Up=("orders_picked_up","sum"),
        Not_Packed_On_Time=("orders_not_packed_on_time","sum"),
        Not_Dispatched_On_Time=("orders_not_dispatched_on_time","sum"),
        Total_Impacted=("orders_impacted","sum"),
    ).reset_index()
    seller_tbl["Pickup_%"] = (seller_tbl["Picked_Up"] / seller_tbl["Ready_for_Dispatch"].replace(0, float("nan")) * 100).round(1).fillna(0).astype(str) + "%"
    seller_tbl.columns = ["Seller","Pending Packing","Packed","Ready for Dispatch","Picked Up","Not Packed On Time","Not Dispatched On Time","Total Impacted","Pickup %"]
    st.dataframe(seller_tbl, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">🚛 Courier Performance Table</div>', unsafe_allow_html=True)
    courier_rows = fdf[fdf["courier"] != ""]
    if not courier_rows.empty:
        c_total = courier_rows.groupby("courier").agg(
            Total_Attempts=("orders_ready_dispatch","sum"),
            Orders_Impacted=("orders_impacted","sum"),
        ).reset_index()
        missed_grp = fdf[fdf["undispatched_reason"] == "Courier pickup did not happen"].groupby("courier").size().reset_index(name="Missed_Pickups")
        c_tbl = c_total.merge(missed_grp, on="courier", how="left").fillna(0)
        c_tbl["Missed_Pickups"] = c_tbl["Missed_Pickups"].astype(int)
        c_tbl["Reliability_Score"] = ((1 - c_tbl["Missed_Pickups"] / c_tbl["Total_Attempts"].replace(0, 1)) * 100).clip(0, 100).round(1).astype(str) + "%"
        c_tbl.columns = ["Courier","Total Pickup Attempts","Orders Impacted","Missed Pickups","Reliability Score"]
        st.dataframe(c_tbl, use_container_width=True, hide_index=True)
    else:
        st.info("No courier data available.")

    # ── Root Cause Analysis ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔎 Root Cause Analysis</div>', unsafe_allow_html=True)
    rca1, rca2 = st.columns(2)

    with rca1:
        fault_df = fdf.groupby("fault_type")["orders_impacted"].sum().reset_index()
        if not fault_df.empty and fault_df["orders_impacted"].sum() > 0:
            fig = px.pie(fault_df, names="fault_type", values="orders_impacted",
                         title="Fault Ownership: Seller vs 3PL",
                         color_discrete_sequence=["#ef4444","#3b82f6"])
            fig.update_traces(textfont_color="#ffffff")
            st.plotly_chart(styled_fig(fig), use_container_width=True)

    with rca2:
        # Combined breakdown
        rca_data = []
        for reason in PACKING_DELAY_REASONS:
            val = fdf[fdf["packing_delay_reason"] == reason]["orders_impacted"].sum()
            if val > 0:
                rca_data.append({"Category": "Packing Delay", "Reason": reason, "Orders": int(val)})
        for reason in PARTIAL_REASONS:
            val = fdf[fdf["partial_handover_reason"] == reason]["orders_impacted"].sum()
            if val > 0:
                rca_data.append({"Category": "Partial Handover", "Reason": reason, "Orders": int(val)})
        courier_miss = fdf[fdf["undispatched_reason"] == "Courier pickup did not happen"].groupby("courier")["orders_impacted"].sum()
        for c, v in courier_miss.items():
            if v > 0:
                rca_data.append({"Category": "Courier Failure", "Reason": c, "Orders": int(v)})

        if rca_data:
            rca_df = pd.DataFrame(rca_data)
            fig = px.bar(rca_df, x="Orders", y="Reason", color="Category", orientation="h",
                         title="Root Cause Breakdown",
                         color_discrete_sequence=["#f59e0b","#3b82f6","#ef4444"])
            st.plotly_chart(styled_fig(fig), use_container_width=True)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">⬇️ Export Data</div>', unsafe_allow_html=True)
    csv_export = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥  Export Filtered Data as CSV",
        data=csv_export,
        file_name=f"logistics_ops_{date_from}_to_{date_to}.csv",
        mime="text/csv",
    )
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PREVIOUS ENTRIES
# ══════════════════════════════════════════════════════════════════════════════

with tab3:

    st.markdown('<div class="section-title">📂 View / Edit Previous Entries</div>', unsafe_allow_html=True)

    df = load_data()

    if df.empty:
        st.info("No entries available.")
        st.stop()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input("Start Date", value=df["date"].min().date())

    with col2:
        end_date = st.date_input("End Date", value=df["date"].max().date())

    with col3:
        seller_filter = st.selectbox("Seller", ["All"] + SELLERS)

    # Apply filters
    filtered = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]

    if seller_filter != "All":
        filtered = filtered[filtered["seller"] == seller_filter]

    if filtered.empty:
        st.warning("No entries match the selected filters.")
        st.stop()

    filtered_display = filtered.copy()
    filtered_display["date"] = filtered_display["date"].dt.strftime("%Y-%m-%d")

    st.dataframe(filtered_display, use_container_width=True)

    # Select entry
    st.markdown("### Select Entry to Edit / Delete")

    selected_index = st.selectbox(
        "Choose entry",
        filtered.index,
        format_func=lambda x: f"{df.loc[x,'date'].date()} | {df.loc[x,'seller']}"
    )

    selected_row = df.loc[selected_index]

    st.write("#### Selected Entry")
    st.dataframe(pd.DataFrame([selected_row]))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑 Delete Entry"):

            df = df.drop(selected_index)
            df.to_csv(CSV_PATH, index=False)

            st.success("Entry deleted successfully.")
            st.rerun()

    with col2:
        if st.button("✏️ Edit Entry"):
            st.warning("Delete this entry and resubmit a corrected one from the Daily Entry tab.")
