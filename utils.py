import pandas as pd
import streamlit as st
from datetime import datetime


def format_fig_layout(fig):
    """
    Updates the layout of a Plotly figure

    Args:
        fig (Figure): The Plotly figure to update.

    Returns:
        Figure: The updated figure with updated layout.
    """
    fig = fig.update_layout(
        height=400,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_color="black",
                        font_size=12, font_family="Rockwell"),
        plot_bgcolor='rgba(255, 255, 255, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.8)',
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0)',  # Transparent legend background
        ),
        xaxis=dict(
            showgrid=False,  # Hide x-axis gridlines
            zeroline=False,  # Hide x-axis zero line
        ),
        yaxis=dict(
            showgrid=False,  # Hide y-axis gridlines
            zeroline=False,  # Hide y-axis zero line
        )
    )

    return fig


def get_lead_info(df):
    record = df.iloc[0]
    name = f"{record['Vorname']} {record['Nachname']}"
    email = record['Email']
    phone = record['Telefon']

    return name, email, phone


def display_lead_metrics(row):
    lot_area = round(row['Grundstueckflaeche']) if not pd.isna(row['Grundstueckflaeche']) else 0
    living_area = round(row['Wohnflaeche']) if not pd.isna(row['Wohnflaeche']) else 0
    business_area = round(row['Geschaeftsflaeche']) if not pd.isna(row['Geschaeftsflaeche']) else 0
    rental_income = row['Mieteinnahmen (Kaltmiete)'] if not pd.isna(row['Mieteinnahmen (Kaltmiete)']) else 0
    residential_units = row['Wohneinheiten'] if not pd.isna(row['Wohneinheiten']) else 0
    commercial_units = row['Gewerbeeinheiten'] if not pd.isna(row['Gewerbeeinheiten']) else 0
    num_floors = row['Etagenanzahl'] if not pd.isna(row['Etagenanzahl']) else 0
    num_rooms = row['Zimmeranzahl'] if not pd.isna(row['Zimmeranzahl']) else 0

    metrics_row = st.columns(9)
    metrics_row[0].metric(label="Year of Construction", value=round(row['Baujahr']))
    metrics_row[1].metric(label="Lot Area (sqm)", value=lot_area)
    metrics_row[2].metric(label="Living Area (sqm)", value=living_area)
    metrics_row[3].metric(label="Business Area (sqm)", value=business_area)
    metrics_row[4].metric(label="Rental Income", value=rental_income)
    metrics_row[5].metric(label="Residential Units", value=residential_units)
    metrics_row[6].metric(label="Commercial Units", value=commercial_units)
    metrics_row[7].metric(label="No. of Floors", value=num_floors)
    metrics_row[8].metric(label="No. of Rooms", value=num_rooms)


def display_plot_metrics(row):
    residential_units = row['Wohneinheiten'] if not pd.isna(row['Wohneinheiten']) else 0
    commercial_units = row['Gewerbeeinheiten'] if not pd.isna(row['Gewerbeeinheiten']) else 0
    num_floors = row['Etagenanzahl'] if not pd.isna(row['Etagenanzahl']) else 0
    num_rooms = row['Zimmeranzahl'] if not pd.isna(row['Zimmeranzahl']) else 0

    st.metric(label="Residential Units", value=residential_units)
    st.metric(label="Commercial Units", value=commercial_units)
    st.metric(label="Number of Floors", value=num_floors)
    st.metric(label="Number of Rooms", value=num_rooms)


def get_lead_location_info(row):
    """
    Generate a formatted address from the given row
    of data, including a clickable Google Maps link.
    """
    street = row['Strasse']
    postal_code = row['Postleitzahl']
    city = row['Ort']
    house_number = row['Hausnummer']
    state = row['bundesland']

    full_address = f"{street} {house_number}, {postal_code} {city}, {state}"
    google_maps_link = f"https://www.google.com/maps/search/?api=1&query={full_address.replace(' ', '+')}"

    formatted_address = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px;">
        <p> 📍 <a href="{google_maps_link}" target="_blank" style="text-decoration: none; color: blue;">{full_address}</a></p>
    </div>
    """
    formatted_address = f"📍 [{full_address}]({google_maps_link})\n"

    return formatted_address


def format_date(date_value):
    """
    Format the date from 'YYYY-MM-DD HH:MM:SS' to 'DDth Month, YYYY'
    """

    if pd.isnull(date_value) or date_value == '':
        return "Not Specified"

    if isinstance(date_value, pd.Timestamp):
        date_obj = date_value.to_pydatetime()  # Convert Timestamp to datetime
    else:
        date_obj = datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")

    day = date_obj.day
    suffix = 'th' if 4 <= day <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    formatted_day = f"{day}{suffix}"

    return f"{formatted_day} {date_obj.strftime('%b, %Y')}"


def save_data(new_data, conn):
    existing_data = conn.read(worksheet='leads')
    existing_df = pd.DataFrame(existing_data)

    new_data_df = pd.DataFrame(new_data)
    common_columns = existing_df.columns.intersection(new_data_df.columns)
    filtered_new_data = new_data_df[common_columns]

    for col in existing_df.columns:
        if col not in filtered_new_data.columns:
            filtered_new_data[col] = pd.NA
    combined_data = pd.concat([existing_df, filtered_new_data], ignore_index=True)
    combined_data.drop_duplicates(subset='Id', keep='last', inplace=True)

    conn.update(data=combined_data, worksheet='leads')
    st.success("Data Updated successfully!")
    st.cache_data.clear()

    # conn.update(data=df, worksheet='leads')
    # df.to_csv("data/df.csv", index=False)


def drop_lead(df, conn):
    if not isinstance(df, pd.DataFrame) or df.shape[0] < 1:
        st.error("The DataFrame must contain at least one lead.")
        return
    existing_data = conn.read(worksheet='leads')
    existing_df = pd.DataFrame(existing_data)

    if 'Id' not in df.columns:
        st.error("The provided leads must contain an 'Id' field.")
        return

    ids_to_drop = df['Id'].unique()
    ids_present = existing_df[existing_df['Id'].isin(ids_to_drop)]

    if ids_present.empty:
        st.error("The specified lead is not present in the existing data.")
    else:
        updated_df = existing_df[~existing_df['Id'].isin(ids_present['Id'])]
        conn.update(data=updated_df, worksheet='leads')
        st.success("Lead record deleted successfully!")
    st.cache_data.clear()


def lead_feats_metrics(df):
    num_floors = df['Etagenanzahl'].mean() if not pd.isna(df['Etagenanzahl'].mean()) else 0
    num_rooms = df['Zimmeranzahl'].mean() if not pd.isna(df['Zimmeranzahl'].mean()) else 0
    # rental_income = df['Mieteinnahmen (Kaltmiete)'].mean() if not pd.isna(df['Mieteinnahmen (Kaltmiete)'].mean()) else 0

    st.metric(label="Total Leads", value=len(df))
    st.metric(label="Avg. Floors", value=round(num_floors))
    st.metric(label="Avg. Rooms", value=round(num_rooms))
    # feats_metrics[2].metric(label="Rental Income", value=round(rental_income,2))


