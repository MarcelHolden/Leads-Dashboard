import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import plotly.express as px
import folium
from folium.plugins import MarkerCluster

from utils import format_fig_layout
import streamlit as st

colors = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#84a59d", "#006d77",
          "#f6bd60", "#90be6d", "#577590", "#e07a5f", "#81b29a", "#f2cc8f", "#0081a7"]

g_colors = {
    'Ja': "#0E9594",
    'Nein': "#127475",
    'Other': "#F5DFBB"
}

def leads_by_location(data):
    data['Postcode (first 2 digits)'] = data['Postleitzahl'].astype(str).str[:2]
    leads_by_postcode = data.groupby(['bundesland','Ort', 'Postcode (first 2 digits)'])['Id'].count().reset_index()
    leads_by_postcode.columns = ['State', 'City', 'Postcode', 'Number of Leads']
    leads_by_postcode = leads_by_postcode.sort_values(by='State')
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(leads_by_postcode.columns),
            font=dict(size=14, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['center'],
            height=50
        ),
        cells=dict(
            values=[leads_by_postcode[K].tolist() for K in leads_by_postcode.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            align=['center'],
            height=30
        ))]
    )
    fig = format_fig_layout(fig)

    fig.update_layout(
        title="Leads by Location",
        margin=dict(t=50, l=0, r=0, b=0),
        height=500
    )

    return fig


def property_type_breakdown(data):
    type_data = data.groupby(['Objekttyp', 'Haustyp'], observed=False)['Id'].count().reset_index()
    pivot_data = type_data.pivot(index='Objekttyp', columns='Haustyp', values='Id').fillna(0)
    wrapped_labels = [label.replace(' ', '<br>') if len(label) > 10 else label for label in pivot_data.index]  # Example wrapping logic

    if len(pivot_data) == 1 and pivot_data.sum(axis=1).iloc[0] > 0:
        single_category = pivot_data.index[0]
        total_leads = pivot_data.sum(axis=1).iloc[0]
        fig = show_indicator(total_leads, single_category, "Property Type Breakdown with House Types")
        fig.update_layout(height=500)
        return fig

    elif len(pivot_data) == 1 and pivot_data.sum(axis=1).iloc[0] == 0:
        single_category = pivot_data.index[0]
        fig = show_indicator(0, "No Units", "Property Type Breakdown with House Types")
        fig.update_layout(height=500)
        return fig

    elif len(pivot_data) == 0:
        fig = show_indicator(0, "No Units", "Property Type Breakdown with House Types")
        fig.update_layout(height=500)
        return fig


    fig = go.Figure()
    for i, house_type in enumerate(pivot_data.columns):
        fig.add_trace(go.Bar(
            x=pivot_data.index,
            y=pivot_data[house_type],
            name=house_type,
            marker_color=colors[i],
            orientation='v'
        ))

    fig = format_fig_layout(fig)
    fig.update_layout(
        title="Property Type Breakdown with House Types",
        yaxis_title="Property Type (Objekttyp)",
        xaxis_title="Number of Leads",
        barmode='stack',
        # legend_title="House Type (Haustyp)",
        legend=dict(orientation="h", xanchor='center', x=0.35, y=-0.25),
        height=500,
        yaxis=dict(
            ticktext=wrapped_labels,  # Use wrapped labels
            tickvals=pivot_data.index  # Ensure tickvals match index
        ),
        # hovermode='y unified'
    )

    return fig


def property_units_breakdown(data):
    units_data = data.groupby('Objekttyp').agg({
        'Wohneinheiten': 'sum',
        'Gewerbeeinheiten': 'sum',
        'Id': 'count'
    }).reset_index()

    units_data['Total'] = units_data['Wohneinheiten'] + units_data['Gewerbeeinheiten'] + units_data['Id']
    units_data = units_data.sort_values(by='Total', ascending=True)

    units_data['Wohneinheiten'] = units_data['Wohneinheiten'].fillna(0)
    units_data['Gewerbeeinheiten'] = units_data['Gewerbeeinheiten'].fillna(0)

    if len(units_data)==1 and (units_data.iloc[0]['Id'] == units_data.iloc[0]['Total']):
        single_category = units_data['Objekttyp'].iloc[0]
        single_count = units_data['Total'].iloc[0]
        fig = show_indicator(single_count, single_category,"Total Residential and Commercial Units by Property Type")
        fig.update_layout(height=500)
        return fig
    elif len(units_data)==1 and (units_data.iloc[0]['Id'] != units_data.iloc[0]['Total']):
        pie_data = units_data.iloc[0]
        labels = ['Residential Units', 'Commercial Units']
        values = [pie_data['Wohneinheiten'], pie_data['Gewerbeeinheiten']]

        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            textinfo='percent',
            hoverinfo='label+value',
            marker=dict(colors=[colors[1], colors[5]]),
            hole=0.6,
            hovertemplate='<b>%{label}</b><br>Total Units= %{value} (%{percent})<extra></extra>'
        ))
        fig.update_layout(
            title=f"{pie_data['Objekttyp']} - Residential vs Commercial Units",
            height=500,
            margin=dict(t=50, l=0, r=0, b=0),
            legend=dict(orientation="h", xanchor='center', x=0.5, y=-0.25),

        )
        return fig

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=units_data['Objekttyp'],
        x=units_data['Id'],
        name='Total Leads',
        marker_color=colors[0],
        orientation='h'
    ))

    fig.add_trace(go.Bar(
        y=units_data['Objekttyp'],
        x=units_data['Wohneinheiten'],
        name='Residential Units (Wohneinheiten)',
        marker_color=colors[1],
        orientation='h'
    ))

    fig.add_trace(go.Bar(
        y=units_data['Objekttyp'],
        x=units_data['Gewerbeeinheiten'],
        name='Commercial Units (Gewerbeeinheiten)',
        marker_color=colors[5],
        orientation='h'
    ))
    fig = format_fig_layout(fig)
    fig.update_layout(
        title="Total Residential and Commercial Units by Property Type",
        yaxis_title="Property Type (Objekttyp)",
        xaxis_title="Total Units",
        barmode='stack',
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.25),
        hovermode='y unified',
        height=500
    )

    return fig


