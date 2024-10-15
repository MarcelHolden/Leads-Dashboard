import pandas as pd


def fill_na_columns(data, columns, fill_value):
    """
    Function to handle missing values for specific columns.
    """
    for col in columns:
        data[col] = data[col].fillna(fill_value)
    return data


def fill_grundstueckflaeche_with_mean(data):
    """
    Function to fill missing values in 'Grundstueckflaeche' with its mean.
    """
    if data['Grundstueckflaeche'].isnull().any():
        mean_area = data['Grundstueckflaeche'].mean()
        data['Grundstueckflaeche'] = data['Grundstueckflaeche'].fillna(mean_area)
    return data


def process_baujahr(data):
    """
    Function to process the 'Baujahr' column.
    """
    data['Baujahr'] = pd.to_numeric(data['Baujahr'], errors='coerce')
    data['Baujahr'] = data['Baujahr'].dropna().astype(int).round()
    data = data[(data['Baujahr'] >= 1000) & (data['Baujahr'] <= 9999)]
    return data


def categorize_property_area(data):
    """
    Function to bin the living area and categorize it.
    """
    living_area_bins = [0, 800, 1100, 1300, 1500, 2000, 3000, 12900]
    living_area_labels = [
        'Up to 800 sqm',
        '800-1100 sqm',
        '1100-1300 sqm',
        '1300-1500 sqm',
        '1500-2000 sqm',
        '2000-3000 sqm',
        'Above 3000 sqm'
    ]
    data['property_area_range'] = pd.cut(data['Grundstueckflaeche'], bins=living_area_bins, labels=living_area_labels)
    return data


def process_postleitzahl(data):
    """
    Function to process 'Postleitzahl' column.
    """
    data['Postleitzahl_2'] = data['Postleitzahl'].apply(lambda x: f"DE-{str(x)[-2:]}" if x != 'Not Specified' else x)
    return data


def process_created_at(data):
    """
    Function to fill 'Created_at' column with proper datetime values.
    """
    data['Created_at'] = pd.to_datetime(data['Created_at'], errors='coerce')
    return data


def process_rental_income(df):
    df['Mieteinnahmen (Kaltmiete)'] = df['Mieteinnahmen (Kaltmiete)'].fillna(0)
    # df['Mieteinnahmen (Kaltmiete)'] = df['Mieteinnahmen (Kaltmiete)'].str.replace(r'[€,\smonatlich, â‚ ¬]', '', regex=True)
    # df['Mieteinnahmen (Kaltmiete)'] = df['Mieteinnahmen (Kaltmiete)'].str.replace(',', '.')
    # df['Mieteinnahmen (Kaltmiete)'] = pd.to_numeric(df['Mieteinnahmen (Kaltmiete)'], errors='coerce')
    return df


def process_data(data):
    """
    Main process_data function that integrates all the smaller functions.
    """

    data['Id'] = data['Id'].astype('int64')

    # Fill missing values for 'bundesland', 'Ort', and 'Postleitzahl', 'Objektzustand', 'Ausstattung'
    data = fill_na_columns(data, ['bundesland', 'Ort', 'Postleitzahl', 'Objektzustand', 'Ausstattung', 'Objekttyp', 'Haustyp', 'Aktuelle Nutzung'], 'Not Specified')

    # Fill missing 'Grundstueckflaeche' with mean value
    data = fill_grundstueckflaeche_with_mean(data)

    # Process 'Baujahr' column
    data = process_baujahr(data)

    # Categorize property area
    data = categorize_property_area(data)

    # Process 'Postleitzahl' column
    data = process_postleitzahl(data)

    # Process 'Created_at' column
    data = process_created_at(data)

    # Fill numerical columns with 0
    numerical_cols = ['Wohneinheiten', 'Gewerbeeinheiten', 'Geschaeftsflaeche',
                      'Anhaenge/Dateien', 'Zimmeranzahl', 'Etagenanzahl']
    data = fill_na_columns(data, numerical_cols, 0)

    # Fill categorical columns with 'Nein'
    categorical_cols_nein = ["Bebaut", "Alleinlage", "Erschlossen", 'Gastwc', 'Vollvermietet',
                             'Balkon', 'Aufzug', 'Dachgeschoss', 'Keller', "100-Tage-Verkaufsgarantie",
                             "Verkaufspreis", "Wertanalyse", "Verrentung"]
    data = fill_na_columns(data, categorical_cols_nein, 'Nein')

    # Fill 'Parkplatz' column with 'nein'
    data['Parkplatz'] = data['Parkplatz'].fillna('nein')

    # Fill other specific columns with 'keine' or 'No Information'
    categorical_cols_keine = ['Dach', 'Fenster', 'Leitungen', 'Heizung', 'Fassade',
                              'Badezimmer', 'Innenausbau', 'Grundrissgestaltung']
    data = fill_na_columns(data, categorical_cols_keine, 'keine')

    information_cols = ['Immobilie und Lage', 'Objektinformationen', 'Modernisierungen',
                        'Schaeden/Maengel', 'Informationen zu besonderen Rechten', 'Nachricht']
    data = fill_na_columns(data, information_cols, 'No Information')

    data = process_rental_income(data)

    return data
