# Streamlit search app

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


# Custom CSS to increase text size throughout the app
st.markdown("""
<style>
    /* Increase font size for the entire app */
    html, body, [class*="st-"] {
        font-size: 20px !important;
    }
   
    /* Increase table text size */
    table {
        font-size: 18px !important;
    }
   
    /* Adjust header sizes */
    h1 {
        font-size: 30px !important;
    }
    h2 {
        font-size: 26px !important;
    }
    h3 {
        font-size: 23px !important;
    }
   
    /* Make input fields larger */
    .stTextInput input {
        font-size: 16px !important;
    }
   
    /* Make buttons text larger */
    .stButton button {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("Reference Search")
st.header("Journal publications and articles", divider='rainbow')
st.markdown("Welcome to our app where you can find links to all things about careers guidance")


# Read reference data
ref_url = "https://docs.google.com/spreadsheets/d/1sUCaZ22aiXJl8WdMYaUCi45ryYt1g_i0jm6k7IcS9ZQ/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)
ref_data = conn.read(spreadsheet=ref_url, usecols=[2, 3, 5, 6, 7])

# Read book data - Add your second Google Sheet URL here
book_url = "https://docs.google.com/spreadsheets/d/1LHJ_1FK4fyZ-jvy_qN4v8kXgGu7Vm2XiHvQVkVoHAdM/edit?usp=sharing"  
book_data = conn.read(spreadsheet=book_url, usecols=[0, 1, 2, 3, 4, 7])  # Adjust column indices as needed for your book sheet


#input section
# Create three input boxes for keywords
col1, col2 = st.columns(2)
with col1:
    keyword1 = st.text_input("Keyword/Phrase 1")
with col2:
    keyword2 = st.text_input("Keyword/Phrase 2")


# Search
search_button = st.button("Search References and Books")


ref_search_columns = ["Title", "People/identity focus1", "People/identity focus2",
                "Outcome", "Practices", "Description"]

book_search_columns = ["Title", "Key audience(s)", "Key Groups/themes"]  # These columns will be used for searching


# Function to filter the dataframe based on keywords
def filter_references(df, keywords, columns):
    """Filter dataframe rows that contain any of the keywords in specified columns"""
    if not any(keywords):  # If no keywords provided
        return df
   
    # Initialize mask as all False
    mask = pd.Series(False, index=df.index)
   
    # For each keyword and column
    for keyword in keywords:
        if not keyword:  # Skip empty keywords
            continue
           
        for col in columns:
            if col in df.columns:
                # Update mask for rows where the column contains the keyword (case insensitive)
                mask = mask | df[col].astype(str).str.contains(keyword, case=False, na=False)
   
    return df[mask]


# Function to make link clickable with custom text
def make_clickable_link_text(url):
    """Convert URL to clickable HTML link with text 'Link' that opens in a new tab"""
    if pd.isna(url) or not str(url).startswith('http'):
        return ""
    return f'<a href="{url}" target="_blank">Link</a>'


# Get the link column names
ref_link_column = ref_data.columns[4]  # The 5th column (index 4) from usecols=[2, 3, 5, 6, 7]
book_link_column = book_data.columns[5]  # The 5th column from usecols=[0,1,2,3,4,7]


# Create a formatted version of the dataframe for display
def get_display_dataframe(df, link_column):
    """Prepare dataframe for display with formatted links"""
    display_df = df.copy()
    # Convert the URLs to HTML links with "Link" text
    display_df[link_column] = display_df[link_column].apply(make_clickable_link_text)
    return display_df


# Function to select and rename columns for book display
def prepare_book_display_df(df):
    """Select only Title, Name, Year, and Link columns from book dataframe"""
    # Assuming column structure based on usecols=[0, 1, 2, 3, 4, 7]
    # Where Title is at index 0, Name is at index 1, Year is at index 2, and Link is at index 5
    display_cols = [0, 1, 2, 5]  # Indices of the columns we want to keep
    
    # Select only the columns we want to display
    display_df = df.iloc[:, display_cols].copy()
    
    # Rename the columns to our desired names
    display_df.columns = ["Title", "Name", "Year", "Link"]
    
    # Format the link column
    display_df["Link"] = display_df["Link"].apply(make_clickable_link_text)
    
    return display_df


# Create a scrollable table with CSS
def display_scrollable_table(df, height="400px"):
    """Display a scrollable HTML table with the given height and larger text"""
    # Generate the HTML table
    html_table = df.to_html(escape=False, index=False)
   
    # Add CSS for scrollable table with larger text
    scrollable_table = f"""
    <div style="height: {height}; overflow-y: auto; margin-bottom: 20px;">
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 18px;
            }}
            th {{
                background-color: #f1f1f1;
                padding: 12px 15px;
                text-align: left;
                font-weight: bold;
            }}
            td {{
                padding: 12px 15px;
                text-align: left;
            }}
            tr:nth-child(even) {{
                background-color: #f8f8f8;
            }}
            a {{
                color: #1e88e5;
                text-decoration: none;
                font-weight: bold;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
        {html_table}
    </div>
    """
   
    # Display the scrollable table
    st.write(scrollable_table, unsafe_allow_html=True)


# Process search when button is clicked
if search_button:
    # Gather non-empty keywords
    keywords = [k for k in [keyword1, keyword2] if k]
   
    if not keywords:
        st.warning("Please enter at least one keyword to search.")
    else:
        # Filter the reference dataframe
        filtered_ref_data = filter_references(ref_data, keywords, ref_search_columns)
        
        # Filter the book dataframe
        filtered_book_data = filter_references(book_data, keywords, book_search_columns)
       
        # Display References section
        st.subheader("References")
        if len(filtered_ref_data) == 0:
            st.info(f"No references found containing: {', '.join(keywords)}")
            # If no results, show empty table
            display_scrollable_table(pd.DataFrame(columns=ref_data.columns))
        else:
            st.success(f"Found {len(filtered_ref_data)} references matching your search.")
            
            # Format the filtered data with clickable links that say "Link"
            display_ref_data = get_display_dataframe(filtered_ref_data, ref_link_column)
            
            # Display scrollable table
            display_scrollable_table(display_ref_data)
            
            # Download option for results
            csv = filtered_ref_data.to_csv(index=False)
            st.download_button(
                label="Download Reference Results as CSV",
                data=csv,
                file_name="reference_search_results.csv",
                mime="text/csv"
            )
        
        # Add space between tables
        st.markdown("<br><br>", unsafe_allow_html=True)
            
        # Display Books section
        st.subheader("Books")
        if len(filtered_book_data) == 0:
            st.info(f"No books found containing: {', '.join(keywords)}")
            # If no results, show empty table with only the desired columns
            display_scrollable_table(pd.DataFrame(columns=["Title", "Name", "Year", "Link"]))
        else:
            st.success(f"Found {len(filtered_book_data)} books matching your search.")
            
            # Prepare the book data for display with only the specified columns
            display_book_data = prepare_book_display_df(filtered_book_data)
            
            # Display scrollable table
            display_scrollable_table(display_book_data)
            
            # Download option for results
            # Note: We'll include all columns in the CSV download
            csv = filtered_book_data.to_csv(index=False)
            st.download_button(
                label="Download Book Results as CSV",
                data=csv,
                file_name="book_search_results.csv",
                mime="text/csv"
            )
else:
    # Show message before searching
    st.info("Enter keywords above and click 'Search References and Books' to find relevant publications.")
   
    # Display initial scrollable tables with sample data
    st.subheader("Sample References")
    initial_ref_display_data = get_display_dataframe(ref_data.head(5), ref_link_column)
    display_scrollable_table(initial_ref_display_data)
    
    # Add space between tables
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.subheader("Sample Books")
    # Prepare the sample book data with only the specified columns
    initial_book_display_data = prepare_book_display_df(book_data.head(5))
    display_scrollable_table(initial_book_display_data)