def leads_treemap(data):
    bundesland_data = data.groupby('bundesland').agg(
        Total_Leads=('Id', 'count'),                  # Count of leads (Id)
        Total_Cities=('Ort', 'nunique'),              # Count of unique cities (Ort)
        Total_Lot_Area=('Grundstueckflaeche', 'sum')  # Sum of lot area
    ).reset_index()

    # Check if there is only one state
    if len(bundesland_data) == 1:
        # Create a go.Indicator if there is only one state
        fig = go.Figure(go.Indicator(
            mode="number",
            value=bundesland_data['Total_Leads'].iloc[0],
            title={"text": f"Total Leads in {bundesland_data['bundesland'].iloc[0]}"},
            number={'valueformat': ','}  # Format for thousands separator
        ))
        fig.update_layout(
            title="Lead Count for Single State",
            margin=dict(t=50, l=0, r=0, b=0),
            height=500,
            plot_bgcolor='rgba(173, 216, 230, 0.8)',
            paper_bgcolor='rgba(173, 216, 230, 0.8)',
        )
    else:
        # Otherwise, create the treemap as usual
        fig = go.Figure(go.Treemap(
            labels=bundesland_data['bundesland'],
            parents=[''] * len(bundesland_data),
            values=bundesland_data['Total_Leads'],
            textinfo='label+value+percent entry',
            hoverinfo='label+value+percent entry',
            marker=dict(colors=colors),
            customdata=bundesland_data[['bundesland', 'Total_Cities', 'Total_Leads', 'Total_Lot_Area']],  # Additional data for hover
            hovertemplate='<b>%{customdata[0]}</b><br><br>' +
                          'Total Cities: %{customdata[1]}<br>' +
                          'Total Leads Registered: %{customdata[2]}<br>' +
                          'Total Lot Area: %{customdata[3]:.2f} sqm<extra></extra>'
        ))
        fig = format_fig_layout(fig)

        fig.update_layout(
            title="Total Leads by State",
            margin=dict(t=50, l=0, r=0, b=0),
            height=500
        )

    return fig


def leads_features_heatmap(df, col):
    features = ['Dach', 'Fenster', 'Leitungen', 'Heizung', 'Fassade', 'Badezimmer', 'Innenausbau', 'Grundrissgestaltung']
    df = df[[col] + features]
    df = df.fillna('keine')

    years_mapping = {
        "0-5 Jahre": 0,
        "5-10 Jahre": 5,
        "10-15 Jahre": 10,
        "mehr als 15 Jahre": 15,
        "keine": None
    }

    def inverse_map(avg_cond):
        if 0 <= avg_cond < 5:
            return "0-5 Jahre"
        elif 5 <= avg_cond < 10:
            return "5-10 Jahre"
        if 10 <= avg_cond < 15:
            return "10-15 Jahre"
        elif avg_cond >=15:
            return "mehr als 15 Jahre"
        else:
            return "keine"

    for feature in features:
        df[feature] = df[feature].map(years_mapping)

    heatmap_data = df.groupby(col).mean().reset_index()
    transposed_data = heatmap_data.set_index(col).T

    fig = go.Figure(data=go.Heatmap(
        z=transposed_data.values,
        x=heatmap_data[col],
        y=transposed_data.index,
        hovertemplate='<b>%{x}</b><br>Feature: %{y} <br>Avg. Usage: %{z} years<extra></extra>',
        customdata=[[inverse_map(val) for val in row][::-1] for row in transposed_data.values],
        colorscale=[
            [0.0, '#d9ed92'],  # Corresponds to '0-5 Jahre'
            [0.25, '#99d98c'],  # Corresponds to '5-10 Jahre'
            [0.5, '#52b69a'],  # Corresponds to '10-15 Jahre'
            [0.75, '#168aad'],  # Corresponds to 'mehr als 15 Jahre'
            [1.0, '#184e77'],  # Corresponds to None (keine)
        ],
        colorbar=dict(
            tickvals=[0, 5, 10, 15],
            ticktext=["0-5 Jahre", "5-10 Jahre", "10-15 Jahre", "mehr als 15 Jahre"],
            title="Feature Age"
        ),
    ))

    fig = format_fig_layout(fig)

    fig.update_layout(
        title=f'Average Feature Values by {col}',
        xaxis_title=col,
        yaxis_title="Features",
        xaxis=dict(tickmode='array', tickvals=heatmap_data[col], showgrid=False),
        yaxis=dict(tickmode='array', tickvals=transposed_data.index, showgrid=False),
        height=500
    )

    return fig


