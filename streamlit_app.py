import streamlit as st
import pandas as pd
from openai import OpenAI
from PIL import Image

# Fetch the OpenAI API key from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]

# Initialize the OpenAI client using the API key from Streamlit secrets
client = OpenAI(api_key=api_key)

# LOGO
st.info("MULTIFACTOR AI - for NIFCO")

# Title of the Streamlit app
st.title("Warehouse Management Assistant")
st.header("Based on sales volume and provided data, where should a part be stored?")

# Initialize session state for storing combined Excel data
if "combined_data" not in st.session_state:
    st.session_state.combined_data = None

# Step 1: Excel File Uploader
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

# Step 2: Text Input Fields for Parameters
part_number = st.text_input("Enter Part Number:")
customer = st.text_input("Enter Customer Name:")
months = st.number_input("Last X Months of Sales Volume:", min_value=1, value=3, step=1)

# Step 3: Submit Button to trigger the OpenAI API call
if st.button("Submit"):
    if not uploaded_file or not part_number or not customer:
        st.error("Please upload the Excel file and fill in all input fields before submitting.")
    else:
        try:
            # Process the uploaded Excel file
            df = pd.read_excel(uploaded_file)
            
            # Filter data for the specific part number and customer
            filtered_df = df[(df['Part Number'] == part_number) & (df['Customer'] == customer)]
            
            if filtered_df.empty:
                st.error(f"No data found for Part Number {part_number} and Customer {customer}")
            else:
                # Calculate total sales volume for the specified number of months
                sales_columns = [col for col in filtered_df.columns if 'Sales' in col]
                recent_sales = sales_columns[-months:]
                total_sales = filtered_df[recent_sales].sum().sum()
                
                # Get part description
                part_description = filtered_df['Description'].iloc[0] if 'Description' in filtered_df.columns else "Description not available"
                
                # Prepare data for the API request
                data_summary = f"""
                Part Number: {part_number}
                Customer: {customer}
                Description: {part_description}
                Total Sales Volume (Last {months} months): {total_sales}
                """
                
                # Format the prompt with user data and predefined instructions
                system_message = f"""
                Act like an expert warehouse manager specializing in logistics and inventory management for large-scale distribution centers. You have over 15 years of experience optimizing warehouse layouts, reducing traffic congestion, and improving operational efficiency, especially for high-volume customers.

                Objective:
                Your task is to analyze the provided data for Part {part_number} associated with {customer}, focusing on the last {months} months of sales volume. Based on this analysis, provide a storage recommendation within the warehouse, keeping traffic flow, shipping frequency, and container type in mind.

                Data Summary:
                {data_summary}

                Warehouse Layout:
                - The warehouse is organized into rows A to E, with each row having 36 racks.
                - Based on the part's sales volume and description, identify the best row for placement.
                - Prioritize rows that allow easy access for high-turnover parts while minimizing traffic congestion.

                Storage Recommendation:
                Provide your recommendation in the following format:
                • Row: [Specify row letter]
                • Rack: [Specify rack numbers]
                • Rack Level: [Specify the level within the rack]

                Explanation:
                - Row: Explain why this row is optimal for the part's turnover rate and overall warehouse efficiency.
                - Rack: Describe why these particular racks are suitable, considering shipping frequency and space requirements.
                - Rack Level: Justify why this rack level is appropriate, focusing on ease of access for picking and efficient handling.

                Final Output:
                Ensure your recommendation is data-driven, using the provided sales volume and part characteristics to make the best possible storage decision. Stick to the format provided and include a clear explanation for each choice.
                Only display [Storage Recommendation:] and [Explanation:]
                """

                # Make the OpenAI API request
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a warehouse layout optimization assistant."},
                        {"role": "user", "content": system_message},
                    ]
                )

                # Display the formatted response
                api_response = response.choices[0].message.content
                st.subheader("Part Location Answer:")
                st.write(api_response)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
