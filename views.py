import csv

import numpy as np
import pandas as pd
import streamlit as st
from data_processing import process_data
from filters import get_filters_and_data, get_lead_feature_filters, lead_feature_filters
from streamlit_folium import folium_static
from plots import leads_by_location, property_type_breakdown, property_units_breakdown, leads_treemap, \
    residential_units_pie_chart, commercial_units_pie_chart, lead_count_pie_chart, property_condition_map, \
    conversion_channels_dist, features_table, leads_registration_overtime, geographic_listing_analytics, \
    leads_cluster_map, leads_features_heatmap, germany_feature_conditions_choropleth, lead_usage_distribution, \
    lead_parking_distribution, lead_htype_distribution, lead_feats_count_chart, lead_equipment_distribution, \
    house_condition_choropleth, house_equipment_choropleth, house_condition_table, house_equipment_table, \
    avg_feature_condition_table, lead_detail_table
from utils import get_lead_info, display_lead_metrics, \
    get_lead_location_info, format_date, save_data, lead_feats_metrics, drop_lead
from css.streamlit_ui import feature_html


def summary_view(data):
    df = get_filters_and_data(data)

    metrics = st.columns(6)
    metrics[0].metric(label="Total Leads", value=len(df))
    metrics[1].metric(label="Total Residential Units", value=round(df['Wohneinheiten'].sum()))
    metrics[2].metric(label="Total Commercial Units", value=round(df['Gewerbeeinheiten'].sum()))
    metrics[3].metric(label="Avg. Living Area (sq meters)", value=f"{df['Wohnflaeche'].mean():.2f}")
    metrics[4].metric(label="Avg. Lot Area (sq meters)", value=f"{df['Grundstueckflaeche'].mean():.2f}")
    metrics[5].metric(label="Avg. No. of Rooms", value=f"{round(df['Zimmeranzahl'].mean())}")

    row_2 = st.columns(3)
    row_2[0].plotly_chart(lead_count_pie_chart(df), use_container_width=True)
    row_2[1].plotly_chart(residential_units_pie_chart(df), use_container_width=True)
    row_2[2].plotly_chart(commercial_units_pie_chart(df), use_container_width=True)

    row_3 = st.columns((4, 3))
    row_3[0].plotly_chart(leads_treemap(df), use_container_width=True)
    row_3[1].plotly_chart(leads_by_location(df), use_container_width=True)

    st.write("---")
    st.subheader("Lead Features Analytics")

    df_2 = lead_feature_filters(df)

    feats_row_1 = st.columns((1,2,2,2))
    with feats_row_1[0]:
        st.write("##### ")
        lead_feats_metrics(df_2)
    feats_row_1[1].plotly_chart(lead_usage_distribution(df_2), use_container_width=True)
    feats_row_1[2].plotly_chart(lead_parking_distribution(df_2), use_container_width=True)
    feats_row_1[3].plotly_chart(lead_equipment_distribution(df_2), use_container_width=True)

    feats_row_2 = st.columns((4,3))
    feats_row_2[0].plotly_chart(lead_htype_distribution(df_2), use_container_width=True)
    feats_row_2[1].plotly_chart(lead_feats_count_chart(df_2), use_container_width=True)

    st.write("##### ")
    heatmap_cols = st.columns(6)
    with heatmap_cols[0]:
        st.write("##### ")
        st.write("##### Average Feature Usage")
    filter_by = heatmap_cols[1].selectbox(label="Analyze by", options=['State', 'City', 'Postal Code'])
    filter_map = {'State': 'bundesland', 'City': 'Ort', 'Postal Code': 'Postleitzahl_2'}
    filter_var = filter_map.get(filter_by)
    st.plotly_chart(leads_features_heatmap(df, filter_var), use_container_width=True)


