"""
Class: CS230--Section 2
Name: Khalifa Alharmoodi
Description: (This is the final project to analyze data)
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

#Function to read data
def read_data(p):
    df = pd.read_csv(p, header=1).set_index('Volcano Number')
    return df

#Function to get unique values in given column
def get_uniques(df, column_name):
    activity_evidences_list = pd.unique(df[column_name])
    return activity_evidences_list

#Function to count each instance in `instances` list in given column
def count_in_df(instances, df, column_name):
    return [df.loc[df[column_name].isin([instance])].shape[0] for instance in instances]

#Function to generate pie chart of frequencies
def generate_pie_chart(frequency, labels):
    plt.figure()
    explodes = np.arange(len(frequency), dtype=np.float64)[np.argsort(frequency)]
    explodes /= 10 * np.max(explodes)
    plt.pie(frequency, labels=labels, explode=explodes, autopct="%.1f%%")
    return plt

#Function to generate plt bar chart
def generate_bar_chart(y, x, y_label):
    color = st.sidebar.color_picker('Pick a color for the Bar Chart')
    plt.figure()
    plt.title(f"Volcanoes per {y_label}")
    plt.barh(y, x, color=color)
    plt.xticks(x)
    plt.xlabel('Volcano Count')
    plt.ylabel(y_label)
    plt.grid(color='grey', linestyle='--')
    return plt

#Function to generate plt horizontal bar chart
def generate_barh_chart(y, x, y_label, color):
    plt.figure()
    plt.title(f"Volcanoes per {y_label}")
    plt.barh(y, x, color=color)
    plt.xticks(x)
    plt.xlabel('Volcano Count')
    plt.ylabel(y_label)
    plt.grid(color='grey', linestyle='--')
    return plt

#Function to generate map
def generate_map(df):
    map_df = df.filter(['Volcano Name', 'Latitude', 'Longitude', 'Elevation (m)'])
    elevations = map_df['Elevation (m)']
    elevations += np.min(elevations)
    elevations = 1e+6 * np.exp(elevations / np.max(elevations))
    elevations = np.clip(elevations, 0, 100000)
    map_df['radius'] = elevations

    view_state = pdk.ViewState(latitude=map_df['Latitude'].mean(),
                               longitude=map_df['Longitude'].mean(),
                               zoom=2)

    volcano_layer = pdk.Layer('ScatterplotLayer',
                              data=map_df,
                              get_position='[Longitude, Latitude]',
                              get_radius='radius',
                              get_color=[245, 70, 20],
                              elevation_scale=10,
                              pickable=True,
                              extruded=True)

    tool_tip = {'html': 'Volcano: <b>{Volcano Name}</b><br>Elevation: <b>{Elevation (m)}</b>m',
                'style': {'backgroundColor': 'steelblue', 'color': 'white'}}

    generated_map = pdk.Deck(initial_view_state=view_state,
                             layers=[volcano_layer],
                             tooltip=tool_tip)

    return generated_map

#Formatting the output
st.title('Volcanic Eruptions')

tabs = {
    "Home": "Homepage",
    "Activity Evidence": "Activity Evidence - Pie Chart",
    "Volcanoes per Country": "Volcanoes per Country - Bar Chart",  # volcanoes per country
    "Tectonic Settings": "Tectonic Settings - Bar Chart",  # volcanoes per tectonic setting
    "Map": "Map of Volcano Locations",
    "Dataset": "Full Dataset",
    "Filtering": "Filtering the Dataset"
}

home, pie, bar_country, bar_tectonic, volcano_map, volcano_df, filter_df = st.tabs(tabs.keys())
#Option to have sidebar rather than options under title
#st.sidebar.title("Select one of the options to navigate between tabs:")

data = read_data("GVP_Volcano_List_Holocene.csv")

#Homepage formatting with picture
with home:
    st.image("krakatau-indonesia.jpeg",
             caption="Image Source: "
                     "https://deih43ym53wif.cloudfront.net/krakatau-indonesia-shutterstock_1272261541_79eebad9da.jpeg")
    st.subheader("About the Dataset: ")
    st.write("The 'GVP Volcano List Holocene' dataset contains 1.4k volcano eruptions occurred."
             " It includes information about the number, name, country, primary type, activity evidence,"
             " last known eruption, region, subregion, the location (with latitude and longitude), elevation,"
             " dominant rock type and tectonic setting of the volcano."
             " Users will be able to explore the statistics using the sidebar options.")

#Pie Chart of Activity Evidences with option do add
with pie:
    column = "Activity Evidence"
    options = st.multiselect("Select the types of offenses to add to your Pie Chart: ",
                             get_uniques(data, column),
                             default=['Eruption Dated', 'Eruption Observed'])
    counts = count_in_df(options, data, column)

    pie_chart = generate_pie_chart(counts, options)
    plt.title(f"Pie Chart of {column}")
    st.pyplot(pie_chart)

#Bar chart of volcanoes per country with options to add and remove countries
with bar_country:
    st.write("Here you can explore number of volcanoes in each country:")
    column = "Country"
    country_options = st.multiselect("Select countries: ", sorted(get_uniques(data, column)),
                                     default=["Japan", "Armenia", "United States"])
    volcano_cnt = count_in_df(country_options, data, column)

    bar_color = st.color_picker('Pick a color for the Country Bar Chart')
    st.pyplot(generate_barh_chart(country_options, volcano_cnt, column, bar_color))

#Bar chart of tectonic setting with option to change color of bars
with bar_tectonic:
    st.write("Here you can explore number of volcanoes for each tectonic setting:")
    column = "Tectonic Setting"

    tectonic_settings = get_uniques(data, column)
    tectonic_settings = map(str, tectonic_settings)
    tectonic_settings = sorted(tectonic_settings, key=lambda x: x.split('/'))

    volcano_cnt = count_in_df(tectonic_settings, data, column)

    bar_color = st.color_picker('Pick a color for the Tectonic Setting Bar Chart')
    barh_chart = generate_barh_chart(tectonic_settings, volcano_cnt, column, bar_color)
    plt.xscale("log")       #exponentional so no overlapping
    st.pyplot(barh_chart)

#Map of Volcanoes
with volcano_map:
    st.pydeck_chart(generate_map(data))

#See DataFrame
with volcano_df:
    st.write("This is the DataFrame")
    st.write(data)
    st.write(f"Total Number of Volcanoes: {len(data.index)}")

#allowing filteration of data
with filter_df:
    # Filter DataFrame
    st.write("Here you can filter the dataset based on different columns")
    options = st.multiselect('Choose specific Columns to filter the DataFrame:',
                             data.columns,
                             default=['Volcano Name', 'Region', 'Elevation (m)'])
    df2 = data.filter(options)
    st.write(df2)
