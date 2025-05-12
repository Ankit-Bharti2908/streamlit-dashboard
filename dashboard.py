import streamlit as st
import os
import shutil
import pandas as pd

# Create data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# Function to save CSV files to data directory
def save_csv_file(content, filename):
    with open(os.path.join("data", filename), "w") as f:
        f.write(content)

# Function to save markdown files to data directory
def save_markdown_file(content, filename):
    with open(os.path.join("data", filename), "w") as f:
        f.write(content)

# Copy the streamlit app to the main directory
def copy_streamlit_app():
    shutil.copy("streamlit_app.py", "app.py")

# Extract CSV content from code blocks in .md files
def extract_csv_from_markdown(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    
    # Extract content between ```csv and ``` tags
    import re
    pattern = r"```csv\n(.*?)```"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1)
    else:
        return None

# Setup data files
def setup_data_files():
    # Save tasks.csv
    try:
        tasks_csv = extract_csv_from_markdown("tasks.csv (Complete Version).md")
        if tasks_csv:
            save_csv_file(tasks_csv, "tasks.csv")
            st.success("✅ tasks.csv saved successfully")
        else:
            st.error("❌ Failed to extract tasks.csv content")
    except Exception as e:
        st.error(f"❌ Error processing tasks.csv: {str(e)}")
    
    # Save project_timelines.md
    try:
        with open("project_timelines.md (Enhanced Version).md", "r") as f:
            project_timelines = f.read()
        save_markdown_file(project_timelines, "project_timelines.md")
        st.success("✅ project_timelines.md saved successfully")
    except Exception as e:
        st.error(f"❌ Error processing project_timelines.md: {str(e)}")
    
    # Save projects.csv
    try:
        projects_csv = extract_csv_from_markdown("projects.csv.md")
        if projects_csv:
            save_csv_file(projects_csv, "projects.csv")
            st.success("✅ projects.csv saved successfully")
        else:
            st.error("❌ Failed to extract projects.csv content")
    except Exception as e:
        st.error(f"❌ Error processing projects.csv: {str(e)}")
    
    # Save content_types.csv
    try:
        with open("content_types.csv (Detailed Version)", "r") as f:
            content_types_csv = f.read()
        save_csv_file(content_types_csv, "content_types.csv")
        st.success("✅ content_types.csv saved successfully")
    except Exception as e:
        st.error(f"❌ Error processing content_types.csv: {str(e)}")
    
    # Save team_members.csv
    try:
        with open("team_members.csv", "r") as f:
            team_members_csv = f.read()
        save_csv_file(team_members_csv, "team_members.csv")
        st.success("✅ team_members.csv saved successfully")
    except Exception as e:
        st.error(f"❌ Error processing team_members.csv: {str(e)}")
    
    # Save messages.csv
    try:
        with open("messages.csv (Complete Version)", "r") as f:
            messages_csv = f.read()
        save_csv_file(messages_csv, "messages.csv")
        st.success("✅ messages.csv saved successfully")
    except Exception as e:
        st.error(f"❌ Error processing messages.csv: {str(e)}")

# Create images directory and placeholder images
def setup_images():
    if not os.path.exists("images"):
        os.makedirs("images")
        st.success("✅ Created images directory")
    
    # Create placeholder image notes
    image_note = """# Image Placeholder
This directory will contain dashboard screenshots for the README documentation.
"""
    with open(os.path.join("images", "README.md"), "w") as f:
        f.write(image_note)
    st.success("✅ Created images placeholder note")

# Main function
def main():
    st.title("ATS Homekraft Marketing Dashboard Setup")
    
    st.markdown("""
    This setup script will:
    1. Create necessary data directories
    2. Extract and prepare all data files
    3. Copy the streamlit app to app.py
    4. Create placeholder images directory
    
    After setup, you can run the dashboard with:
    ```
    streamlit run app.py
    ```
    """)
    
    if st.button("Setup Dashboard", type="primary"):
        with st.spinner("Setting up dashboard files..."):
            setup_data_files()
            copy_streamlit_app()
            setup_images()
            st.success("Dashboard setup complete!")
        
        st.balloons()
        
        # Display sample data
        st.subheader("Sample Data")
        
        try:
            # Show tasks
            tasks = pd.read_csv("data/tasks.csv")
            st.write("Tasks Sample (first 5 rows):")
            st.dataframe(tasks.head())
            
            # Show projects
            projects = pd.read_csv("data/projects.csv")
            st.write("Projects Sample:")
            st.dataframe(projects)
            
            # Show team members
            team_members = pd.read_csv("data/team_members.csv")
            st.write("Team Members Sample:")
            st.dataframe(team_members)
            
            # Show messages sample
            messages = pd.read_csv("data/messages.csv")
            st.write("Messages Sample (first 5 rows):")
            st.dataframe(messages.head())
            
            # Show content types
            content_types = pd.read_csv("data/content_types.csv")
            st.write("Content Types Sample:")
            st.dataframe(content_types)
        except Exception as e:
            st.error(f"Error displaying sample data: {str(e)}")
        
        st.success("You can now run 'streamlit run app.py' to start the dashboard!")

if __name__ == "__main__":
    main()