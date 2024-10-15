import streamlit as st

def get_filters_and_data(data):
    n_filters = 7
    filters = st.columns(n_filters)

    selected_states = filters[0].multiselect(
        label="State(s)",
        options=data['bundesland'].unique(),
        placeholder='All'
    )
    if not selected_states:
        selected_states = data['bundesland'].unique()

    selected_cities = filters[1].multiselect(
        label="Cities(s)",
        options=data['Ort'].unique(),
        placeholder='All'
    )
    if not selected_cities:
        selected_cities = data['Ort'].unique()

    selected_postalcodes = filters[2].multiselect(
        label="Postal Codes(s)",
        options=data['Postleitzahl_2'].unique(),
        placeholder='All'
    )
    if not selected_postalcodes:
        selected_postalcodes = data['Postleitzahl_2'].unique()

    selected_property_types = filters[3].multiselect(
        label="Property Type(s)",
        options=data['Objekttyp'].unique(),
        placeholder='All'
    )
    if not selected_property_types:
        selected_property_types = data['Objekttyp'].unique()

    sale_guarantee = filters[4].multiselect(
        label="100-Tage-Verkaufsgarantie",
        options=data['100-Tage-Verkaufsgarantie'].unique(),
        placeholder='All'
    )
    if not sale_guarantee:
        sale_guarantee = data['100-Tage-Verkaufsgarantie'].unique()

    # Year of Construction filter
    year_options = sorted(data['Baujahr'].dropna().unique())
    selected_years = filters[5].multiselect(
        label="Year of Construction",
        options=year_options,
        placeholder='All'
    )
    if not selected_years:
        selected_years = year_options

    # Property Area filter
    living_area_options = [
        'Up to 800 sqm',
        '800-1100 sqm',
        '1100-1300 sqm',
        '1300-1500 sqm',
        '1500-2000 sqm',
        '2000-3000 sqm',
        'Above 3000 sqm'
    ]
        # sorted(data['property_area_range'].unique())
    selected_living_area = filters[6].multiselect(
        label="Property Area",
        options=living_area_options,
        placeholder='All'
    )

    if not selected_living_area:
        selected_living_area = living_area_options

    # Filter based on multiselect selections
    filtered_data = data[
        (data['bundesland'].isin(selected_states)) &
        (data['Ort'].isin(selected_cities)) &
        (data['Postleitzahl_2'].isin(selected_postalcodes)) &
        (data['Objekttyp'].isin(selected_property_types)) &
        (data['100-Tage-Verkaufsgarantie'].isin(sale_guarantee)) &
        (data['Baujahr'].isin(selected_years)) &
        (data['property_area_range'].isin(selected_living_area))
        ]

    return filtered_data



def get_lead_feature_filters(data):
    filters_row = st.columns((1, 1, 1, 1, 2))

    selected_city = filters_row[0].selectbox("Select City", data['Ort'].unique())
    filtered_data = data[data['Ort'] == selected_city]

    selected_region = filters_row[1].selectbox("Select Postal Code", filtered_data['Postleitzahl_2'].unique())
    filtered_data = filtered_data[filtered_data['Postleitzahl_2'] == selected_region]

    selected_name = filters_row[2].multiselect("Select Name", filtered_data['Vorname'].unique(), placeholder='All')
    if not selected_name:
        selected_name = filtered_data['Vorname'].unique()

    selected_id = filters_row[3].multiselect("Select Id", sorted(filtered_data['Id'].unique()), placeholder='All')
    if not selected_id:
        selected_id = filtered_data['Id'].unique()

    selected_email = filters_row[4].multiselect("Select Email", filtered_data['Email'].unique(), placeholder='All')
    if not selected_email:
        selected_email = filtered_data['Email'].unique()

    return filtered_data[filtered_data['Vorname'].isin(selected_name) &
                         filtered_data['Id'].isin(selected_id) &
                         filtered_data['Email'].isin(selected_email)]



def lead_feature_filters(df):
    feats_filters = st.columns(6)

    # House Condition filter
    h_cond = feats_filters[0].multiselect(label="House Condition", options=df['Objektzustand'].unique(), placeholder="All")
    if not h_cond:
        h_cond = df['Objektzustand'].unique()

    # Equipment Types filter
    h_equip = feats_filters[1].multiselect(label="Equipment Types", options=df['Ausstattung'].unique(), placeholder="All")
    if not h_equip:
        h_equip = df['Ausstattung'].unique()

    # File Attached filter
    h_files = feats_filters[2].multiselect(label="File Attached", options=['Attached', 'Not Attached'], placeholder="All")
    if not h_files:
        h_files = ['Attached', 'Not Attached']

    # Nachricht filter
    h_msg = feats_filters[3].multiselect(label="Nachricht", options=['Provided', 'No Message'], placeholder="All")
    if not h_msg:
        h_msg = ['Provided', 'No Message']

    # Besonderen Rechten filter
    h_ap_rights = feats_filters[4].multiselect(label="Besonderen Rechten", options=['Provided', 'No Information'], placeholder="All")
    if not h_ap_rights:
        h_ap_rights = ['Provided', 'No Information']

    # Schaeden filter
    h_defects = feats_filters[5].multiselect(label="Schaeden", options=['Provided', 'No Information'], placeholder="All")
    if not h_defects:
        h_defects = ['Provided', 'No Information']

    # House condition and equipment type filters
    filtered_data = df[df['Objektzustand'].isin(h_cond) &
                       df['Ausstattung'].isin(h_equip)]

    # File attached filter: Handle the 'Anhaenge/Dateien' column
    if 'Attached' in h_files and 'Not Attached' not in h_files:
        filtered_data = filtered_data[filtered_data['Anhaenge/Dateien'] != 'No Information']
    elif 'Not Attached' in h_files and 'Attached' not in h_files:
        filtered_data = filtered_data[filtered_data['Anhaenge/Dateien'] == 'No Information']

    # Nachricht filter: Handle the 'Nachricht' column
    if 'Provided' in h_msg and 'No Message' not in h_msg:
        filtered_data = filtered_data[filtered_data['Nachricht'] != 'No Information']
    elif 'No Message' in h_msg and 'Provided' not in h_msg:
        filtered_data = filtered_data[filtered_data['Nachricht'] == 'No Information']

    # Besonderen Rechten filter: Handle the 'Informationen zu besonderen Rechten' column
    if 'Provided' in h_ap_rights and 'No Information' not in h_ap_rights:
        filtered_data = filtered_data[filtered_data['Informationen zu besonderen Rechten'] != 'No Information']
    elif 'No Information' in h_ap_rights and 'Provided' not in h_ap_rights:
        filtered_data = filtered_data[filtered_data['Informationen zu besonderen Rechten'] == 'No Information']

    # Schaeden filter: Handle the 'Schaeden/Maengel' column
    if 'Provided' in h_defects and 'No Information' not in h_defects:
        filtered_data = filtered_data[filtered_data['Schaeden/Maengel'] != 'No Information']
    elif 'No Information' in h_defects and 'Provided' not in h_defects:
        filtered_data = filtered_data[filtered_data['Schaeden/Maengel'] == 'No Information']

    return filtered_data