def lead_count_pie_chart(data):
    lead_data = data['Objekttyp'].value_counts().reset_index()
    lead_data.columns = ['Objekttyp', 'Lead Count']

    non_zero_units = lead_data[lead_data['Lead Count']>0]

    if len(lead_data) == 0 or lead_data['Lead Count'].sum()==0:
        return show_indicator(0, "No units","Property Type Distribution")
    elif len(lead_data) == 1 or len(non_zero_units)==1:
        single_category = lead_data['Objekttyp'].iloc[0]
        single_count = lead_data['Lead Count'].iloc[0]
        return show_indicator(single_count, single_category,"Property Type Distribution")

    fig = go.Figure(go.Pie(
        labels=lead_data['Objekttyp'],
        values=lead_data['Lead Count'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Property Type",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Property Type Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )

    fig = format_fig_layout(fig)

    return fig


def residential_units_pie_chart(data):
    residential_data = data.groupby('Objekttyp')['Wohneinheiten'].sum().reset_index()
    residential_data = residential_data.sort_values(by='Wohneinheiten', ascending=False)

    non_zero_units = residential_data[residential_data['Wohneinheiten']>0]
    if len(residential_data) == 0 or residential_data['Wohneinheiten'].sum()==0:
        return show_indicator(0, "No units", "Residential Units Distribution")
    elif len(residential_data) == 1 or len(non_zero_units)==1:
        single_category = residential_data['Objekttyp'].iloc[0]
        single_count = residential_data['Wohneinheiten'].iloc[0]
        return show_indicator(single_count, single_category, "Residential Units Distribution")

    fig = go.Figure(go.Pie(
        labels=residential_data['Objekttyp'],
        values=residential_data['Wohneinheiten'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Residential Units",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Residential Units Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig = format_fig_layout(fig)

    return fig


def commercial_units_pie_chart(data):
    commercial_data = data.groupby('Objekttyp')['Gewerbeeinheiten'].sum().reset_index()
    commercial_data = commercial_data.sort_values(by='Gewerbeeinheiten', ascending=False)

    non_zero_units = commercial_data[commercial_data['Gewerbeeinheiten']>0]
    if len(commercial_data) == 0 or commercial_data['Gewerbeeinheiten'].sum()==0:
        return show_indicator(0, "No units", "Commercial Units Distribution")
    # elif len(commercial_data) == 1 or len(non_zero_units)==1:
    #     single_category = commercial_data['Objekttyp'].iloc[0]
    #     single_count = commercial_data['Gewerbeeinheiten'].iloc[0]
    #     return show_indicator(single_count, single_category, "Commercial Units Distribution")

    fig = go.Figure(go.Pie(
        labels=commercial_data['Objekttyp'],
        values=commercial_data['Gewerbeeinheiten'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Commercial Units",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Commercial Units Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig = format_fig_layout(fig)

    return fig


def show_indicator(value, label, title):
    fig = go.Figure(go.Indicator(
        mode="number",
        value=value,
        title={'text': label},
    ))
    fig = format_fig_layout(fig)
    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0),
                      plot_bgcolor='rgba(173, 216, 230, 0.6)',
                      paper_bgcolor='rgba(173, 216, 230, 0.6)',
                      title=title)

    return fig


def conversion_channels_dist(data):
    channel_counts = data['Quelle'].value_counts()

    fig = go.Figure(data=go.Pie(
        labels=channel_counts.index,
        values=channel_counts.values,
        textinfo='percent',
        hoverinfo='label+value',
        marker=dict(colors=colors[1:]),
        hovertemplate='<b>%{label}</b> <br>Total Conversions= %{value} (%{percent})<extra></extra>',
    ))

    fig = format_fig_layout(fig)
    fig.update_layout(
        title='Conversion Channels Distribution',
        legend=dict(orientation="h", xanchor='center', x=0.45, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
        height=350
    )

    return fig


def features_map(row):
    features = ['Gastwc', 'Vollvermietet', 'Balkon', 'Aufzug', 'Dachgeschoss', 'Keller',  'Bebaut', 'Alleinlage', 'Erschlossen']

    feature_values = {feature: row[feature] for feature in features}
    df = pd.DataFrame(list(feature_values.items()), columns=['Feature', 'Presence'])
    df['Presence'] = df['Presence'].fillna('Nein')
    df['Value'] = df['Presence'].map({'Ja': 1, 'Nein': -1})

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Feature'],
        y=df['Value'],
        marker=dict(color=df['Value'].map({1: "#588157", -1: "#e63946"})),
        text=df['Presence'],
        textposition='auto',
    ))

    fig.update_layout(
        title='Property Features',
        xaxis_title='Features',
        yaxis_title='',
        yaxis=dict(
            range=[-1, 1],
            tickvals=[1, -1],
            ticktext=['Ja', 'Nein'],
        ),
        showlegend=False,
    )

    return fig


def features_table(row):
    features = ["100-Tage-Verkaufsgarantie", "Verkaufspreis", "Wertanalyse",
                "Verrentung", "Bebaut", "Alleinlage", "Erschlossen", 'Gastwc',
                'Vollvermietet', 'Balkon', 'Aufzug', 'Dachgeschoss', 'Keller']

    feature_values = {feature: row[feature] for feature in features}
    df = pd.DataFrame(list(feature_values.items()), columns=['Feature', 'Presence'])

    df['Presence'] = df['Presence'].fillna('Nein')
    df['Presence'] = df['Presence'].map({'Ja': '✔️', 'Nein': '❌'})
    colors = df['Presence'].map({'✔️': '#a3b18a', '❌': '#fed9b7'})

    fig = go.Figure(data=[go.Table(
        header=dict(values=['Feature', 'Availability'],
                    fill_color='#264653',
                    font=dict(size=14, color='white', family='ubuntu'),
                    height=50,
                    align='left'),
        cells=dict(values=[df['Feature'], df['Presence']],
                   fill_color=[['white'] * len(df), colors],
                   font=dict(size=14, color='black', family='ubuntu'),
                   height=40,
                   align='left'))
    ])

    fig.update_layout(title='',
                      margin=dict(t=25, l=0, r=0, b=0),
                      height=600)

    return fig



def property_condition_map(row):
    features = ['Dach', 'Fenster', 'Leitungen', 'Heizung', 'Fassade', 'Badezimmer', 'Innenausbau', 'Grundrissgestaltung']
    feature_values = {feature: row[feature] for feature in features}

    for feature in features:
        if pd.isna(feature_values[feature]):
            feature_values[feature] = "keine"

    condition_mapping = {
        "0-5 Jahre": 1,
        "5-10 Jahre": 2,
        "10-15 Jahre": 3,
        "mehr als 15 Jahre": 4,
        "keine": 0
    }

    inverse_condition_mapping = {v: k for k, v in condition_mapping.items()}

    heatmap_values = [[condition_mapping[feature_values[feature]] for feature in features]]

    # Transposing the heatmap values to make the heatmap vertical
    heatmap_values = list(map(list, zip(*heatmap_values)))

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_values,
        x=['Property'],
        y=features,
        colorscale=[
            [0, '#d9ed92'],     # keine
            [0.125, '#b5e48c'], # slight variation
            [0.25, '#99d98c'],  # '0-5 Jahre'
            [0.375, '#76c893'], # slight variation
            [0.5, '#52b69a'],   # '5-10 Jahre'
            [0.625, '#34a0a4'], # slight variation
            [0.75, '#168aad'],  # '10-15 Jahre'
            [0.875, '#1a759f'], # slight variation
            [1, '#1a759f']      # 'mehr als 15 Jahre'
        ],
        colorbar=dict(
            title='Condition',
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['keine', '0-5 Jahre', '5-10 Jahre', '10-15 Jahre', 'mehr als 15 Jahre'],
            orientation='h',  # Horizontal color bar
            yanchor='bottom',
            y=-0.3  # Adjust position
        ),
        showscale=False,
        hoverongaps=False,
        hovertemplate='<b>%{y}</b> <br>%{customdata}<extra></extra>',
        customdata=[[inverse_condition_mapping[val] for val in row] for row in heatmap_values],
        text=[[inverse_condition_mapping[val] for val in row] for row in heatmap_values],  # Add text to boxes
        texttemplate="%{text}",  # Display custom text inside each box
        textfont=dict(color="black", size=14),
    ))

    fig.update_layout(
        title='Property Condition',
        xaxis_title='',
        yaxis_title='Features',
        yaxis=dict(showgrid=False, zeroline=False, showline=False),
        xaxis=dict(showgrid=False, zeroline=False, showline=False),
        height=600
    )

    # Add white borders to the boxes
    for i in range(len(features)):
        fig.add_shape(
            type='rect',
            x0=-0.5, x1=0.5,
            y0=i - 0.5, y1=i + 0.5,
            line=dict(color='white', width=1)
        )

    return fig


def leads_registration_overtime(data):
    data['Mon-Year'] = data['Created_at'].dt.strftime('%b-%Y')
    data = data.groupby('Mon-Year', observed=False)['Id'].count().reset_index()
    data = data.rename(columns={'Id': 'leads_count'})
    data['Mon-Year'] = pd.to_datetime(data['Mon-Year'], format='%b-%Y')

    data = data.sort_values(by='Mon-Year')
    data['Mon-Year'] = data['Mon-Year'].dt.strftime('%b-%Y')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Mon-Year'],
        y=data['leads_count'],
        mode='lines+markers+text',
        text=data['leads_count'],
        textposition='top center',
        fill='tozeroy',
        fillcolor="#9CC1C1",
        line=dict(color='#094780', width=4),
        marker=dict(color='#094780', size=12),
        hovertemplate='Registered Leads= %{text}<extra></extra>',
    ))

    fig = format_fig_layout(fig)
    fig.update_layout(
        height=350,
        title="Leads Trend",
        xaxis_title="Time",
        yaxis_title="Leads Count",
        yaxis_range=[0, data['leads_count'].max() + 10],
    )

    return fig


@st.cache_data
def geographic_listing_analytics(df):
    listing_data = df.groupby('bundesland').agg(
        total_ids=('Id', 'count'),
        total_lot_area=('Grundstueckflaeche', 'sum')
    ).reset_index()

    listing_data = listing_data.rename({'total_ids': 'Registered Leads', 'total_lot_area': 'Net Lot Area'}, axis=1)

    url = 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json'
    geojson = requests.get(url).json()

    fig = px.choropleth_mapbox(
        listing_data,
        geojson=geojson,
        locations='bundesland',
        featureidkey="properties.name",
        color='Registered Leads',
        hover_name='bundesland',
        hover_data=['Registered Leads', 'Net Lot Area'],
        color_continuous_scale='Viridis',
        title='Number of Listed Properties by Bundesland',
        mapbox_style='carto-positron',
        center={"lat": 51.1657, "lon": 10.4515},
        zoom=4.5,
        opacity=0.8,
        height=500
    )

    fig.update_geos(fitbounds="locations",
                    visible=True,
                    projection_scale=10.5,
                    center={"lat": 51.1657, "lon": 10.4515})
    fig = format_fig_layout(fig)

    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=500,
                      coloraxis_colorbar={
                          'orientation': 'h',
                          'xanchor': 'center',
                          'x': 0.5,
                          'yanchor': 'bottom',
                          'y': -0.2
                      },)

    return fig


@st.cache_data
def leads_cluster_map(df):
    geojson_url = 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json'
    geojson = requests.get(geojson_url).json()

    folium_map = folium.Map(location=[51.1657, 10.4515], zoom_start=6, width='100%', height='100%')
    marker_cluster = MarkerCluster().add_to(folium_map)

    for _, row in df.iterrows():
        for feature in geojson['features']:
            if feature['properties']['name'] == row['bundesland']:
                geometry_type = feature['geometry']['type']
                coords = feature['geometry']['coordinates']

                if geometry_type == 'MultiPolygon':
                    lon, lat = coords[0][0][0]  # [lon, lat] format
                elif geometry_type == 'Polygon':
                    lon, lat = coords[0][0]  # [lon, lat] format

                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(
                        f"<b>Lead ID:</b> {row['Id']}<br>"
                        f"<b>Property Area:</b> {round(row['Grundstueckflaeche'],2)} sqm<br>"
                        f"<b>Owner Name:</b> {row['Vorname']} {row['Nachname']}",
                        max_width=300
                    ),
                    tooltip=row['Ort']
                ).add_to(marker_cluster)
                break

    return folium_map