def marketing_attribution_view(data):
    df = get_filters_and_data(data)

    metrics = st.columns(5)

    total_leads = len(df)
    metrics[0].metric(label="Total Leads", value=total_leads if total_leads else 0)

    total_residential_units = df['Wohneinheiten'].sum()
    metrics[1].metric(label="Total Residential Units", value=round(total_residential_units) if not np.isnan(total_residential_units) else 0)

    total_commercial_units = df['Gewerbeeinheiten'].sum()
    metrics[2].metric(label="Total Commercial Units", value=round(total_commercial_units) if not np.isnan(total_commercial_units) else 0)

    avg_living_area = df['Wohnflaeche'].mean()
    metrics[3].metric(label="Avg. Living Area (sq meters)", value=f"{avg_living_area:.2f}" if not np.isnan(avg_living_area) else "0.00")

    avg_lot_area = df['Grundstueckflaeche'].mean()
    metrics[4].metric(label="Avg. Lot Area (sq meters)", value=f"{avg_lot_area:.2f}" if not np.isnan(avg_lot_area) else "0.00")

    row_1 = st.columns((4,3))
    row_1[0].plotly_chart(leads_registration_overtime(df), use_container_width=True)
    row_1[1].plotly_chart(conversion_channels_dist(df), use_container_width=True)


def property_breakdown_view(data):
    df = get_filters_and_data(data)

    row_1 = st.columns(2)
    row_1[0].plotly_chart(property_type_breakdown(df), use_container_width=True)
    row_1[1].plotly_chart(property_units_breakdown(df), use_container_width=True)


def geographic_analytics_view(data):
    df = get_filters_and_data(data)

    row_1 = st.columns((3,5))
    row_1[0].plotly_chart(geographic_listing_analytics(df), use_container_width=True)

    with row_1[1]:
        folium_static(leads_cluster_map(df), height=500, width=1000)

    row_2 = st.columns(2)
    with row_2[0]:
        filter_by = st.columns(3)[0].selectbox(label="Search by", options=['State', 'City', 'Post Code'])
        if filter_by == 'State':
            row_2[0].plotly_chart(germany_feature_conditions_choropleth(df), use_container_width=True)
        else:
            row_2[0].plotly_chart(avg_feature_condition_table(df, col=filter_by), use_container_width=True)
    with row_2[1]:
        analyze = st.columns(3)[0].selectbox(label="Analyze", options=["House Condition", "House Equipment"])
        if filter_by == "State":
            if analyze == "House Condition":
                st.plotly_chart(house_condition_choropleth(df), use_container_width=True)
            else:
                st.plotly_chart(house_equipment_choropleth(df), use_container_width=True)
        else:
            if analyze == "House Condition":
                st.plotly_chart(house_condition_table(df, col=filter_by), use_container_width=True)
            else:
                st.plotly_chart(house_equipment_table(df, col=filter_by), use_container_width=True)



def display_lead_info(filtered_data):
    st.write("#### ")
    if not filtered_data.empty:
        filtered_data = filtered_data.sort_values(by=['Email', 'Id'])
        for lead_email in filtered_data['Email'].unique():
            temp_df = filtered_data[filtered_data['Email'] == lead_email]
            name, email, phone = get_lead_info(temp_df)
            st.columns(4)[0].info(f"""👤 {name}  
                                          📧 {email}  
                                          📞 {phone}""")
            for idx, row in temp_df.iterrows():
                display_property_info(row, idx)
                st.write("# ")
                # st.write("---")

            st.write("---")
            st.write("# ")
    else:
        st.write("No properties found for the selected lead.")


def display_property_info(row, idx):
    name_row = st.columns((2, 2, 1, 1))
    name_row[0].write(f"### Property Listing no. {idx}")
    name_row[1].success(get_lead_location_info(row))
    name_row[2].success(f"##### {row['Quelle']}", icon="🔗")
    name_row[3].success(f"##### {format_date(row['Created_at'])}", icon="📅")

    display_lead_metrics(row)

    main_info = st.columns(3)
    with main_info[0]:
        with st.expander("Nachricht 💬"):
            field_value = row['Nachricht']
            st.write(field_value if not pd.isnull(field_value) else "No Message")
    with main_info[2]:
        with st.expander("Defect Information 🚨"):
            field_value = row['Schaeden/Maengel']
            st.write(field_value if not pd.isnull(field_value) else "No Defect.")
    with main_info[1]:
        with st.expander("Informationen zu besonderen Rechten 📄"):
            field_value = row['Informationen zu besonderen Rechten']
            st.write(field_value if not pd.isnull(field_value) else "No Info")

    display_property_details(row)

