import streamlit as st
import pandas as pd
from openai import OpenAI
from PIL import Image

# Fetch the OpenAI API key from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]

# Initialize the OpenAI client using the API key from Streamlit secrets
client = OpenAI(api_key=api_key)

# Title of the Streamlit app
st.title("Warehouse Management Assistant")
st.header("Based on shipping volume -and all the data provided-, where should a part be stored")

# Load and display the image (if available)
# image = Image.open("warehouse_image.jpg")  # Uncomment if using an image
# st.image(image, caption="Warehouse Management", use_column_width=True)

# Step 1: Excel File Uploader
uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

# Step 2: Text Input Fields for Parameters
part_number = st.text_input("Enter Part Number:")
customer = st.text_input("Enter Customer Name:")
months = st.number_input("Enter Number of Months of Shipping Volume:", min_value=1, value=3, step=1)

# Step 3: Submit Button to trigger the OpenAI API call
if st.button("Submit"):
    if not uploaded_files or not part_number or not customer:
        st.error("Please upload the Excel files and fill in all input fields before submitting.")
    else:
        try:
            # Process the uploaded Excel files
            excel_data = []
            for file in uploaded_files:
                df = pd.read_excel(file)
                excel_data.append(df)
            combined_data = pd.concat(excel_data, ignore_index=True)

            # Step 5: Format the prompt with user data and predefined instructions
            system_message = (
                f"We want to layout by the top customers based on volume. "
                f"Keep these top customers separated in separate areas, this will prevent traffic congestion in the warehouse. "
                f"Layout by container type, keeping the same containers together so they stack better on skids. "
                f"In the current layout, the warehouse is divided into rows (A to E), with each row having 36 racks. "
                f"Use all the data provided, to determine where Part {part_number} belonging to {customer} should be stored "
                f"based on the last {months} months of shipping volume."
            )

            # Step 6: Make the OpenAI API request
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Make sure to use a valid model
                messages=[
                    {"role": "system", "content": "You are a warehouse layout optimization assistant."},
                    {"role": "user", "content": system_message},
                ]
            )

            # Step 7: Display the formatted response
            api_response = response['choices'][0]['message']['content']
            st.subheader("API Response:")
            st.write(api_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Instructions for deployment
st.info("MULTIFACTOR AI - for NIFCO")

# Add a chat box at the bottom for additional questions
st.subheader("Ask additional questions about the data")

# Chat box input
additional_question = st.text_input("Ask additional questions about the data:")

# Submit button for the chat box
if st.button("Submit Question"):
    if additional_question:
        try:
            # Format the prompt for the chat question
            chat_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a warehouse management assistant."},
                    {"role": "user", "content": additional_question}
                ],
                max_tokens=500
            )
            
            # Display the response from the chat box
            chat_api_response = chat_response.choices[0].message.content
            st.subheader("Response to Your Question:")
            st.write(chat_api_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please ask a question before submitting.")