@st.cache_data
def germany_feature_conditions_choropleth(df):
    features = ['Dach', 'Fenster', 'Leitungen', 'Heizung', 'Fassade', 'Badezimmer', 'Innenausbau', 'Grundrissgestaltung']
    df = df[['bundesland'] + features]
    df = df.fillna('keine')

    years_mapping = {
        "0-5 Jahre": 0,
        "5-10 Jahre": 5,
        "10-15 Jahre": 10,
        "mehr als 15 Jahre": 15,
        "keine": None
    }
    def inverse_map(avg_cond):
        if 0 <= avg_cond < 5:
            return "0-5 Jahre"
        elif 5 <= avg_cond < 10:
            return "5-10 Jahre"
        if 10 <= avg_cond < 15:
            return "10-15 Jahre"
        elif avg_cond >= 15:
            return "mehr als 15 Jahre"
        else:
            return "keine"

    for feature in features:
        df[feature] = df[feature].map(years_mapping)

    avg_feature_data = df.groupby('bundesland').mean().reset_index()
    avg_feature_data['Avg_Condition'] = avg_feature_data[features].mean(axis=1)
    avg_feature_data['Condition_Category'] = avg_feature_data['Avg_Condition'].apply(inverse_map)

    url = 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json'
    geojson = requests.get(url).json()

    fig = px.choropleth_mapbox(
        avg_feature_data,
        geojson=geojson,
        locations='bundesland',
        featureidkey="properties.name",
        color='Avg_Condition',
        hover_name='bundesland',
        hover_data={
            'Condition_Category': True,
            'Avg_Condition': False
        },
        title='Average Feature Condition by Bundesland',
        color_continuous_scale=[
            [0.0, '#d9ed92'],  # Corresponds to '0-5 Jahre'
            [0.25, '#99d98c'],  # Corresponds to '5-10 Jahre'
            [0.5, '#52b69a'],  # Corresponds to '10-15 Jahre'
            [0.75, '#168aad'],  # Corresponds to 'mehr als 15 Jahre'
            [1.0, '#184e77'],  # Corresponds to None (keine)
        ],
        mapbox_style="carto-positron",  # Choose mapbox style ("carto-positron", "open-street-map", "satellite-streets")
        center={"lat": 51.1657, "lon": 10.4515},
        zoom=5,
        opacity=0.8
    )

    fig = format_fig_layout(fig)
    fig.update_layout(
        mapbox=dict(bearing=-10),
        coloraxis_colorbar=dict(
            title="Avg. Feature Condition",
            tickvals=[0, 5, 10, 15],
            ticktext=["0-5 Jahre", "5-10 Jahre", "10-15 Jahre", "mehr als 15 Jahre"],
            orientation='h',
            xanchor='center',
            x=0.5,
            yanchor='bottom',
            y=-0.2
        ),
        height=800,
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
    )
    fig.update_geos(fitbounds="locations", visible=True)

    return fig


