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
st.header("Based on sales volume -and all the data provided-, where should a part be stored")

# Load and display the image (if available)
# image = Image.open("warehouse_image.jpg")  # Uncomment if using an image
# st.image(image, caption="Warehouse Management", use_column_width=True)

# Initialize session state for storing combined Excel data
if "combined_data" not in st.session_state:
    st.session_state.combined_data = None  # Initialize it to None

# Step 1: Excel File Uploader
uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

# Step 2: Text Input Fields for Parameters
part_number = st.text_input("Enter Part Number:")
customer = st.text_input("Enter Customer Name:")
months = st.number_input("Last X Months of Sales Volume:", min_value=1, value=3, step=1)

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
            system_message = f"""
            Act like an expert warehouse manager specializing in logistics and space optimization for high-traffic distribution centers. You have been optimizing warehouse layouts and improving picking efficiency for over 15 years, working with top-tier manufacturers and distributors. Your expertise involves reducing traffic congestion, optimizing for shipping frequency, and ensuring easy accessibility of high-turnover inventory.

Objective: Analyze the provided Excel data for Part {part_number} belonging to {customer}, focusing on the last {months} months of sales volume. Based on this, recommend optimal storage placement in the warehouse, ensuring efficient handling and accessibility.

Step-by-Step Breakdown:
Data Extraction:

Open the 'Sept_24_2024 Sales Report' sheet within the provided Excel document.
Find sales data for {part_number} associated with {customer}.
For the last 3 months (columns: 'SEP-24', 'AUG-24', and 'JUL-24'), add up the sales volumes to calculate the total volume over these months.
Part Description:

Extract the description of {part_number} from the spreadsheet to understand the nature of the item (e.g., size, handling requirements, weight).
Volume-Based Layout Placement:

Review the warehouse layout, which includes rows labeled A to E, with each row containing 36 racks.
Based on the sales volume data, determine which row is most suitable for this part. High-volume parts should be placed in easily accessible rows to minimize traffic congestion and reduce travel time for pickers.
Container Type Grouping:

If available, check the container type for the part and ensure it is grouped with similar container types for better stacking and skid loading efficiency.
Storage Recommendations:

Provide your storage recommendation in the following format:
• Row: [Specify row letter]
• Rack: [Specify rack numbers]
• Rack Level: [Specify the level within the rack]

Explanation:

Row: Briefly explain why this row is suitable based on the part's turnover rate and the need to avoid warehouse congestion.
Rack: Justify why these racks were chosen considering shipping frequency and available space.
Rack Level: Explain why the specified level within the rack is appropriate for the part’s accessibility and handling requirements, ensuring efficient picking and packing.
Final Step:

Ensure the recommendation is based solely on the provided data and is tailored to warehouse layout constraints, shipping efficiency, and part volume. Use the description and sales data to drive your decision.
Take a deep breath and work on this problem step-by-step.
            """


            # Step 6: Make the OpenAI API request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Make sure to use a valid model
                messages=[
                    {"role": "system", "content": "You are a warehouse layout optimization assistant."},
                    {"role": "user", "content": system_message},
                ]
            )

            # Step 7: Display the formatted response
            api_response = response.choices[0].message.content
            st.subheader("Part Location Answer:")
            st.write(api_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
