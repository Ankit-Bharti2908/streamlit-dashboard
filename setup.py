import os
import shutil

# Create necessary directories
print("Setting up directory structure...")
os.makedirs("data", exist_ok=True)

# Copy source files to data directory
source_files = [
    "tasks.csv", 
    "projects.csv", 
    "team_members.csv", 
    "content_types.csv", 
    "project_timelines.md"
]

print("Copying data files...")
for file in source_files:
    if os.path.exists(file):
        shutil.copy(file, os.path.join("data", file))
        print(f"  - Copied {file} to data directory")
    else:
        print(f"  - Warning: Source file {file} not found")

print("\nSetup complete! Run the dashboard with: streamlit run app.py")