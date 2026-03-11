import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

st.set_page_config(page_title="Logistics Operations Dashboard",page_icon="🚚",layout="wide")

CSV_PATH="operations_data.csv"

SELLERS=sorted([
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
"mona","klaw","kalbavi","rasna"
])

COURIERS=["DelhiveryOne","Ekart","Shiprocket"]
SR_COURIERS=["Ekart_SR","Delhivery_SR","Xpressbees_SR","DTDC_SR"]

UNDISPATCHED_REASONS=[
"Courier pickup did not happen",
"Pickup happened but shipments were handed over partially",
"Shipments were not ready at the seller",
"Courier Scanning issue"
]

PARTIAL_REASONS=[
"Vehicle space constraints",
"Seller handed over shipments partially"
]

PACKING_DELAY_REASONS=[
"Seller has not packed the orders",
"Manpower issue",
"Warehouse closed"
]

FAULT_TYPES=["Seller Fault","3PL Fault"]

COLUMNS=[
"date",
"seller",
"orders_pending_packing",
"orders_ready_dispatch",
"orders_packed",
"orders_picked_up",
"orders_not_packed_on_time",
"undispatched_reason",
"courier",
"sub_courier",
"partial_handover_reason",
"packing_delay_reason",
"fault_type",
"orders_impacted",
"backlog_previous_day"
]

def load_data():
if os.path.exists(CSV_PATH):
df=pd.read_csv(CSV_PATH)
df["date"]=pd.to_datetime(df["date"])
return df
return pd.DataFrame(columns=COLUMNS)

def save_row(row):
df_new=pd.DataFrame([row])
if os.path.exists(CSV_PATH):
df_new.to_csv(CSV_PATH,mode="a",header=False,index=False)
else:
df_new.to_csv(CSV_PATH,index=False)

st.title("🚚 Logistics Operations Control Tower")

tab1,tab2,tab3=st.tabs(["Daily Data Entry","Operations Dashboard","Previous Entries"])

# TAB 1

with tab1:

```
with st.form("entry_form"):

    col1,col2=st.columns(2)

    with col1:
        entry_date=st.date_input("Date",value=date.today())

    with col2:
        seller=st.selectbox("Seller",SELLERS)

    st.subheader("Order Flow")

    c1,c2,c3=st.columns(3)

    with c1:
        orders_pending_packing=st.number_input("Orders Pending for Packing",0,step=1)
        orders_ready_dispatch=st.number_input("Orders Ready for Dispatch",0,step=1)

    with c2:
        orders_packed=st.number_input("Orders Packed",0,step=1)
        orders_picked_up=st.number_input("Orders Picked Up",0,step=1)

    with c3:
        orders_not_packed_on_time=st.number_input("Orders Not Packed On Time",0,step=1)

    backlog_previous_day=st.number_input("Backlog from Previous Day",0,step=1)

    st.subheader("Undispatched Reason")

    undispatched_reason=st.selectbox("Reason",[""]+UNDISPATCHED_REASONS)

    courier=""
    sub_courier=""
    partial_handover_reason=""

    if undispatched_reason=="Courier pickup did not happen":
        courier=st.selectbox("Courier",COURIERS)
        if courier=="Shiprocket":
            sub_courier=st.selectbox("Shiprocket Sub Courier",SR_COURIERS)

    if undispatched_reason=="Pickup happened but shipments were handed over partially":
        partial_handover_reason=st.selectbox("Partial Handover Reason",PARTIAL_REASONS)

    st.subheader("Packing Delay")

    packing_delay_reason=""
    if orders_pending_packing>0:
        packing_delay_reason=st.selectbox("Packing Delay Reason",PACKING_DELAY_REASONS)

    st.subheader("Fault & Impact")

    fc1,fc2=st.columns(2)

    with fc1:
        fault_type=st.selectbox("Fault Type",FAULT_TYPES)

    with fc2:
        orders_impacted=st.number_input("Orders Impacted",0,step=1)

    submitted=st.form_submit_button("Submit Entry")

    if submitted:

        row={
        "date":str(entry_date),
        "seller":seller,
        "orders_pending_packing":orders_pending_packing,
        "orders_ready_dispatch":orders_ready_dispatch,
        "orders_packed":orders_packed,
        "orders_picked_up":orders_picked_up,
        "orders_not_packed_on_time":orders_not_packed_on_time,
        "undispatched_reason":undispatched_reason,
        "courier":courier,
        "sub_courier":sub_courier,
        "partial_handover_reason":partial_handover_reason,
        "packing_delay_reason":packing_delay_reason,
        "fault_type":fault_type,
        "orders_impacted":orders_impacted,
        "backlog_previous_day":backlog_previous_day
        }

        save_row(row)
        st.success("Entry Saved")
```

# TAB 2

with tab2:

```
df=load_data()

if df.empty:
    st.info("No data yet")
    st.stop()

total_pending=int(df["orders_pending_packing"].sum())
total_ready=int(df["orders_ready_dispatch"].sum())
total_packed=int(df["orders_packed"].sum())
total_pickup=int(df["orders_picked_up"].sum())
total_not_packed=int(df["orders_not_packed_on_time"].sum())
total_impacted=int(df["orders_impacted"].sum())

pickup_rate=(total_pickup/total_ready*100) if total_ready>0 else 0

c1,c2,c3,c4=st.columns(4)

c1.metric("Pending Packing",total_pending)
c2.metric("Ready for Dispatch",total_ready)
c3.metric("Packed",total_packed)
c4.metric("Picked Up",total_pickup)

c5,c6,c7=st.columns(3)

c5.metric("Not Packed On Time",total_not_packed)
c6.metric("Orders Impacted",total_impacted)
c7.metric("Pickup Success %",round(pickup_rate,1))

st.subheader("Seller Pending Packing")

seller_pending=df.groupby("seller")["orders_pending_packing"].sum().reset_index()

fig=px.bar(seller_pending,x="seller",y="orders_pending_packing")
st.plotly_chart(fig,use_container_width=True)
```

# TAB 3

with tab3:

```
df=load_data()

if df.empty:
    st.info("No entries")
    st.stop()

start_date=st.date_input("Start Date",value=df["date"].min().date())
end_date=st.date_input("End Date",value=df["date"].max().date())

seller_filter=st.selectbox("Seller",["All"]+SELLERS)

filtered=df[(df["date"].dt.date>=start_date)&(df["date"].dt.date<=end_date)]

if seller_filter!="All":
    filtered=filtered[filtered["seller"]==seller_filter]

st.dataframe(filtered,use_container_width=True)

selected_index=st.selectbox(
"Select Entry",
filtered.index,
format_func=lambda x:f"{df.loc[x,'date'].date()} | {df.loc[x,'seller']}"
)

col1,col2=st.columns(2)

with col1:
    if st.button("Delete Entry"):
        df=df.drop(selected_index)
        df.to_csv(CSV_PATH,index=False)
        st.success("Entry Deleted")
        st.rerun()

with col2:
    st.info("Edit by deleting and re-entering")
```
