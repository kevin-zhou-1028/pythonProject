'''
Class: CS230-- Section 001
Name: Kevin Zhou
Description: Final Project
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
'''
import plotly_express as px
import datetime
import streamlit as st
import pandas as pd
import numpy as np

DATASET = "Boston Crime Incident Report.csv"
DISTRICT = "BostonPoliceDistricts.csv"

st.set_page_config(
    page_title="Home Page",
    page_icon="🏡",
)

# read dataframe input file
def read_file(filename):
    dataf = pd.read_csv(filename,dtype={"INCIDENT_NUMBER":"string"})

    occuredDate = dataf["OCCURRED_ON_DATE"]
    dateTime = [i.split() for i in occuredDate]

    date = [a[0] for a in dateTime]
    dataf["OCCURRED_ON_DATE"] = date
    # replace column name for mapping and filtering
    dataf.rename(columns={'OCCURRED_ON_DATE':'DATE', 'Lat': 'lat', 'Long': 'lon'}, inplace=True)

    # change value in DATE column from string to datetime
    dataf["DATE"] = pd.to_datetime(dataf['DATE'])
    dataf["DATE"] = dataf["DATE"].dt.date
    return dataf

def read_sheet(filename):
    district = pd.read_csv(filename)
    district_list = district["District"].tolist()

    return district_list

# create page navigator for multi-page app
page = st.sidebar.selectbox("Page Navigator",
                            ["Home Page", "Mapping Demo", "Chart Demo", "Table Demo"])

# separate pages according to users choices; include corresponding functions in the selected page
if page == "Home Page":
    def home_page():
        # create home page layout
        st.header("CS230 Final Project Boston Crime")
        st.subheader("Instructor: Tom Connors")

        st.sidebar.header("Home Page")

        st.markdown(
            """
            **👈 Select a demo from the sidebar** to view project
            ### Programmer Info
            - Name: Kevin Zhou
            - Class section: CS230 Section 1
        """
        )

elif page == "Mapping Demo":
    def filter_data(dataset, district):

        map_filter = {}
        columns = dataset.columns[:-1]
        # create filter options using columns, remove column names
        # that cannot be filtered or contain too many categories
        col = [columns[i] for i in range(len(columns))]
        remove_list = ["INCIDENT_NUMBER", "OFFENSE_CODE", "OFFENSE_CODE_GROUP", "REPORTING_AREA", "STREET", "HOUR", "YEAR", "UCR_PART"]
        for i in remove_list:
            if i in col:
                col.remove(i)

        # multiselect box for user to choose filter option, always
        # display message to inform users that lat and lon must be included
        main_filter = st.sidebar.multiselect("Please select filters", col, default=col[-2:])
        if "lot" not in main_filter or "lat" not in main_filter:
            st.sidebar.warning("Filter must include lat and lon")

        # create sub-filters based on main filter choice
        if "DISTRICT" in main_filter:
            distrtict_filter = st.multiselect("Please choose districts", district)
            map_filter["DISTRICT"] = distrtict_filter

        if "OFFENSE_DESCRIPTION" in main_filter:
            offense = np.sort(dataset["OFFENSE_DESCRIPTION"].unique())  # get unique values in column
            code_filter = st.multiselect("Please choose offense", offense)
            map_filter["OFFENSE_DESCRIPTION"] = code_filter

        if "SHOOTING" in main_filter:
            map_filter["SHOOTING"] = [1]

            # Obtain input for time range
        if "DATE" in main_filter:
            min_date = datetime.date(2021, 1, 1)
            max_date = datetime.date(2021, 12, 31)
            start_date = st.date_input('Start date', min_date, min_value=min_date, max_value=max_date)
            end_date = st.date_input("end date", max_date, min_value=min_date, max_value=max_date)

            if start_date > end_date:
                st.warning("End date must be bigger than start day, please try again")
            map_filter["STARTDATE"] = start_date
            map_filter["ENDDATE"] = end_date

        if "MONTH" in main_filter:
            month = np.sort(dataset["MONTH"].unique())  # get unique values in column
            month_filter = st.multiselect("Please choose month", month)
            map_filter["MONTH"] = month_filter

        if "DAY_OF_WEEK" in main_filter:
            day = np.sort(dataset["DAY_OF_WEEK"].unique())  # get unique values in column
            day_filter = st.multiselect("Please choose day", day)
            map_filter["DAY_OF_WEEK"] = day_filter

        return map_filter

    # create dataframe to put into map function based on user filter selection
    def filtered_frame(dataset, filters):
        # if user choose date range, filter dataframe based on date first
        if "STARTDATE" in filters.keys() and "ENDDATE" in filters.keys():
            start_date = filters["STARTDATE"]
            end_data = filters["ENDDATE"]

            filtered_df = dataset.loc[(dataset["DATE"] >= start_date) & (dataset["DATE"] <= end_data)]
            filters.pop("STARTDATE")
            filters.pop("ENDDATE")

            for key, value in filters.items():  # for loop to filter dataframe all rows wanted based on filters
                filtered_df = filtered_df[filtered_df[key].isin(value)]

        else:
            filtered_df = dataset
            for key, value in filters.items():
                filtered_df = filtered_df[filtered_df[key].isin(value)]

        return filtered_df