@st.cache_data
def avg_feature_condition_table(df, col='City'):
    features = ['Dach', 'Fenster', 'Leitungen', 'Heizung', 'Fassade', 'Badezimmer', 'Innenausbau', 'Grundrissgestaltung']
    main_col = 'Ort' if col == 'City' else 'Postleitzahl_2'

    df = df[[main_col] + features]
    df = df.fillna('keine')

    # Map years to numeric values for computing averages
    years_mapping = {
        "0-5 Jahre": 0,
        "5-10 Jahre": 5,
        "10-15 Jahre": 10,
        "mehr als 15 Jahre": 15,
        "keine": None
    }

    # Helper function to reverse map the averages back to textual descriptions
    def inverse_map(avg_cond):
        if 0 <= avg_cond < 5:
            return "0-5 Jahre"
        elif 5 <= avg_cond < 10:
            return "5-10 Jahre"
        if 10 <= avg_cond < 15:
            return "10-15 Jahre"
        elif avg_cond >= 15:
            return "mehr als 15 Jahre"
        else:
            return "keine"

    # Apply the mapping to each feature
    for feature in features:
        df[feature] = df[feature].map(years_mapping)

    # Calculate the average condition for each feature by the specified column (Ort or Postleitzahl_2)
    avg_feature_data = df.groupby(main_col).mean().reset_index()

    # Compute overall average condition
    avg_feature_data['Avg_Condition'] = avg_feature_data[features].mean(axis=1)

    # Map the average condition back to textual categories
    avg_feature_data['Condition_Category'] = avg_feature_data['Avg_Condition'].apply(inverse_map)

    # Color mapping based on condition categories
    def color_mapping(x):
        if x == "0-5 Jahre":
            return '#d9ed92'
        elif x == "5-10 Jahre":
            return '#99d98c'
        elif x == "10-15 Jahre":
            return '#52b69a'
        elif x == "mehr als 15 Jahre":
            return '#168aad'
        else:
            return '#ecffeb'  # Default color for 'keine'

    avg_feature_data['color'] = avg_feature_data['Condition_Category'].apply(color_mapping)

    # Create the table using Plotly
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{col}</b>", "<b>Avg Feature Condition</b>"],
            align='center',
            font=dict(size=14, color='white'),
            fill_color='#264653',
            height=50
        ),
        cells=dict(
            values=[avg_feature_data[main_col], avg_feature_data['Condition_Category']],
            fill_color=[['#ecffeb'] * len(avg_feature_data), avg_feature_data['color']],
            align='center',
            font=dict(color='black', size=12),
            height=30
        )
    )])

    fig.update_layout(
        title=f"Average Feature Condition by {col}",
        margin=dict(l=0, r=0, t=50, b=0),
        height=800
    )

    return fig