def display_property_details(row):
    property_type = 'No Info' if pd.isnull(row['Objekttyp']) else row['Objekttyp']
    house_type = 'No Info' if pd.isnull(row['Haustyp']) else row['Haustyp']
    house_condition = 'No Info' if pd.isnull(row['Objektzustand']) else row['Objektzustand']
    house_equip = 'No Info' if pd.isnull(row['Ausstattung']) else row['Ausstattung']
    house_use = 'No Info' if pd.isnull(row['Aktuelle Nutzung']) else row['Aktuelle Nutzung']
    attachment_info = 'No Info' if pd.isnull(row['Anhaenge/Dateien']) else row['Anhaenge/Dateien']

    row_2 = st.columns((2, 2, 2))
    with row_2[0]:
        col1, col2 = st.columns(2)
        col1.markdown(feature_html.format("Property Type", "🏠", property_type), unsafe_allow_html=True)
        col1.markdown(feature_html.format("House Type", "🏘️", house_type), unsafe_allow_html=True)
        col1.markdown(feature_html.format("House Condition", "📄", house_condition), unsafe_allow_html=True)
        col2.markdown(feature_html.format("Equipment", "⚙️", house_equip), unsafe_allow_html=True)
        col2.markdown(feature_html.format("House Use", "🔑", house_use), unsafe_allow_html=True)
        col2.markdown(feature_html.format("Files Attached", "📁", attachment_info), unsafe_allow_html=True)

    row_2[1].plotly_chart(features_table(row), use_container_width=True)
    row_2[2].plotly_chart(property_condition_map(row), use_container_width=True)


def features_view(data):
    filtered_data = get_lead_feature_filters(data)
    display_lead_info(filtered_data)

def updatedata_view(data, conn):
    data_fields = st.session_state['fields']
    lead_data = data[data['Id'] == data['Id'].min()]

    row_1 = st.columns(3)
    uploaded_file = row_1[0].file_uploader("Choose a CSV or Excel file to load data from", type=["csv", "xlsx"])
    # ids_list = []
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):

            # Read the uploaded file
            try:
                # Try reading with the default delimiter (comma)
                lead_data = pd.read_csv(uploaded_file, delimiter=',')
                lead_data = lead_data.reset_index(drop=True)
            except pd.errors.ParserError:
                # If it fails, try reading with a semicolon delimiter
                uploaded_file.seek(0)  # Reset file pointer to the beginning
                try:
                    lead_data = pd.read_csv(uploaded_file, delimiter=';')
                    lead_data = lead_data.reset_index(drop=True)
                except pd.errors.ParserError:
                        # Optionally try other delimiters or handle the error
                        st.error("Error: Unable to read the CSV file with both ',' and ';' delimiters.")
        else:
            lead_data = pd.read_excel(uploaded_file)

        if all(col in lead_data.columns for col in data_fields):
            lead_data = lead_data[data_fields]
            lead_data = process_data(lead_data)
            ids_list = sorted(list(lead_data['Id'].unique()))
            inner_cols = row_1[1].columns((1, 2))
            inner_cols[0].write("##### ")
            if inner_cols[0].button("Add All Records"):
                updated_data = data.copy()
                lead_data = lead_data[data_fields]
                duplicate_ids = lead_data[lead_data['Id'].isin(updated_data['Id'])]['Id'].tolist()
                new_records = lead_data[~lead_data['Id'].isin(updated_data['Id'])]
                updated_data = pd.concat([updated_data, new_records], ignore_index=True)
                if duplicate_ids:
                    duplicate_message = f"Id(s) {', '.join(map(str, duplicate_ids))} already present, skipping them."
                    inner_cols[1].warning(duplicate_message)
                inner_cols[1].success("Lead Data updated successfully!")
                save_data(new_records, conn)
            data = pd.concat([data, lead_data], ignore_index=True)
        else:
            row_1[2].error("The provided data file does not contain sufficient information.")
            lead_data = data[data['Id'] == data['Id'].min()]
            ids_list = sorted(list(data['Id'].unique()))
    else:
        ids_list = sorted(list(data['Id'].unique()))

    row_2 = st.columns((1, 5))
    lead_id = row_2[0].selectbox(label="Lead Id", options=ids_list, index=ids_list.index(lead_data['Id'].iloc[0]))

    st.session_state['lead_data'] = data[data['Id'] == lead_id][data_fields]
    # Display form and lead data
    data_display = st.columns((3, 1))
    with data_display[0]:
        update_form(data, st.session_state['lead_data'], lead_id, conn)
    with data_display[1]:
        display_df = st.session_state['lead_data'].iloc[0].T
        # display_df.columns = ['Info']
        st.plotly_chart(lead_detail_table(display_df), use_container_width=True)
        # st.dataframe(display_df, use_container_width=True, height=650)