elif page == "Chart Demo":
    st.sidebar.header("Chart Demo")

    # separate demo into two parts
    charts = st.sidebar.radio("Select the chart you want to see:", ("Pie and Bar Chart", "Line Chart"))
    if charts == "Pie and Bar Chart":
        def chart_filters(dataset, district):
            # create dictionary of dictionary for filters, key of top layer dictionary is main theme, key of second
            # layer dictionary if column name, values of second layer dictionary is a list store row values
            chart_filter = {}
            st.subheader("Pie Chart and Bar Chart")

            # select theme as the first filter
            selection = st.sidebar.radio("Select a theme:", ("Location", "Time"))
            if selection == "Location":
                loc_filter = {}

                # specify main theme
                location = st.sidebar.selectbox("Please select a type of Location", ["DISTRICT", "REPORTING_AREA", "STREET"])
                if location == "DISTRICT":
                    district_filter = st.sidebar.multiselect("Please choose districts", district)
                    loc_filter["DISTRICT"] = district_filter

                elif location == "REPORTING_AREA":
                    area = np.sort(dataset["REPORTING_AREA"].unique())  # get unique value
                    area_filter = st.sidebar.multiselect("Please choose reporting area", area)
                    loc_filter["REPORTING_AREA"] = area_filter

                else:
                    street = np.sort(dataset["STREET"].unique())
                    street_filter = st.sidebar.multiselect("Please choose street", street)
                    loc_filter["STREET"] = street_filter

                chart_filter["Location"] = loc_filter

                # second layer dictionary for chart_filter
                crime_filter = {}
                offense = np.sort(dataset["OFFENSE_DESCRIPTION"].unique())
                crime = st.sidebar.multiselect("Please select a type Crime", offense)

                crime_filter["OFFENSE_DESCRIPTION"] = crime
                chart_filter["Crime"] = crime_filter

            if selection == "Time":
                # second layer dictionary, dictionary of list
                time_filter = {}
                time = st.sidebar.selectbox("Please select a type of Time", ["DATE", "DAY_OF_WEEK", "MONTH"])
                min_date = datetime.date(2021,1,1)
                max_date = datetime.date(2021,12,31)

                if time == "DATE":
                    start_date = st.date_input('Start date', min_date, min_value=min_date,
                                               max_value=max_date)
                    end_date = st.date_input("end date", max_date, min_value=min_date,
                                               max_value=max_date)
                    if (start_date > end_date):
                        st.warning("End date must be bigger than start day, please try again")

                        # start and end dates create date range
                    time_filter["STARTDATE"] = start_date
                    time_filter["ENDDATE"] = end_date

                elif time == "DAY_OF_WEEK":
                    day = np.sort(dataset["DAY_OF_WEEK"].unique())
                    day_filter = st.sidebar.multiselect("Please choose day", day)
                    time_filter["DAY_OF_WEEK"] = day_filter

                else:
                    month = np.sort(dataset["MONTH"].unique())
                    month_filter = st.sidebar.multiselect("Please choose month", month)
                    time_filter["MONTH"] = month_filter

                chart_filter["Time"] = time_filter
                crime_filter = {}
                offense = np.sort(dataset["OFFENSE_DESCRIPTION"].unique())
                crime = st.sidebar.multiselect("Please select a type Crime", offense)

                crime_filter["OFFENSE_DESCRIPTION"] = crime
                chart_filter["Crime"] = crime_filter

            return chart_filter

        def chart(dataset, filters):
            # list all row and column combinations
            if "Location" in filters.keys():
                # dataframe district + crime
                if "DISTRICT" in filters["Location"].keys():
                    df = dataset[dataset["DISTRICT"].isin(filters["Location"]["DISTRICT"])
                                 & dataset["OFFENSE_DESCRIPTION"].isin(filters["Crime"]["OFFENSE_DESCRIPTION"])]

                # data frame reporting area + crime
                elif "REPORTING_AREA" in filters["Location"].keys():
                    df = dataset[dataset["REPORTING_AREA"].isin(filters["Location"]["REPORTING_AREA"])
                                 & dataset["OFFENSE_DESCRIPTION"].isin(filters["Crime"]["OFFENSE_DESCRIPTION"])]

            elif "Time" in filters.keys():
                # dataframe time range + crime
                if "STARTDATE" in filters["Time"].keys() and "ENDDATE" in filters["Time"].keys():
                    df1 = dataset.loc[(dataset["DATE"] >= filters["Time"]["STARTDATE"]) &
                                     (dataset["DATE"] <= filters["Time"]["ENDDATE"])]

                    df = df1[dataset["OFFENSE_DESCRIPTION"].isin(filters["Crime"]["OFFENSE_DESCRIPTION"])]

                # dataframe day of week + crime
                elif "DAY_OF_WEEK" in filters["Time"].keys():
                    df = dataset[dataset["DAY_OF_WEEK"].isin(filters["Time"]["DAY_OF_WEEK"])
                                 & dataset["OFFENSE_DESCRIPTION"].isin(filters["Crime"]["OFFENSE_DESCRIPTION"])]

                # dataframe month + crime
                else:
                    df = dataset[dataset["MONTH"].isin(filters["Time"]["MONTH"])
                                 & dataset["OFFENSE_DESCRIPTION"].isin(filters["Crime"]["OFFENSE_DESCRIPTION"])]

            # group offense type and count each offense type based on rows returned
            df_grouped = df.groupby(by=["OFFENSE_DESCRIPTION"]).size().reset_index(name="counts")
            # pie chart where labels are offense description and percentages are proportions to total counts
            fig = px.pie(data_frame=df_grouped, values="counts", names="OFFENSE_DESCRIPTION",
                         title=f"Pie Chart for Crime Rate for {filters[list(filters.keys())[0]]}")

            st.write(df_grouped)
            # bar chart to supplement pie chart
            fig1 = px.bar(data_frame=df_grouped, x="OFFENSE_DESCRIPTION", y="counts",
                          title=f"Barchart for Crime Count for {filters[list(filters.keys())[0]]}")
            return fig, fig1
    else:
        # line chart that shows fluctuations of crime frequency in Boston in 2021
        def plot_chart_filter(dataset, districts):
            st.subheader("Line Chart - Fluctuation of Crime rate")
            max_date = datetime.date(2021, 12, 31)
            # user select days interval they want to visualize, date always start from last day of year
            # default selection 365
            days = st.radio("Select Days to View", [365, 180, 90, 60, 30, 10, 5], horizontal=True)
            if days == 5:
                min_date = datetime.date(2021, 12, 26)
            elif days == 10:
                min_date = datetime.date(2021, 12, 21)
            elif days == 30:
                min_date = datetime.date(2021, 12, 1)
            elif days == 60:
                min_date = datetime.date(2021, 11, 1)
            elif days == 90:
                min_date = datetime.date(2021, 10, 2)
            elif days == 180:
                min_date = datetime.date(2021, 7, 4)
            elif days == 365:
                min_date = datetime.date(2021, 1, 1)

            dataset = dataset.loc[(dataset["DATE"] >= min_date) &
                              (dataset["DATE"] <= max_date)]

            further_filter = st.sidebar.radio("Select a theme:", ("District", "Offense", "Both"))
            # see fluctuation based on districts
            if further_filter == "District":
                district_filter = st.sidebar.multiselect("Filter by Districts", districts, default=districts)
                dataset = dataset.loc[dataset["DISTRICT"].isin(district_filter)]

            # see fluctuations based on offense types
            elif further_filter == "Offense":
                offense = np.sort(dataset["OFFENSE_DESCRIPTION"].unique())
                offense_filter = st.sidebar.multiselect("Please choose an offense", offense, default="AFFRAY")
                dataset = dataset.loc[dataset["OFFENSE_DESCRIPTION"].isin(offense_filter)]

            # see fluctuations from both location and crime types
            else:
                district_filter = st.sidebar.multiselect("Filter by Districts", districts, default=districts)
                dataset = dataset.loc[dataset["DISTRICT"].isin(district_filter)]
                offense = np.sort(dataset["OFFENSE_DESCRIPTION"].unique())
                offense_filter = st.sidebar.multiselect("Please choose an offense", offense, default="AFFRAY")
                dataset = dataset.loc[dataset["OFFENSE_DESCRIPTION"].isin(offense_filter)]

            # group by date so streamlit can count number of crimes on each day and create line chart
            df_grouped = dataset.groupby(by=["DATE"]).size().reset_index(name="counts")
            fig2 = px.line(df_grouped, x='DATE', y="counts", title="Fluctuation of Crime rate in Boston in Year 2021")
            return fig2