@st.cache_data
def house_condition_choropleth(data):
    condition_mapping = {
        "gut": 5,
        "neuwertig": 4,
        "mittel": 3,
        "Not Specified": 2,
        "renovierungsbeduerftig": 1,
        "schlecht": 0
    }

    def inverse_map(x):
        if x<=0:
            return "schlecht"
        elif 0<x<=1:
            return "renovierungsbeduerftig"
        elif 1<x<=2:
            return "Not Specified"
        elif 2<x<=3:
            return "mittel"
        elif 3<x<=4:
            return "neuwertig"
        elif 4<x<=5:
            return "gut"

    data['Objektzustand_num'] = data['Objektzustand'].map(condition_mapping)
    avg_feature_data = data.groupby('bundesland')['Objektzustand_num'].mean().reset_index().rename({
        "Objektzustand_num":"Avg_Condition"
    }, axis=1)
    avg_feature_data['Condition'] = avg_feature_data['Avg_Condition'].apply(inverse_map)
    reverse_mapping = {v: k for k, v in condition_mapping.items()}

    url = 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json'
    geojson = requests.get(url).json()

    fig = px.choropleth_mapbox(
        avg_feature_data,
        geojson=geojson,
        locations='bundesland',
        featureidkey="properties.name",
        color='Avg_Condition',
        color_continuous_scale='RdYlGn',
        hover_name='bundesland',
        hover_data={'Avg_Condition': False, 'Condition': True},
        labels={'Avg Condition': 'Avg Condition'},
        title="Average House Condition by Bundesland",
        mapbox_style="carto-positron",
        zoom=5,
        center={"lat": 51.1657, "lon": 10.4515},
        opacity=0.8
    )

    fig.update_layout(
        margin={"r":0,"t":60,"l":0,"b":0},
        coloraxis_colorbar=dict(
            tickvals=[0, 1, 2, 3, 4, 5],
            ticktext=[reverse_mapping[5], reverse_mapping[4], reverse_mapping[3], reverse_mapping[2], reverse_mapping[1], reverse_mapping[0]],
            title="House Condition",
            orientation='h',
            xanchor='center',
            x=0.5,
            yanchor='bottom',
            y=-0.2
        ),
        mapbox=dict(bearing=-10),
        height=800,
    )

    return fig


@st.cache_data
def house_condition_table(data, col='City'):
    main_col = 'Ort' if col=='City' else 'Postleitzahl_2'
    condition_mapping = {
        "gut": 5,
        "neuwertig": 4,
        "mittel": 3,
        "Not Specified": 2,
        "renovierungsbeduerftig": 1,
        "schlecht": 0
    }

    reverse_condition_mapping = {v: k for k, v in condition_mapping.items()}
    data['Objektzustand_num'] = data['Objektzustand'].map(condition_mapping)
    avg_feature_data = data.groupby(main_col)['Objektzustand_num'].mean().reset_index().rename({
        "Objektzustand_num": "Avg_Condition"
    }, axis=1)
    avg_feature_data['Condition_Text'] = avg_feature_data['Avg_Condition'].apply(lambda x: reverse_condition_mapping.get(int(np.round(x)), 'Not Specified'))
    def color_mapping(x):
        if x=='gut':
            return '#55a630'
        elif x=='neuwertig':
            return '#aacc00'
        elif x =='mittel':
            return '#ffc100'
        elif x == 'renovierungsbeduerftig':
            return '#ff4747'
        elif x=='schlecht':
            return '#ff4000'
        else:
            return '#ecffeb'
    avg_feature_data['color'] = avg_feature_data['Condition_Text'].apply(color_mapping)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{col}</b>", "<b>Avg House Condition</b>"],
            align='center',
            font=dict(size=14, color='white', family='ubuntu'),
            fill_color='#264653',
            height=50
        ),
        cells=dict(
            values=[avg_feature_data[main_col], avg_feature_data['Condition_Text']],
            fill_color=[['#ecffeb']*len(avg_feature_data), avg_feature_data['color']],
            align='center',
            font=dict(color='black', size=12),
            height=30
        )
    )])
    fig.update_layout(
        title=f"Average House Condition by {col}",
        margin=dict(l=0, r=0, t=50, b=0),
        height=800
    )

    return fig


