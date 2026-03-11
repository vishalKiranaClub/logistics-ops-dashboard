import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Operations Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0f14 !important;
    color: #ffffff !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stHeader"] { background: #0d0f14 !important; }
[data-testid="stSidebar"] { background: #141720 !important; }

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
.metric-card {
    background: #141720;
    border: 1px solid #252a3a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 12px;
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
.metric-card .sub { color: #9ca3af; font-size: 12px; margin-top: 4px; }
.metric-accent { border-top: 3px solid #3b82f6 !important; }
.metric-warn   { border-top: 3px solid #f59e0b !important; }
.metric-danger { border-top: 3px solid #ef4444 !important; }
.metric-success{ border-top: 3px solid #22c55e !important; }

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
.entry-card {
    background: #141720;
    border: 1px solid #252a3a;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.entry-seller { font-size: 15px; font-weight: 700; color: #ffffff; }
.entry-date   { font-size: 12px; color: #9ca3af; }
.entry-meta   { font-size: 12px; color: #9ca3af; display: flex; gap: 16px; flex-wrap: wrap; margin-top: 8px; }
.entry-badge  {
    background: rgba(59,130,246,0.15);
    color: #93c5fd;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}
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
.stButton > button {
    background: #3b82f6 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
}
.stButton > button:hover { background: #2563eb !important; }
.stDownloadButton > button {
    background: #141720 !important;
    color: #3b82f6 !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stDataFrame"] { background: #141720; border-radius: 10px; }
hr { border-color: #252a3a !important; }
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
    "Shipments were not ready",
    "Courier scanning issue",
]
PARTIAL_REASONS = ["Vehicle space constraints", "Seller handed over shipments partially"]
PACKING_DELAY_REASONS = [
    "Seller has not packed the orders",
    "Manpower issue",
    "Warehouse closed",
]
FAULT_TYPES = ["Seller Fault", "3PL Fault"]

COLUMNS = [
    "date","seller",
    "orders_pending_packing","orders_ready_dispatch",
    "orders_not_packed_on_time","orders_picked_up",
    "orders_not_dispatched_on_time",
    "undispatched_reason","courier","sub_courier",
    "partial_handover_reason","packing_delay_reason",
    "fault_type","orders_impacted","backlog_previous_day",
]

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df["date"] = pd.to_datetime(df["date"])
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        # fill NaN for numeric cols
        for col in ["orders_pending_packing","orders_ready_dispatch","orders_not_packed_on_time",
                    "orders_picked_up","orders_not_dispatched_on_time","orders_impacted","backlog_previous_day"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        return df.reset_index(drop=True)
    return pd.DataFrame(columns=COLUMNS)


def save_data(df: pd.DataFrame):
    df.to_csv(CSV_PATH, index=False)


def save_row(row: dict):
    df_new = pd.DataFrame([row])
    if os.path.exists(CSV_PATH):
        df_new.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else:
        df_new.to_csv(CSV_PATH, mode="w", header=True, index=False)


def metric_card(label, value, sub="", variant="accent"):
    return f"""
    <div class="metric-card metric-{variant}">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {"<div class='sub'>" + sub + "</div>" if sub else ""}
    </div>"""


def render_order_flow_fields(defaults=None, key_prefix="new"):
    """Render order flow + undispatched + packing + fault fields outside a form."""
    d = defaults or {}

    c1, c2 = st.columns(2)
    with c1:
        orders_pending_packing = st.number_input(
            "Orders Pending for Packing", min_value=0,
            value=int(d.get("orders_pending_packing", 0)), key=f"{key_prefix}_pending")
        orders_ready_dispatch = st.number_input(
            "Orders Ready for Dispatch", min_value=0,
            value=int(d.get("orders_ready_dispatch", 0)), key=f"{key_prefix}_ready")
    with c2:
        orders_not_packed_on_time = st.number_input(
            "Orders Not Packed On Time", min_value=0,
            value=int(d.get("orders_not_packed_on_time", 0)), key=f"{key_prefix}_notpacked")
        orders_picked_up = st.number_input(
            "Orders Picked Up", min_value=0,
            value=int(d.get("orders_picked_up", 0)), key=f"{key_prefix}_pickedup")

    orders_not_dispatched_on_time = max(0, int(orders_ready_dispatch) - int(orders_picked_up))
    st.caption(f"📌 Orders Not Dispatched On Time (auto-calculated): **{orders_not_dispatched_on_time}**")

    st.markdown('<div class="section-title">🚛 Undispatched Reason</div>', unsafe_allow_html=True)
    cur_undisp = d.get("undispatched_reason", "")
    undisp_opts = ["— Select —"] + UNDISPATCHED_REASONS
    undisp_idx = undisp_opts.index(cur_undisp) if cur_undisp in undisp_opts else 0
    undispatched_reason = st.selectbox(
        "Why were orders not dispatched?", undisp_opts, index=undisp_idx, key=f"{key_prefix}_undisp")

    courier = sub_courier = partial_handover_reason = ""

    if undispatched_reason == "Courier pickup did not happen":
        cur_c = d.get("courier", COURIERS[0])
        c_idx = COURIERS.index(cur_c) if cur_c in COURIERS else 0
        courier = st.selectbox("Courier", COURIERS, index=c_idx, key=f"{key_prefix}_courier")
        if courier == "Shiprocket":
            cur_sc = d.get("sub_courier", SR_COURIERS[0])
            sc_idx = SR_COURIERS.index(cur_sc) if cur_sc in SR_COURIERS else 0
            sub_courier = st.selectbox("Shiprocket Sub-Courier", SR_COURIERS, index=sc_idx, key=f"{key_prefix}_subcourier")

    elif undispatched_reason == "Pickup happened but shipments were handed over partially":
        cur_ph = d.get("partial_handover_reason", PARTIAL_REASONS[0])
        ph_idx = PARTIAL_REASONS.index(cur_ph) if cur_ph in PARTIAL_REASONS else 0
        partial_handover_reason = st.selectbox(
            "Partial Handover Reason", PARTIAL_REASONS, index=ph_idx, key=f"{key_prefix}_partial")

    st.markdown('<div class="section-title">⏱ Packing Delay</div>', unsafe_allow_html=True)
    packing_delay_opts = ["— Not Applicable —"] + PACKING_DELAY_REASONS
    cur_pd = d.get("packing_delay_reason", "")
    pd_idx = packing_delay_opts.index(cur_pd) if cur_pd in packing_delay_opts else 0
    packing_delay_raw = st.selectbox(
        "Packing Delay Reason", packing_delay_opts, index=pd_idx,
        key=f"{key_prefix}_packdelay",
        help="Select a reason if orders were pending for packing")
    packing_delay_reason = "" if packing_delay_raw == "— Not Applicable —" else packing_delay_raw

    st.markdown('<div class="section-title">⚖️ Fault & Impact</div>', unsafe_allow_html=True)
    fc1, fc2 = st.columns(2)
    with fc1:
        cur_ft = d.get("fault_type", FAULT_TYPES[0])
        ft_idx = FAULT_TYPES.index(cur_ft) if cur_ft in FAULT_TYPES else 0
        fault_type = st.selectbox("Fault Type", FAULT_TYPES, index=ft_idx, key=f"{key_prefix}_fault")
    with fc2:
        orders_impacted = st.number_input(
            "Orders Impacted", min_value=0,
            value=int(d.get("orders_impacted", 0)), key=f"{key_prefix}_impacted")

    backlog_previous_day = st.number_input(
        "Backlog from Previous Day", min_value=0,
        value=int(d.get("backlog_previous_day", 0)), key=f"{key_prefix}_backlog",
        help="Carry-forward orders from yesterday")

    return dict(
        orders_pending_packing=orders_pending_packing,
        orders_ready_dispatch=orders_ready_dispatch,
        orders_not_packed_on_time=orders_not_packed_on_time,
        orders_picked_up=orders_picked_up,
        orders_not_dispatched_on_time=orders_not_dispatched_on_time,
        undispatched_reason=undispatched_reason if undispatched_reason != "— Select —" else "",
        courier=courier,
        sub_courier=sub_courier,
        partial_handover_reason=partial_handover_reason,
        packing_delay_reason=packing_delay_reason,
        fault_type=fault_type,
        orders_impacted=orders_impacted,
        backlog_previous_day=backlog_previous_day,
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
  <div style="font-size:28px;">🚚</div>
  <div>
    <div style="font-size:22px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
      Logistics Operations Control Tower
    </div>
    <div style="font-size:13px;color:#9ca3af;">Real-time dispatch & packing operations monitoring</div>
  </div>
</div>
<hr style="margin:12px 0 20px 0;">
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋  Daily Data Entry", "📂  Previous Entries", "📊  Operations Dashboard"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA ENTRY
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📝 Submit Daily Operational Metrics</div>', unsafe_allow_html=True)

    n1, n2 = st.columns(2)
    with n1:
        entry_date = st.date_input("Date", value=date.today(), key="new_date")
    with n2:
        seller = st.selectbox("Seller", SELLERS, key="new_seller")

    st.markdown('<div class="section-title">📦 Order Flow</div>', unsafe_allow_html=True)
    flow = render_order_flow_fields(key_prefix="new")

    if st.button("✅  Submit Entry", use_container_width=True, key="submit_new"):
        row = {"date": str(entry_date), "seller": seller, **flow}
        save_row(row)
        st.success(f"✅ Entry saved for **{seller}** on **{entry_date}**")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PREVIOUS ENTRIES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🗂 Browse & Manage Previous Entries</div>', unsafe_allow_html=True)

    df_all = load_data()

    if df_all.empty:
        st.info("No entries yet. Submit data in the Daily Data Entry tab.")
    else:
        ef1, ef2, ef3 = st.columns(3)
        with ef1:
            e_min = df_all["date"].min().date()
            e_max = df_all["date"].max().date()
            e_from = st.date_input("From", value=e_min, key="e_from")
        with ef2:
            e_to = st.date_input("To", value=e_max, key="e_to")
        with ef3:
            e_sellers = st.multiselect("Filter by Seller", sorted(df_all["seller"].unique()), key="e_sel")

        emask = (df_all["date"].dt.date >= e_from) & (df_all["date"].dt.date <= e_to)
        if e_sellers:
            emask &= df_all["seller"].isin(e_sellers)
        filtered = df_all[emask].copy()

        st.markdown(
            f"<div style='color:#9ca3af;font-size:13px;margin-bottom:12px;'>"
            f"Showing <b style='color:#fff'>{len(filtered)}</b> entries</div>",
            unsafe_allow_html=True)

        if filtered.empty:
            st.warning("No entries match the selected filters.")
        else:
            # Build display labels
            entry_options = []
            for idx, row in filtered.sort_values("date", ascending=False).iterrows():
                lbl = (f"[{row['date'].date()}]  {row['seller']}  —  "
                       f"Pending: {row['orders_pending_packing']}  |  "
                       f"Ready: {row['orders_ready_dispatch']}  |  "
                       f"Picked Up: {row['orders_picked_up']}  |  "
                       f"Impacted: {row['orders_impacted']}")
                entry_options.append((lbl, idx))

            label_to_idx = {lbl: idx for lbl, idx in entry_options}
            selected_label = st.selectbox(
                "Select an entry to view / edit / delete",
                list(label_to_idx.keys()),
                key="entry_select"
            )

            if selected_label:
                sel_idx = label_to_idx[selected_label]
                sel_row = df_all.loc[sel_idx]

                st.markdown('<div class="section-title">👁 Entry Details</div>', unsafe_allow_html=True)

                undisp_html = (
                    f"<div style='margin-top:8px;font-size:12px;color:#9ca3af;'>"
                    f"Undispatched Reason: <b style='color:#fde68a'>{sel_row.get('undispatched_reason','')}</b></div>"
                    if sel_row.get("undispatched_reason") else ""
                )
                st.markdown(f"""
                <div class="entry-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="entry-seller">📦 {sel_row['seller']}</span>
                    <span class="entry-date">{sel_row['date'].date()}</span>
                  </div>
                  <div class="entry-meta">
                    <span>Pending Packing: <b style="color:#f59e0b">{sel_row['orders_pending_packing']}</b></span>
                    <span>Ready for Dispatch: <b style="color:#3b82f6">{sel_row['orders_ready_dispatch']}</b></span>
                    <span>Not Packed On Time: <b style="color:#ef4444">{sel_row['orders_not_packed_on_time']}</b></span>
                    <span>Picked Up: <b style="color:#22c55e">{sel_row['orders_picked_up']}</b></span>
                    <span>Not Dispatched: <b style="color:#ef4444">{sel_row['orders_not_dispatched_on_time']}</b></span>
                    <span>Impacted: <b style="color:#ef4444">{sel_row['orders_impacted']}</b></span>
                    <span>Fault: <span class="entry-badge">{sel_row.get('fault_type','')}</span></span>
                  </div>
                  {undisp_html}
                </div>
                """, unsafe_allow_html=True)

                ac1, ac2 = st.columns(2)
                with ac1:
                    do_edit = st.button("✏️  Edit This Entry", key="btn_edit", use_container_width=True)
                with ac2:
                    do_delete = st.button("🗑  Delete This Entry", key="btn_delete", use_container_width=True)

                # ── DELETE ────────────────────────────────────────────────────
                if do_delete:
                    st.session_state["confirm_delete"] = sel_idx

                if st.session_state.get("confirm_delete") == sel_idx:
                    st.warning(
                        f"⚠️ Are you sure you want to delete the entry for "
                        f"**{sel_row['seller']}** on **{sel_row['date'].date()}**? "
                        f"This cannot be undone.")
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("✅ Yes, Delete", key="confirm_del_yes"):
                            df_updated = df_all.drop(index=sel_idx).reset_index(drop=True)
                            save_data(df_updated)
                            st.session_state.pop("confirm_delete", None)
                            st.session_state.pop("editing_idx", None)
                            st.success("Entry deleted successfully.")
                            st.rerun()
                    with dc2:
                        if st.button("❌ Cancel", key="confirm_del_no"):
                            st.session_state.pop("confirm_delete", None)
                            st.rerun()

                # ── EDIT ──────────────────────────────────────────────────────
                if do_edit:
                    st.session_state["editing_idx"] = sel_idx

                if st.session_state.get("editing_idx") == sel_idx:
                    st.markdown('<div class="section-title">✏️ Edit Entry</div>', unsafe_allow_html=True)

                    ed1, ed2 = st.columns(2)
                    with ed1:
                        new_date = st.date_input("Date", value=sel_row["date"].date(), key="edit_date")
                    with ed2:
                        s_idx = SELLERS.index(sel_row["seller"]) if sel_row["seller"] in SELLERS else 0
                        new_seller = st.selectbox("Seller", SELLERS, index=s_idx, key="edit_seller")

                    st.markdown('<div class="section-title">📦 Order Flow</div>', unsafe_allow_html=True)
                    new_flow = render_order_flow_fields(defaults=sel_row.to_dict(), key_prefix="edit")

                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("💾  Save Changes", use_container_width=True, key="save_edit"):
                            df_updated = df_all.copy()
                            updated = {"date": str(new_date), "seller": new_seller, **new_flow}
                            for col, val in updated.items():
                                df_updated.at[sel_idx, col] = val
                            save_data(df_updated)
                            st.session_state.pop("editing_idx", None)
                            st.success(f"✅ Entry updated for **{new_seller}** on **{new_date}**")
                            st.rerun()
                    with ec2:
                        if st.button("✖  Cancel Edit", use_container_width=True, key="cancel_edit"):
                            st.session_state.pop("editing_idx", None)
                            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    df = load_data()

    if df.empty:
        st.info("No data yet. Submit entries in the Daily Data Entry tab to populate the dashboard.")
        st.stop()

    # Filters
    st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        date_from = st.date_input("From Date", value=df["date"].min().date(), key="dash_from")
    with f2:
        date_to = st.date_input("To Date", value=df["date"].max().date(), key="dash_to")
    with f3:
        sel_sellers = st.multiselect("Seller", sorted(df["seller"].unique()), default=[], key="dash_sel")
    with f4:
        raw_couriers = df["courier"].dropna().astype(str).str.strip()
        couriers_in_data = sorted([c for c in raw_couriers.unique() if c and c != "nan"])
        sel_couriers = st.multiselect("Courier", couriers_in_data, default=[], key="dash_courier")

    mask = (df["date"].dt.date >= date_from) & (df["date"].dt.date <= date_to)
    if sel_sellers:
        mask &= df["seller"].isin(sel_sellers)
    if sel_couriers:
        mask &= df["courier"].isin(sel_couriers)
    fdf = df[mask].copy()

    if fdf.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    today_df = fdf[fdf["date"].dt.date == date.today()]

    # KPIs
    st.markdown('<div class="section-title">📊 KPI Summary</div>', unsafe_allow_html=True)
    total_pending    = int(fdf["orders_pending_packing"].sum())
    total_ready      = int(fdf["orders_ready_dispatch"].sum())
    total_pickup     = int(fdf["orders_picked_up"].sum())
    total_not_disp   = int(fdf["orders_not_dispatched_on_time"].sum())
    total_not_packed = int(fdf["orders_not_packed_on_time"].sum())
    total_impacted   = int(fdf["orders_impacted"].sum())
    pickup_rate      = (total_pickup / total_ready * 100) if total_ready > 0 else 0

    kpi_cols = st.columns(4)
    cards = [
        ("Pending Packing",        total_pending,         "orders", "warn"),
        ("Ready for Dispatch",     total_ready,           "orders", "accent"),
        ("Picked Up",              total_pickup,          "orders", "success"),
        ("Not Dispatched On Time", total_not_disp,        "orders", "danger"),
        ("Not Packed On Time",     total_not_packed,      "orders", "warn"),
        ("Total Orders Impacted",  total_impacted,        "orders", "danger"),
        ("Pickup Success Rate",    f"{pickup_rate:.1f}%", "picked / ready",
         "success" if pickup_rate >= 90 else ("warn" if pickup_rate >= 70 else "danger")),
    ]
    for i, (label, val, sub, variant) in enumerate(cards):
        with kpi_cols[i % 4]:
            st.markdown(metric_card(label, val, sub, variant), unsafe_allow_html=True)

    # Alerts
    st.markdown('<div class="section-title">🚨 Operations Alert Panel</div>', unsafe_allow_html=True)
    alerts = []

    if not today_df.empty:
        top_delay_s = today_df.groupby("seller")["orders_not_packed_on_time"].sum()
        if top_delay_s.max() > 0:
            alerts.append(("critical",
                f"⚠️ <b>Packing Alert (Today):</b> <b>{top_delay_s.idxmax()}</b> has the highest packing delays — "
                f"<b>{int(top_delay_s.max())}</b> orders not packed on time."))

        missed_today = today_df[today_df["undispatched_reason"] == "Courier pickup did not happen"]
        if not missed_today.empty:
            top_c_s = missed_today.groupby("courier")["orders_impacted"].sum()
            alerts.append(("critical",
                f"🚛 <b>Courier Failure (Today):</b> <b>{top_c_s.idxmax()}</b> missed pickups — "
                f"<b>{int(top_c_s.max())}</b> orders impacted."))

        not_ready_today = today_df[today_df["undispatched_reason"] == "Shipments were not ready"]
        if not not_ready_today.empty:
            alerts.append(("warning",
                f"📦 <b>Shipments Not Ready (Today):</b> "
                f"<b>{len(not_ready_today)}</b> seller(s) had shipments not ready for dispatch."))

        scanning_today = today_df[today_df["undispatched_reason"] == "Courier scanning issue"]
        if not scanning_today.empty:
            scan_impact = int(scanning_today["orders_impacted"].sum())
            alerts.append(("warning",
                f"🔍 <b>Courier Scanning Issue (Today):</b> "
                f"<b>{len(scanning_today)}</b> instance(s) — <b>{scan_impact}</b> orders impacted."))

    for _, row in fdf[fdf["orders_impacted"] > 100].iterrows():
        alerts.append(("critical",
            f"🔴 <b>Critical Issue:</b> <b>{row['seller']}</b> on <b>{row['date'].date()}</b> — "
            f"<b>{int(row['orders_impacted'])}</b> orders impacted. Fault: {row['fault_type']}."))

    if pickup_rate < 80 and total_ready > 0:
        alerts.append(("warning",
            f"📉 <b>Low Pickup Rate:</b> Overall pickup success is <b>{pickup_rate:.1f}%</b> — below 80% threshold."))

    if not alerts:
        st.markdown('<div class="alert-info">✅ No critical alerts. Operations appear normal.</div>', unsafe_allow_html=True)
    else:
        for atype, msg in alerts[:10]:
            cls = "alert-critical" if atype == "critical" else "alert-warning"
            st.markdown(f'<div class="{cls}">{msg}</div>', unsafe_allow_html=True)

    # Charts
    chart_bg = "#141720"
    chart_font = "#9ca3af"
    grid_color = "#252a3a"

    def sfig(fig):
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

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        sp = fdf.groupby("seller")["orders_pending_packing"].sum().reset_index()
        sp = sp[sp["orders_pending_packing"] > 0].sort_values("orders_pending_packing", ascending=True).tail(15)
        if not sp.empty:
            st.plotly_chart(sfig(px.bar(sp, x="orders_pending_packing", y="seller", orientation="h",
                title="Seller-wise Pending Packing", color_discrete_sequence=["#f59e0b"])), use_container_width=True)
        else:
            st.info("No pending packing data.")

    with r1c2:
        cf = fdf[fdf["undispatched_reason"] == "Courier pickup did not happen"]
        if not cf.empty:
            cfg = cf.groupby("courier")["orders_impacted"].sum().reset_index()
            cfg.columns = ["Courier","Orders Impacted"]
            st.plotly_chart(sfig(px.bar(cfg, x="Courier", y="Orders Impacted",
                title="Courier Pickup Failures", color_discrete_sequence=["#ef4444"])), use_container_width=True)
        else:
            st.info("No courier pickup failures in selected range.")

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        pdd = fdf[fdf["packing_delay_reason"].fillna("") != ""].groupby("packing_delay_reason")["orders_impacted"].sum().reset_index()
        if not pdd.empty:
            fig = px.pie(pdd, names="packing_delay_reason", values="orders_impacted",
                         title="Packing Delay Reasons", color_discrete_sequence=["#f59e0b","#ef4444","#3b82f6"])
            fig.update_traces(textfont_color="#ffffff")
            st.plotly_chart(sfig(fig), use_container_width=True)
        else:
            st.info("No packing delay data.")

    with r2c2:
        phd = fdf[fdf["partial_handover_reason"].fillna("") != ""].groupby("partial_handover_reason")["orders_impacted"].sum().reset_index()
        if not phd.empty:
            fig = px.pie(phd, names="partial_handover_reason", values="orders_impacted",
                         title="Partial Handover Reasons", color_discrete_sequence=["#3b82f6","#22c55e"])
            fig.update_traces(textfont_color="#ffffff")
            st.plotly_chart(sfig(fig), use_container_width=True)
        else:
            st.info("No partial handover data.")

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        du = fdf.groupby(fdf["date"].dt.date)["orders_not_dispatched_on_time"].sum().reset_index()
        du.columns = ["date","Not Dispatched On Time"]
        fig = px.line(du, x="date", y="Not Dispatched On Time",
                      title="Daily Undispatched Orders Trend",
                      color_discrete_sequence=["#ef4444"], markers=True)
        fig.update_traces(line_width=2)
        st.plotly_chart(sfig(fig), use_container_width=True)

    with r3c2:
        dr = fdf.groupby(fdf["date"].dt.date).agg(
            picked=("orders_picked_up","sum"), ready=("orders_ready_dispatch","sum")).reset_index()
        dr["Pickup Rate %"] = (dr["picked"] / dr["ready"].replace(0, float("nan")) * 100).round(1)
        fig = px.line(dr, x="date", y="Pickup Rate %",
                      title="Daily Pickup Success Rate Trend",
                      color_discrete_sequence=["#22c55e"], markers=True)
        fig.update_traces(line_width=2)
        fig.add_hline(y=90, line_dash="dash", line_color="#f59e0b",
                      annotation_text="90% target", annotation_font_color="#f59e0b")
        st.plotly_chart(sfig(fig), use_container_width=True)

    # Undispatched reason bar
    und = fdf[fdf["undispatched_reason"].fillna("") != ""].groupby("undispatched_reason")["orders_impacted"].sum().reset_index()
    if not und.empty:
        st.plotly_chart(sfig(px.bar(und, x="undispatched_reason", y="orders_impacted",
            title="Orders Impacted by Undispatched Reason",
            color_discrete_sequence=["#3b82f6","#f59e0b","#ef4444"])), use_container_width=True)

    # Tables
    st.markdown('<div class="section-title">📋 Seller Performance Table</div>', unsafe_allow_html=True)
    stbl = fdf.groupby("seller").agg(
        Pending_Packing=("orders_pending_packing","sum"),
        Ready_for_Dispatch=("orders_ready_dispatch","sum"),
        Picked_Up=("orders_picked_up","sum"),
        Not_Packed_On_Time=("orders_not_packed_on_time","sum"),
        Not_Dispatched_On_Time=("orders_not_dispatched_on_time","sum"),
        Total_Impacted=("orders_impacted","sum"),
    ).reset_index()
    stbl["Pickup_%"] = (stbl["Picked_Up"] / stbl["Ready_for_Dispatch"].replace(0, float("nan")) * 100
                        ).round(1).fillna(0).astype(str) + "%"
    stbl.columns = ["Seller","Pending Packing","Ready for Dispatch","Picked Up",
                    "Not Packed On Time","Not Dispatched On Time","Total Impacted","Pickup %"]
    st.dataframe(stbl, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">🚛 Courier Performance Table</div>', unsafe_allow_html=True)
    crow = fdf[fdf["courier"].fillna("").astype(str).str.strip().str.len() > 0]
    if not crow.empty:
        ctotal = crow.groupby("courier").agg(
            Total_Attempts=("orders_ready_dispatch","sum"),
            Orders_Impacted=("orders_impacted","sum")).reset_index()
        mgrp = fdf[fdf["undispatched_reason"] == "Courier pickup did not happen"] \
            .groupby("courier").size().reset_index(name="Missed_Pickups")
        ctbl = ctotal.merge(mgrp, on="courier", how="left").fillna(0)
        ctbl["Missed_Pickups"] = ctbl["Missed_Pickups"].astype(int)
        ctbl["Reliability_Score"] = (
            (1 - ctbl["Missed_Pickups"] / ctbl["Total_Attempts"].replace(0, 1)) * 100
        ).clip(0, 100).round(1).astype(str) + "%"
        ctbl.columns = ["Courier","Total Pickup Attempts","Orders Impacted","Missed Pickups","Reliability Score"]
        st.dataframe(ctbl, use_container_width=True, hide_index=True)
    else:
        st.info("No courier data available.")

    # Root Cause
    st.markdown('<div class="section-title">🔎 Root Cause Analysis</div>', unsafe_allow_html=True)
    rca1, rca2 = st.columns(2)
    with rca1:
        faultdf = fdf.groupby("fault_type")["orders_impacted"].sum().reset_index()
        if not faultdf.empty and faultdf["orders_impacted"].sum() > 0:
            fig = px.pie(faultdf, names="fault_type", values="orders_impacted",
                         title="Fault Ownership: Seller vs 3PL",
                         color_discrete_sequence=["#ef4444","#3b82f6"])
            fig.update_traces(textfont_color="#ffffff")
            st.plotly_chart(sfig(fig), use_container_width=True)

    with rca2:
        rca_data = []
        for reason in PACKING_DELAY_REASONS:
            v = fdf[fdf["packing_delay_reason"] == reason]["orders_impacted"].sum()
            if v > 0: rca_data.append({"Category":"Packing Delay","Reason":reason,"Orders":int(v)})
        for reason in PARTIAL_REASONS:
            v = fdf[fdf["partial_handover_reason"] == reason]["orders_impacted"].sum()
            if v > 0: rca_data.append({"Category":"Partial Handover","Reason":reason,"Orders":int(v)})
        for c, v in fdf[fdf["undispatched_reason"] == "Courier pickup did not happen"] \
                .groupby("courier")["orders_impacted"].sum().items():
            if v > 0: rca_data.append({"Category":"Courier Failure","Reason":c,"Orders":int(v)})
        v = fdf[fdf["undispatched_reason"] == "Shipments were not ready"]["orders_impacted"].sum()
        if v > 0: rca_data.append({"Category":"Not Ready","Reason":"Shipments not ready","Orders":int(v)})

        if rca_data:
            rdf = pd.DataFrame(rca_data)
            st.plotly_chart(sfig(px.bar(rdf, x="Orders", y="Reason", color="Category", orientation="h",
                title="Root Cause Breakdown",
                color_discrete_sequence=["#f59e0b","#3b82f6","#ef4444","#22c55e"])), use_container_width=True)

    # Export
    st.markdown('<div class="section-title">⬇️ Export Data</div>', unsafe_allow_html=True)
    st.download_button(
        label="📥  Export Filtered Data as CSV",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name=f"logistics_ops_{date_from}_to_{date_to}.csv",
        mime="text/csv",
    )
