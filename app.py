import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu as option_menu
from data_processing import process_data
from streamlit_gsheets import GSheetsConnection
from auth import authenticate_user, handle_authentication_status
from css.streamlit_ui import main_styles, inner_styles
from views import features_view, geographic_analytics_view, property_breakdown_view, marketing_attribution_view, \
    summary_view

from views import updatedata_view


pd.options.mode.chained_assignment = None

# -------------------------Page Config----------------------------------------
st.set_page_config(page_title="Leads Dashboard", layout="wide")

# -------------------------CSS Styling----------------------------------------
with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown(main_styles, unsafe_allow_html=True)

# ------------------------------- Data -----------------------------------------
# data = pd.read_csv("data/df.csv")
# users_df = pd.read_csv("data/users2.csv")

# ------------------------------- Data Loading ---------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    data = conn.read(worksheet='leads')
    users_df = conn.read(worksheet='users')
    return data, users_df

# Fetch data
data, users_df = load_data()

# Store in session-state
st.session_state['data'] = data
st.session_state['fields'] = list(data.columns)

# preprocess-data
data = process_data(data)

# ------------------------------- Authentication --------------------------------
# st.cache_data.clear()

authenticator, authentication_status, name, username = authenticate_user(users_df)
handle_authentication_status(authenticator, authentication_status, name)


role=None
# authentication_status = True
if authentication_status:
    st.markdown(inner_styles, unsafe_allow_html=True)
    # menu_options = ['Overview', 'Marketing Attribution', 'Property Breakdown',
    #                 'Geographic Analytics', 'Leads Features', 'Update Leads']
    role = users_df[users_df['Email'] == username]['Role'].values[0] if authentication_status else None
    if role == "Administrator/in":
        menu_options = ['Overview', 'Marketing Attribution', 'Property Breakdown',
                        'Geographic Analytics', 'Leads Features', 'Update Leads']
        menu_icons = ['bi bi-graph-up', 'bi bi-bar-chart', 'bi bi-house',
                      'bi bi-globe', 'bi bi-person-lines-fill', 'bi bi-arrow-clockwise']
    elif role == "Mitarbeiter/in":
        menu_options = ['Leads Features', 'Update Leads', 'Property Breakdown',
                        'Geographic Analytics']
        menu_icons = ['bi bi-person-lines-fill', 'bi bi-arrow-clockwise', 'bi bi-house','bi bi-globe']
    elif role == "Trackingpartner":
        menu_options = ['Leads Features', 'Property Breakdown', 'Geographic Analytics']
        menu_icons = ['bi bi-person-lines-fill', 'bi bi-house', 'bi bi-globe']
    else:
        menu_options = ['Login Required']
        menu_icons = ['bi bi-graph-up']

    menu = option_menu(menu_title=None, orientation="horizontal", menu_icon=None,
                       icons = menu_icons,
                       options=menu_options)

    if menu == "Overview":
        summary_view(data)

    if menu == "Marketing Attribution":
        marketing_attribution_view(data)

    if menu == "Property Breakdown":
        property_breakdown_view(data)

    if menu == "Geographic Analytics":
        geographic_analytics_view(data)

    if menu == "Leads Features":
        features_view(data)

    if menu == "Update Leads":
        updatedata_view(data, conn)