@st.cache_data
def house_equipment_choropleth(data):
    equipment_mapping = {
        "luxus": 5,
        "gehoben": 4,
        "mittel": 3,
        "Not Specified": 2,
        "einfach": 1,
        "nicht zeitgemaess": 0
    }
    reverse_mapping = {v: k for k, v in equipment_mapping.items()}
    def inverse_map(x):
        if 0 <= x < 1:
            return "nicht zeitgemaess"
        elif 1 <= x < 2:
            return "einfach"
        elif 2 <= x < 3:
            return "Not Specified"
        elif 3 <= x < 4:
            return "mittel"
        elif 4 <= x < 5:
            return "gehoben"
        elif x >= 5:
            return "luxus"

    data['Ausstattung_num'] = data['Ausstattung'].map(equipment_mapping)
    avg_feature_data = data.groupby('bundesland')['Ausstattung_num'].mean().reset_index().rename({
        "Ausstattung_num": "Avg_Equipment"
    }, axis=1)
    avg_feature_data['Equipment'] = avg_feature_data['Avg_Equipment'].apply(inverse_map)

    url = 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json'
    geojson = requests.get(url).json()

    fig = px.choropleth_mapbox(
        avg_feature_data,
        geojson=geojson,
        locations='bundesland',
        featureidkey="properties.name",
        color='Avg_Equipment',
        hover_name='bundesland',
        hover_data={'Avg_Equipment': False, 'Equipment': True},
        labels={'Avg_Equipment': 'Avg Equipment'},
        title="Average House Equipment by Bundesland",
        mapbox_style="carto-positron",
        zoom=5,
        center={"lat": 51.1657, "lon": 10.4515},
        color_continuous_scale='RdYlGn',
        opacity=0.8
    )

    fig.update_layout(
        margin={"r":0,"t":60,"l":0,"b":0},
        coloraxis_colorbar=dict(
            tickvals=[0, 1, 2, 3, 4, 5],
            ticktext=[reverse_mapping[5], reverse_mapping[4], reverse_mapping[3], reverse_mapping[2], reverse_mapping[1], reverse_mapping[0]],
            title="House Equipment",
            orientation='h',
            xanchor='center',
            x=0.5,
            yanchor='bottom',
            y=-0.2
        ),
        mapbox=dict(bearing=-10),
        height=800
    )

    return fig


@st.cache_data
def house_equipment_table(data, col='City'):
    main_col = 'Ort' if col == 'City' else 'Postleitzahl_2'

    # Condition mapping for equipment type
    equipment_mapping = {
        "luxus": 5,
        "gehoben": 4,
        "mittel": 3,
        "Not Specified": 2,
        "einfach": 1,
        "nicht zeitgemaess": 0
    }

    reverse_equipment_mapping = {v: k for k, v in equipment_mapping.items()}

    # Apply equipment mapping
    data['Ausstattung_num'] = data['Ausstattung'].map(equipment_mapping)

    # Group by chosen column and calculate average equipment score
    avg_feature_data = data.groupby(main_col)['Ausstattung_num'].mean().reset_index().rename({
        "Ausstattung_num": "Avg_Condition"
    }, axis=1)

    avg_feature_data['Condition_Text'] = avg_feature_data['Avg_Condition'].apply(lambda x: reverse_equipment_mapping.get(int(np.round(x)), 'Not Specified'))

    def color_mapping(x):
        if x == 'luxus':
            return '#55a630'
        elif x == 'gehoben':
            return '#aacc00'
        elif x == 'mittel':
            return '#ffc100'
        elif x == 'einfach':
            return '#ff4747'
        elif x == 'nicht zeitgemaess':
            return '#ff4000'
        else:
            return '#ecffeb'

    avg_feature_data['color'] = avg_feature_data['Condition_Text'].apply(color_mapping)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{col}</b>", "<b>Avg Equipment Condition</b>"],
            align='center',
            font=dict(size=14, color='white'),
            fill_color='#264653',
            height=50
        ),
        cells=dict(
            values=[avg_feature_data[main_col], avg_feature_data['Condition_Text']],
            fill_color=[['#ecffeb'] * len(avg_feature_data), avg_feature_data['color']],
            align='center',
            font=dict(color='black', size=12),
            height=30
        )
    )])

    fig.update_layout(
        title=f"Average Equipment Condition by {col}",
        margin=dict(l=0, r=0, t=50, b=0),
        height=800
    )

    return fig


