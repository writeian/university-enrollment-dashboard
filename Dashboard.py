import streamlit as st
   import pandas as pd
   import plotly.express as px

   # Title of the app
   st.title('University Enrollment Data Dashboard')

   # Upload CSV file
   uploaded_file = st.file_uploader('Upload your enrollment data CSV', type=['csv'])

   if uploaded_file is not None:
       # Read the CSV file
       df = pd.read_csv(uploaded_file)

       # Display dataset
       if st.checkbox('Show raw data'):
           st.write(df)

       # Enrollment trends over time
       enrollment_trend = df['Year of Enrollment'].value_counts().sort_index()
       st.subheader('Enrollment Trends')
       st.bar_chart(enrollment_trend)

       # Demographic breakdowns
       st.subheader('Demographic Breakdown')
       demographics = df.groupby(['Gender', 'Year of Enrollment']).size().reset_index(name='Count')
       fig = px.bar(demographics, x='Year of Enrollment', y='Count', color='Gender', barmode='group')
       st.plotly_chart(fig)

       # Course popularity
       st.subheader('Course Popularity')
       course_popularity = df['Major'].value_counts()
       fig = px.pie(course_popularity, names=course_popularity.index, values=course_popularity.values, title='Course Popularity')
       st.plotly_chart(fig)

       # Filter options
       st.sidebar.title('Filter Options')
       selected_major = st.sidebar.selectbox('Select Major:', df['Major'].unique())
       filtered_data = df[df['Major'] == selected_major]
       st.write(f'Filtered data for major: {selected_major}')
       st.write(filtered_data)
   else:
       st.write('Please upload a CSV file to get started.')