elif page == "Table Demo":
    def table_demo(dataset):
        columns = dataset.columns[:-1]
        col = [columns[i] for i in range(len(columns))]
        st.header("Table Generator")
        st.subheader("Type to find rows")
        # By entering a text the only rows that contain the text is shown in Dataframe
        # row filter placed before column filter so even though a column is excluded
        # rows that match text input are still returned
        text = st.text_input("Entry box")
        for c in col:
            if text in dataset[c].unique().tolist():
                dataset = dataset[dataset[c] == text]
                break
        st.subheader("Add or remove columns")
        column_filter = st.multiselect("Your Choice", col, col)
        dataset = dataset[column_filter]

        return dataset

def main():
    dataf = read_file(DATASET)

    district_list = read_sheet(DISTRICT)

    if page == "Home Page":
        home_page()
        st.sidebar.markdown("""
        **Menu**
        - Mapping Demo
        - Chart Demo
        - Table Demo""")

    elif page == "Mapping Demo":
        st.sidebar.header("Mapping Demo")
        map_filter = filter_data(dataf, district_list)
        # generate filters for dataframe
        filtered_df = filtered_frame(dataf, map_filter)

        # exclude location (0.0, 0.0)
        df = filtered_df.loc[:, ["INCIDENT_NUMBER", "lat", "lon"]]
        df2 = df.loc[(df['lat'] != 0) & (df['lon'] != 0)]

        st.subheader("Map of Location for Crime Incident in Boston")
        st.map(df2)

    elif page == "Chart Demo":
        if charts == "Pie and Bar Chart":
            st.sidebar.subheader("Pie Chart& Bar Chart")
            # call function to create filter
            chart_filter = chart_filters(dataf, district_list)
            # create pie chart - fig, barchart - fig1
            fig, fig1 = chart(dataf, chart_filter)
            # generate chart on streamlit
            st.plotly_chart(fig)
            st.plotly_chart(fig1)
        else:
            st.sidebar.subheader("Line Chart")
            # create line chart - fig2
            fig2 = plot_chart_filter(dataf, district_list)
            # generate line chart on streamlit
            st.plotly_chart(fig2)


    elif page == "Table Demo":

        dataset = table_demo(dataf)
        st.dataframe(dataset)
        # download cvs file function, source: streamlit.documentation
        @st.cache
        def convert_df(df):
            return df.to_csv().encode('utf-8')
        csv = convert_df(dataset)
        st.download_button(label="Download data as CSV",
                           data=csv,
                           file_name='Boston_Crime_Report.csv',
                           mime='text/csv')


if __name__ == "__main__":
    main()