def lead_usage_distribution(data):
    usage_data = data.groupby('Aktuelle Nutzung')['Id'].count().reset_index()
    usage_data = usage_data.sort_values(by='Id', ascending=False)

    usage_data = usage_data[usage_data['Id']>0]
    if len(usage_data) == 0 or usage_data['Id'].sum()==0:
        return show_indicator(0, "No leads", "Aktuelle Nutzung Distribution")
    elif len(usage_data) == 1 or len(usage_data[usage_data['Id']>0])==1:
        single_category = usage_data['Aktuelle Nutzung'].iloc[0]
        single_count = usage_data['Id'].iloc[0]
        return show_indicator(single_count, single_category, "Aktuelle Nutzung Distribution")

    fig = go.Figure(go.Pie(
        labels=usage_data['Aktuelle Nutzung'],
        values=usage_data['Id'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Aktuelle Nutzung",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Aktuelle Nutzung Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.45, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig = format_fig_layout(fig)

    return fig


def lead_parking_distribution(data):
    parking_data = data.groupby('Parkplatz')['Id'].count().reset_index()
    parking_data = parking_data.sort_values(by='Id', ascending=False)

    parking_data = parking_data[parking_data['Id']>0]
    if len(parking_data) == 0 or parking_data['Id'].sum()==0:
        return show_indicator(0, "No leads", "Parking Types")
    elif len(parking_data) == 1 or len(parking_data[parking_data['Id']>0])==1:
        single_category = parking_data['Parkplatz'].iloc[0]
        single_count = parking_data['Id'].iloc[0]
        return show_indicator(single_count, single_category, "Parking Types")

    fig = go.Figure(go.Pie(
        labels=parking_data['Parkplatz'],
        values=parking_data['Id'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Parkplatz",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Parking Types",
        legend=dict(orientation="h", xanchor='center', x=0.40, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig = format_fig_layout(fig)

    return fig


def lead_htype_distribution(data):
    htype_data = data.groupby('Haustyp')['Id'].count().reset_index()
    htype_data = htype_data.sort_values(by='Id', ascending=True)

    htype_data = htype_data[htype_data['Id']>0]
    if len(htype_data) == 0 or htype_data['Id'].sum()==0:
        return show_indicator(0, "No leads", "House Types")
    elif len(htype_data) == 1 or len(htype_data[htype_data['Id']>0])==1:
        single_category = htype_data['Haustyp'].iloc[0]
        single_count = htype_data['Id'].iloc[0]
        return show_indicator(single_count, single_category, "House Types")

    fig = go.Figure(go.Bar(
        x=htype_data['Id'],
        y=htype_data['Haustyp'],
        text=htype_data['Id'],
        orientation='h',  # Horizontal bar chart
        marker=dict(color='steelblue'),
        hovertemplate='<b>%{y}</b><br>Total Properties= %{x}<extra></extra>',
    ))

    fig = format_fig_layout(fig)

    fig.update_layout(
        title="House Type Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.40, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
        hovermode="y unified",
        height=500
    )

    return fig


def lead_feats_count_chart(df):
    lead_features = ["Bebaut", "Alleinlage", "Erschlossen", "Gastwc", "Vollvermietet",
                     "Balkon", "Aufzug", "Dachgeschoss", "Keller", "Verkaufspreis",
                     "Wertanalyse", "Verrentung"]
    lead_count_df = pd.DataFrame({
        'Feature Name': lead_features,
        'Total Leads': [df[col].value_counts().get('Ja', 0) for col in lead_features]
    })

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(lead_count_df.columns),
            font=dict(size=14, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['center'],
            height=50
        ),
        cells=dict(
            values=[lead_count_df[K].tolist() for K in lead_count_df.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            fill_color='#f1faee',
            align=['left'],
            height=30
        ))]
    )

    fig = format_fig_layout(fig)
    fig.update_layout(
        title="Feature Availability Chart",
        margin=dict(t=50, l=0, r=0, b=0),
        height=500
    )

    return fig


def lead_equipment_distribution(data):
    equipment_data = data.groupby('Ausstattung')['Id'].count().reset_index()
    equipment_data = equipment_data.sort_values(by='Id', ascending=False)

    equipment_data = equipment_data[equipment_data['Id'] > 0]
    if len(equipment_data) == 0 or equipment_data['Id'].sum() == 0:
        return show_indicator(0, "No leads", "Equipment Types")
    elif len(equipment_data) == 1:
        single_category = equipment_data['Ausstattung'].iloc[0]
        single_count = equipment_data['Id'].iloc[0]
        return show_indicator(single_count, single_category, "Equipment Types")

    fig = go.Figure(go.Pie(
        labels=equipment_data['Ausstattung'],
        values=equipment_data['Id'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Ausstattung",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))
    fig.update_layout(
        title="Equipment Types",
        legend=dict(orientation="h", xanchor='center', x=0.40, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig = format_fig_layout(fig)

    return fig


def lead_detail_table(df):
    df = df.reset_index()
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Field', 'Value'],
            font=dict(size=14, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['center'],
            height=40
        ),
        cells=dict(
            values=[df[K].tolist() for K in df.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            fill_color='#f1faee',
            align=['left'],
            height=30
        ))]
    )

    fig = format_fig_layout(fig)
    fig.update_layout(
        title="Lead Detail",
        margin=dict(t=50, l=0, r=0, b=0),
        height=650
    )

    return fig