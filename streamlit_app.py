import streamlit as st
import pandas as pd
from openai import OpenAI

# Fetch the OpenAI API key from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]

# Initialize the OpenAI client using the API key from Streamlit secrets
client = OpenAI(api_key=api_key)

# Title of the Streamlit app
st.title("Warehouse Management Assistant")

# Step 1: Excel File Uploader
uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

# Step 2: Text Input Fields for Parameters
part_number = st.text_input("Enter Part Number:")
customer = st.text_input("Enter Customer Name:")
months = st.number_input("Enter Number of Months of Shipping Volume:", min_value=1, value=3, step=1)

# Display the dynamic prompt being generated
prompt_template = (
    "Based on all the data provided, where should part {part} belonging to {customer} be stored "
    "based on the last {months} months of shipping volume? "
)

full_prompt = prompt_template.format(part=part_number, customer=customer, months=months)
st.write(f"Use Case 1: {full_prompt}")

# Step 3: Submit Button to trigger the OpenAI API call
if st.button("Submit"):
    # Check if files are uploaded and inputs are provided
    if not uploaded_files or not part_number or not customer:
        st.error("Please upload the Excel files and fill in all input fields before submitting.")
    else:
        try:
            # Step 4: Process the uploaded Excel files
            excel_data = []
            for file in uploaded_files:
                df = pd.read_excel(file)
                excel_data.append(df)
            combined_data = pd.concat(excel_data, ignore_index=True)
            
            # Step 5: Format the prompt with user data and predefined instructions
            system_message = f"""
            We want to layout by the top customers based on volume. 
            Keep these top customers separated in separate areas, this will prevent traffic congestion in the warehouse. 
            Layout by container type, keeping the same containers together so they stack better on skids. 
            In the current layout, the warehouse is divided into rows (A to E), with each row having 36 racks. 
            Use all the data provided, to determine where Part {part_number} belonging to {customer} should be stored 
            based on the last {months} months of shipping volume. 
            The answer should look like this example: 
                •   Row: C
                Row C is designated for moderate turnover parts and is ideally positioned near the middle of the warehouse for efficient access.
                •   Rack: Rack 10 to 15
                Since this part is expected to have moderate shipping frequency, we can assign it to Rack 10 to 15 in Row C. This placement allows enough space for storing 50,000 units while keeping it accessible for picking.
                •  Rack Level: Lower to Mid-Level
                The part should be placed on the lower to mid-level shelves of racks 10 to 15 in Row C. This makes the part easily reachable without the need for equipment.
            """
            
            # Step 6: Make the OpenAI API request using ChatCompletion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a warehouse management assistant."},
                    {"role": "user", "content": system_message}
                ],
                max_tokens=500
            )
            
            # Step 7: Display the formatted response
            api_response = response.choices[0].message.content
            st.subheader("API Response:")
            st.write(api_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Step 8: Instructions for deployment
st.info("This app can be deployed on Streamlit Cloud or any other hosting service. "
        "Make sure to set the OPENAI_API_KEY in your environment for secure API access.")