def update_form(data, lead_data, lead_id, conn):
    record = lead_data.iloc[0]
    with st.form(key='lead_form', border=False):
        title_cols = st.columns(4)
        id_input = title_cols[0].text_input(label='Id', value=f"{lead_id}", disabled=True)
        if pd.isnull(record['Created_at']):
            created_on = title_cols[1].date_input(label='Created on', value=None, disabled=True)
        else:
            created_on = title_cols[1].date_input(label='Created on', value=record['Created_at'], disabled=True)

        # Expander for Initials
        with st.expander("#### Initials"):
            initials = st.columns(4)
            initials[0].text_input("Email", value=record['Email'], disabled=True)
            initials[1].text_input("Vorname", value=record['Vorname'], disabled=True)
            initials[2].text_input("Nachname", value=record['Nachname'], disabled=True)
            telefon = initials[3].text_input("Telefon", value=record['Telefon'])

        # Expander for Property Address
        with st.expander("Property Address"):
            address_fields = st.columns(5)
            bundesland = address_fields[0].text_input("Bundesland", value=record['bundesland'])
            ort = address_fields[1].text_input("Ort", value=record['Ort'])
            postleitzahl = address_fields[2].text_input("Postleitzahl", value=record['Postleitzahl'])
            strasse = address_fields[3].text_input("Strasse", value=record['Strasse'])
            hausnummer = address_fields[4].text_input("Hausnummer", value=record['Hausnummer'])

        # Expander for Property Info
        with st.expander("Property Info"):
            prop_features_1 = st.columns(2)
            property_types = list(data['Objekttyp'].unique())
            house_types = list(data['Haustyp'].unique())
            ovr_conditions = list(data['Objektzustand'].unique())
            eqp_types = list(data['Ausstattung'].unique())
            use_opts = list(data['Aktuelle Nutzung'].unique())
            objekttyp = prop_features_1[0].selectbox("Objekttyp", options=property_types, index=property_types.index(record['Objekttyp']))
            haustyp = prop_features_1[1].selectbox("Haustyp", options=house_types, index=house_types.index(record['Haustyp']))
            prop_features_2 = st.columns(3)
            ovr_cond = prop_features_2[0].selectbox("Objektzustand", options=ovr_conditions, index=ovr_conditions.index(record['Objektzustand']))
            ausstattung = prop_features_2[1].selectbox("Ausstattung", options=eqp_types, index=eqp_types.index(record['Ausstattung']))
            nutzung = prop_features_2[2].selectbox("Aktuelle Nutzung", options=use_opts, index=use_opts.index(record['Aktuelle Nutzung']))

            st.write("### ")
            prop_info = st.columns(4)
            yr_built = prop_info[0].number_input("Baujahr", min_value=1658, max_value=2025, value=int(record['Baujahr']), step=1)
            wohnflaeche = prop_info[1].number_input("Wohnfläche", min_value=0.0, value=record['Wohnflaeche'], step=1.0, help="Total living area of the property (in square meters).")
            wohneinheiten = prop_info[2].number_input("Wohneinheiten", min_value=0, value=int(record['Wohneinheiten']), step=1, help="Number of residential units in the property.")
            geschaeftsflaeche = prop_info[3].number_input("Geschäftsfläche", min_value=0.0, value=record['Geschaeftsflaeche'], step=1.0, help="Area designated for commercial or business use (in square meters).")
            gewerbeeinheiten = prop_info[0].number_input("Gewerbeeinheiten", min_value=0, value=int(record['Gewerbeeinheiten']), step=1, help="Number of commercial units in the property.")
            grundstuecksflaeche = prop_info[1].number_input("Grundstücksfläche", min_value=0.0, value=record['Grundstueckflaeche'], step=1.0, help="Total land or lot area (in square meters).")
            zimmeranzahl = prop_info[2].number_input("Zimmeranzahl", min_value=0, value=int(record['Zimmeranzahl']), step=1, help="Number of rooms.")
            etagenanzahl = prop_info[3].number_input("Etagenanzahl", min_value=0.0, value=record['Etagenanzahl'], step=1.0, help="Number of floors.")

        # Expander for Property Address
        with st.expander("Property Features"):
            feats_avb = st.columns(6)
            avb_opts = ['Ja', 'Nein']

            bebaut = feats_avb[0].selectbox("Bebaut", options=avb_opts, index=avb_opts.index(record['Bebaut']))
            alleinlage = feats_avb[1].selectbox("Alleinlage", options=avb_opts, index=avb_opts.index(record['Alleinlage']))
            erschlossen = feats_avb[2].selectbox("Erschlossen", options=avb_opts, index=avb_opts.index(record['Erschlossen']))
            gastwc = feats_avb[3].selectbox("Gastwc", options=avb_opts, index=avb_opts.index(record['Gastwc']))
            vollvermietet = feats_avb[4].selectbox("Vollvermietet", options=avb_opts, index=avb_opts.index(record['Vollvermietet']))
            balkon = feats_avb[5].selectbox("Balkon", options=avb_opts, index=avb_opts.index(record['Balkon']))
            aufzug = feats_avb[0].selectbox("Aufzug", options=avb_opts, index=avb_opts.index(record['Aufzug']))
            dachgeschoss = feats_avb[1].selectbox("Dachgeschoss", options=avb_opts, index=avb_opts.index(record['Dachgeschoss']))
            keller = feats_avb[2].selectbox("Keller", options=avb_opts, index=avb_opts.index(record['Keller']))

        # Expander for Property Address
        with st.expander("Features Usage Info"):
            feats_usg = st.columns(4)
            usg_opts = ["0-5 Jahre", "5-10 Jahre", "10-15 Jahre", "mehr als 15 Jahre", "keine"]

            dach = feats_usg[0].selectbox("Dach", options=usg_opts, index=usg_opts.index(record['Dach']))
            fenster = feats_usg[1].selectbox("Fenster", options=usg_opts, index=usg_opts.index(record['Fenster']))
            leitungen = feats_usg[2].selectbox("Leitungen", options=usg_opts, index=usg_opts.index(record['Leitungen']))
            heizung = feats_usg[3].selectbox("Heizung", options=usg_opts, index=usg_opts.index(record['Heizung']))
            fassade = feats_usg[0].selectbox("Fassade", options=usg_opts, index=usg_opts.index(record['Fassade']))
            badezimmer = feats_usg[1].selectbox("Badezimmer", options=usg_opts, index=usg_opts.index(record['Badezimmer']))
            innenausbau = feats_usg[2].selectbox("Innenausbau", options=usg_opts, index=usg_opts.index(record['Innenausbau']))
            grundrissgestaltung = feats_usg[3].selectbox("Grundrissgestaltung", options=usg_opts, index=usg_opts.index(record['Grundrissgestaltung']))


        # Expander for Property Address
        with st.expander("Add-Ons"):
            addons = st.columns(4)
            avb_opts = ['Ja', 'Nein']
            sources = list(data['Quelle'].unique())
            parking_spaces = list(data['Parkplatz'].unique())

            verkaufsgarantie = addons[0].selectbox("100-Tage-Verkaufsgarantie", options=avb_opts, index=avb_opts.index(record['100-Tage-Verkaufsgarantie']))
            verkaufspreis = addons[1].selectbox("Verkaufspreis", options=avb_opts, index=avb_opts.index(record['Verkaufspreis']))
            wertanalyse = addons[2].selectbox("Wertanalyse", options=avb_opts, index=avb_opts.index(record['Wertanalyse']))
            verrentung = addons[3].selectbox("Verrentung", options=avb_opts, index=avb_opts.index(record['Verrentung']))

            quelle = addons[0].selectbox("Quelle", options=sources, index=sources.index(record['Quelle']))
            dateien = addons[1].number_input("Anhaenge/Dateien", min_value=0, value=int(record['Anhaenge/Dateien']))
            parkplatz = addons[2].selectbox("Parkplatz", options=parking_spaces, index=parking_spaces.index(record['Parkplatz']))
            kaltmiete = addons[3].text_input("Mieteinnahmen (Kaltmiete)", value=record['Mieteinnahmen (Kaltmiete)'])

        with st.expander("Descriptive Information"):
            cols = st.columns(2)
            immobilie_und_lage = cols[0].text_area(label='Immobilie und Lage', value=record['Immobilie und Lage'])
            objektinformationen = cols[1].text_area(label='Objektinformationen', value=record['Objektinformationen'])
            modernisierungen = cols[0].text_area(label='Modernisierungen', value=record['Modernisierungen'])
            maengel = cols[1].text_area(label='Schaeden/Maengel', value=record['Schaeden/Maengel'])
            rechten = cols[0].text_area(label='Informationen zu besonderen Rechten', value=record['Informationen zu besonderen Rechten'])
            st.write("##### ")
            nachricht = st.text_area(label='Nachricht', value=record['Nachricht'])

        btns_cols = st.columns(4)
        with btns_cols[0]:
            submit_button = st.form_submit_button(label='Update Lead')
        with btns_cols[1]:
            drop_button = st.form_submit_button(label='Drop Lead', type="secondary")

        updates = {
            'Telefon': telefon,
            'Nachricht': nachricht,
            '100-Tage-Verkaufsgarantie': verkaufsgarantie,
            'Verkaufspreis': verkaufspreis,
            'Wertanalyse': wertanalyse,
            'Verrentung': verrentung,
            'Quelle': quelle,
            'Anhaenge/Dateien': dateien,
            'Immobilie und Lage': immobilie_und_lage,
            'Objekttyp': objekttyp,
            'Strasse': strasse,
            'Postleitzahl': postleitzahl,
            'Ort': ort,
            'Hausnummer': hausnummer,
            'bundesland': bundesland,
            'Objektinformationen': objektinformationen,
            'Haustyp': haustyp,
            'Baujahr': yr_built,
            'Wohnflaeche': wohnflaeche,
            'Wohneinheiten': wohneinheiten,
            'Geschaeftsflaeche': geschaeftsflaeche,
            'Gewerbeeinheiten': gewerbeeinheiten,
            'Grundstueckflaeche': grundstuecksflaeche,
            'Bebaut': bebaut,
            'Alleinlage': alleinlage,
            'Erschlossen': erschlossen,
            'Zimmeranzahl': zimmeranzahl,
            'Etagenanzahl': etagenanzahl,
            'Objektzustand': ovr_cond,
            'Ausstattung': ausstattung,
            'Gastwc': gastwc,
            'Vollvermietet': vollvermietet,
            'Balkon': balkon,
            'Aufzug': aufzug,
            'Dachgeschoss': dachgeschoss,
            'Keller': keller,
            'Parkplatz': parkplatz,
            'Modernisierungen': modernisierungen,
            'Dach': dach,
            'Fenster': fenster,
            'Leitungen': leitungen,
            'Heizung': heizung,
            'Fassade': fassade,
            'Badezimmer': badezimmer,
            'Innenausbau': innenausbau,
            'Grundrissgestaltung': grundrissgestaltung,
            'Aktuelle Nutzung': nutzung,
            'Schaeden/Maengel': maengel,
            'Mieteinnahmen (Kaltmiete)': kaltmiete,
            'Informationen zu besonderen Rechten': rechten,
        }
        for col, value in updates.items():
            lead_data.loc[lead_data['Id'] == lead_id, col] = value
        st.session_state['lead_data'] = lead_data

        if submit_button:
            save_data(lead_data, conn)
            # lead_data.loc[lead_data['Id'] == lead_id, 'Id'] = id_input
            # lead_data.loc[lead_data['Id'] == lead_id, 'Created_at'] = created_on

        if drop_button:
            drop_lead(lead_data, conn)

    return lead_data