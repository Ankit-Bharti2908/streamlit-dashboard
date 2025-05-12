import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import re
import markdown

# Page configuration
st.set_page_config(page_title="ATS Homekraft Marketing Dashboard", 
                   page_icon="📊", 
                   layout="wide")

# Function to load data
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return pd.DataFrame()

# Load all required data
def load_all_data():
    tasks = load_data("data/tasks.csv")
    projects = load_data("data/projects.csv")
    team_members = load_data("data/team_members.csv")
    content_types = load_data("data/content_types.csv")
    
    # Convert date columns to datetime
    if not tasks.empty:
        date_columns = ['date', 'assigned_on', 'delivered_on']
        for col in date_columns:
            if col in tasks.columns:
                tasks[col] = pd.to_datetime(tasks[col], format='mixed')
    
    if not projects.empty:
        for col in ['start_date', 'end_date']:
            if col in projects.columns:
                projects[col] = pd.to_datetime(projects[col],format='mixed')
    
    return tasks, projects, team_members, content_types

# Function to load project timelines markdown
@st.cache_data
def load_project_timelines():
    try:
        with open("data/project_timelines.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Project timelines file not found"

# Apply custom CSS
def apply_custom_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2563EB;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-left: 4px solid #2563EB;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #4B5563;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1F2937;
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .table-wrapper {
        border-radius: 0.5rem;
        overflow: auto;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Create metrics cards
def create_metrics_row(tasks_df):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Tasks</div>
                <div class="metric-value">{len(tasks_df)}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        completed_tasks = tasks_df[tasks_df['update_status'].isin(['completed', 'sent'])]
        completion_rate = len(completed_tasks) / len(tasks_df) * 100 if len(tasks_df) > 0 else 0
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Completion Rate</div>
                <div class="metric-value">{completion_rate:.1f}%</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        avg_completion_days = tasks_df['completion_days'].mean()
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Avg. Completion Days</div>
                <div class="metric-value">{avg_completion_days:.1f}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        projects_count = tasks_df['project'].nunique()
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Active Projects</div>
                <div class="metric-value">{projects_count}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Monthly task volume chart
def plot_monthly_task_volume(tasks_df):
    if tasks_df.empty:
        st.warning("No data available for plotting")
        return
    
    # Create month column
    tasks_df['month'] = tasks_df['date'].dt.strftime('%b %Y')
    
    # Group by month and project
    monthly_data = tasks_df.groupby(['month', 'project']).size().reset_index(name='count')
    
    # Sort by date
    month_order = pd.Series(tasks_df['date'].dt.to_period('M').unique()).sort_values().astype(str)
    monthly_data['month_sorted'] = monthly_data['month'].astype('category').cat.set_categories(month_order)
    monthly_data = monthly_data.sort_values('month_sorted')
    
    # Create bar chart
    fig = px.bar(monthly_data, x='month', y='count', color='project',
                 title='Monthly Task Volume by Project',
                 labels={'count': 'Number of Tasks', 'month': 'Month', 'project': 'Project'},
                 height=500)
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="",
        yaxis_title="Number of Tasks",
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Task assignment pie chart
def plot_task_assignment(tasks_df):
    if tasks_df.empty:
        st.warning("No data available for plotting")
        return
    
    # Create pie charts for assigned by and assigned to
    col1, col2 = st.columns(2)
    
    with col1:
        assigned_by_data = tasks_df['assigned_by'].value_counts().reset_index()
        assigned_by_data.columns = ['Assigned By', 'Count']
        
        fig = px.pie(assigned_by_data, values='Count', names='Assigned By', 
                     title='Task Assignment Distribution',
                     hole=0.4)
        
        fig.update_layout(
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        assigned_to_data = tasks_df['assigned_to'].value_counts().reset_index()
        assigned_to_data.columns = ['Assigned To', 'Count']
        
        fig = px.pie(assigned_to_data, values='Count', names='Assigned To',
                     title='Task Execution Distribution',
                     hole=0.4)
        
        fig.update_layout(
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Task completion time chart
def plot_task_completion_time(tasks_df, content_types_df):
    if tasks_df.empty:
        st.warning("No data available for plotting")
        return
    
    # Calculate completion categories
    tasks_df['completion_category'] = pd.cut(
        tasks_df['completion_days'],
        bins=[-0.1, 0, 3, 7, float('inf')],
        labels=['Same Day', '1-3 Days', '4-7 Days', '7+ Days']
    )
    
    # Group by content type and completion category
    completion_data = tasks_df.groupby(['content_type', 'completion_category']).size().reset_index(name='count')
    
    # Pivot the data
    pivot_data = completion_data.pivot(index='content_type', columns='completion_category', values='count').fillna(0)
    
    # Reset index to make content_type a column
    pivot_data = pivot_data.reset_index()
    
    # Make sure all categories exist
    for cat in ['Same Day', '1-3 Days', '4-7 Days', '7+ Days']:
        if cat not in pivot_data.columns:
            pivot_data[cat] = 0
    
    # Create stacked bar chart
    fig = px.bar(pivot_data, x='content_type', y=['Same Day', '1-3 Days', '4-7 Days', '7+ Days'],
                 title='Task Completion Time by Content Type',
                 labels={'content_type': 'Content Type', 'value': 'Number of Tasks', 'variable': 'Completion Time'},
                 height=500)
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="",
        yaxis_title="Number of Tasks",
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Content type distribution by project
def plot_content_type_by_project(tasks_df):
    if tasks_df.empty:
        st.warning("No data available for plotting")
        return
    
    # Group by project and content type
    content_data = tasks_df.groupby(['project', 'content_type']).size().reset_index(name='count')
    
    # Create grouped bar chart
    fig = px.bar(content_data, x='project', y='count', color='content_type',
                 title='Content Type Distribution by Project',
                 labels={'count': 'Number of Tasks', 'project': 'Project', 'content_type': 'Content Type'},
                 height=500)
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="",
        yaxis_title="Number of Tasks",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Efficiency trend line chart
def plot_efficiency_trend(tasks_df):
    if tasks_df.empty:
        st.warning("No data available for plotting")
        return
    
    # Create quarter column
    tasks_df['quarter'] = tasks_df['date'].dt.to_period('Q').astype(str)
    
    # Group by quarter
    quarterly_data = tasks_df.groupby('quarter')['completion_days'].mean().reset_index()
    
    # Sort by quarter
    quarterly_data = quarterly_data.sort_values('quarter')
    
    # Create line chart
    fig = px.line(quarterly_data, x='quarter', y='completion_days',
                  title='Efficiency Improvement Over Time',
                  labels={'completion_days': 'Avg. Days to Complete', 'quarter': 'Quarter'},
                  height=400)
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Avg. Days to Complete"
    )
    
    # Add markers to the line
    fig.update_traces(mode='lines+markers', marker=dict(size=10))
    
    st.plotly_chart(fig, use_container_width=True)

# Display tasks table with filters
def display_tasks_table(tasks_df, projects_df, team_members_df):
    if tasks_df.empty:
        st.warning("No task data available")
        return
    
    st.markdown('<div class="sub-header">Task Details</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Project filter
        project_options = ["All"] + sorted(tasks_df['project'].unique().tolist())
        selected_project = st.selectbox("Project", project_options)
    
    with col2:
        # Content type filter
        content_options = ["All"] + sorted(tasks_df['content_type'].unique().tolist())
        selected_content = st.selectbox("Content Type", content_options)
    
    with col3:
        # Assigned to filter
        assignee_options = ["All"] + sorted(tasks_df['assigned_to'].unique().tolist())
        selected_assignee = st.selectbox("Assigned To", assignee_options)
    
    with col4:
        # Status filter
        status_options = ["All"] + sorted(tasks_df['update_status'].unique().tolist())
        selected_status = st.selectbox("Status", status_options)
    
    # Apply filters
    filtered_df = tasks_df.copy()
    
    if selected_project != "All":
        filtered_df = filtered_df[filtered_df['project'] == selected_project]
    
    if selected_content != "All":
        filtered_df = filtered_df[filtered_df['content_type'] == selected_content]
    
    if selected_assignee != "All":
        filtered_df = filtered_df[filtered_df['assigned_to'] == selected_assignee]
    
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df['update_status'] == selected_status]
    
    # Date range filter
    col1, col2 = st.columns(2)
    
    with col1:
        min_date = tasks_df['date'].min().date()
        max_date = tasks_df['date'].max().date()
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & 
                              (filtered_df['date'].dt.date <= end_date)]
    
    # Display filtered tasks
    st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)
    st.dataframe(
        filtered_df[['task_id', 'date', 'task_name', 'project', 'content_type', 
                   'assigned_by', 'assigned_to', 'update_status', 'completion_days']],
        use_container_width=True,
        column_config={
            "task_id": st.column_config.NumberColumn("ID", format="%d"),
            "date": "Date",
            "task_name": "Task Name",
            "project": "Project",
            "content_type": "Content Type",
            "assigned_by": "Assigned By",
            "assigned_to": "Assigned To",
            "update_status": "Status",
            "completion_days": st.column_config.NumberColumn("Days to Complete", format="%d")
        },
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write(f"Showing {len(filtered_df)} of {len(tasks_df)} tasks")

# Display task details
def display_task_details(tasks_df, task_id):
    if tasks_df.empty:
        st.warning("No task data available")
        return
    
    task = tasks_df[tasks_df['task_id'] == task_id]
    
    if task.empty:
        st.error(f"Task ID {task_id} not found")
        return
    
    task = task.iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {task['task_name']}")
        st.markdown(f"**Project:** {task['project']}")
        st.markdown(f"**Content Type:** {task['content_type']}")
        st.markdown(f"**Scope:** {task['work_scope']}")
    
    with col2:
        st.markdown(f"**Assigned By:** {task['assigned_by']}")
        st.markdown(f"**Assigned To:** {task['assigned_to']}")
        st.markdown(f"**Status:** {task['update_status']}")
        
        if not pd.isna(task['delivered_on']):
            days = task['completion_days']
            completion_msg = f"**Completed in:** {days} day{'s' if days != 1 else ''}"
            st.markdown(completion_msg)
    
    st.markdown("---")

# Display project timeline
def display_project_timeline(project_timelines):
    st.markdown('<div class="sub-header">Project Timelines</div>', unsafe_allow_html=True)
    
    # Display the markdown content
    st.markdown(project_timelines)

# CSV viewer tab
def display_csv_viewer(tasks_df, projects_df, team_members_df, content_types_df):
    st.markdown('<div class="sub-header">Data Viewer</div>', unsafe_allow_html=True)
    
    # File selector
    file_options = {
        "Tasks": tasks_df,
        "Projects": projects_df,
        "Team Members": team_members_df,
        "Content Types": content_types_df
    }
    
    selected_file = st.selectbox("Select File to View", list(file_options.keys()))
    
    # Display selected file
    st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)
    st.dataframe(file_options[selected_file], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download button
    csv = file_options[selected_file].to_csv(index=False)
    st.download_button(
        label=f"Download {selected_file} CSV",
        data=csv,
        file_name=f"{selected_file.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

# Main dashboard
def main():
    # Load data
    tasks_df, projects_df, team_members_df, content_types_df = load_all_data()
    project_timelines = load_project_timelines()
    
    # Apply custom styling
    apply_custom_css()
    
    # Dashboard header
    st.markdown('<div class="main-header">ATS Homekraft Marketing Task Dashboard</div>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Task Explorer", "Project Timelines", "Raw Data", "About"])
    
    # Dashboard tab
    with tab1:
        # Metrics
        create_metrics_row(tasks_df)
        
        # Date filter for charts
        min_date = tasks_df['date'].min().date()
        max_date = tasks_df['date'].max().date()
        
        col1, col2 = st.columns(2)
        with col1:
            chart_start_date = st.date_input("Chart Start Date", min_date, key='chart_start', 
                                             min_value=min_date, max_value=max_date)
        with col2:
            chart_end_date = st.date_input("Chart End Date", max_date, key='chart_end',
                                          min_value=min_date, max_value=max_date)
        
        # Filter data for charts
        chart_data = tasks_df[(tasks_df['date'].dt.date >= chart_start_date) & 
                             (tasks_df['date'].dt.date <= chart_end_date)]
        
        # Monthly task volume
        st.markdown('<div class="card">', unsafe_allow_html=True)
        plot_monthly_task_volume(chart_data)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Task assignment and execution
        st.markdown('<div class="card">', unsafe_allow_html=True)
        plot_task_assignment(chart_data)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Task completion time
        st.markdown('<div class="card">', unsafe_allow_html=True)
        plot_task_completion_time(chart_data, content_types_df)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content type by project
        st.markdown('<div class="card">', unsafe_allow_html=True)
        plot_content_type_by_project(chart_data)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Efficiency trend
        st.markdown('<div class="card">', unsafe_allow_html=True)
        plot_efficiency_trend(chart_data)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Task Explorer tab
    with tab2:
        # Task details view
        display_tasks_table(tasks_df, projects_df, team_members_df)
        
        # Individual task view
        st.markdown('<div class="sub-header">Task Detail View</div>', unsafe_allow_html=True)
        task_id = st.number_input("Enter Task ID", min_value=1, max_value=int(tasks_df['task_id'].max()), value=1)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        display_task_details(tasks_df, task_id)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Project Timelines tab
    with tab3:
        display_project_timeline(project_timelines)
    
    # Raw Data tab
    with tab4:
        display_csv_viewer(tasks_df, projects_df, team_members_df, content_types_df)
    
    # About tab
    with tab5:
        st.markdown("""
        ## About This Dashboard
        
        This dashboard provides comprehensive analytics for ATS Homekraft's marketing and creative tasks from July 2024 to April 2025.
        
        ### Data Sources
        - **tasks.csv**: Contains detailed information about 156 marketing tasks
        - **projects.csv**: Information about various real estate projects
        - **team_members.csv**: Details about team members and their roles
        - **content_types.csv**: Categorization of different marketing content types
        
        ### Key Features
        - **Task Analytics**: Visualize task distribution, completion rates, and efficiency metrics
        - **Project Timeline**: View detailed project development phases and milestones
        - **Task Explorer**: Search, filter, and examine individual task details
        - **Raw Data Viewer**: Access and download the underlying dataset
        
        ### Dashboard Usage
        - Use the filters to narrow down tasks by project, assignee, content type, or date range
        - Hover over charts for detailed information
        - Download CSV files for further analysis in other tools
        
        ### Contact
        For questions or issues regarding this dashboard, please contact the marketing department.
        """)

# Create data directory and files if they don't exist
def setup_data_directory():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Check if files exist, if not create them
    files_to_check = [
        ('data/tasks.csv', 'tasks.csv'),
        ('data/projects.csv', 'projects.csv'),
        ('data/team_members.csv', 'team_members.csv'),
        ('data/content_types.csv', 'content_types.csv'),
        ('data/project_timelines.md', 'project_timelines.md')
    ]
    
    for dest_path, source_name in files_to_check:
        if not os.path.exists(dest_path):
            # In a real environment, this would copy from the drive location
            # For this example, we'll assume the files are in the same directory as the script
            if os.path.exists(source_name):
                import shutil
                shutil.copy(source_name, dest_path)
            else:
                # Create empty file as placeholder
                with open(dest_path, 'w') as f:
                    if dest_path.endswith('.csv'):
                        f.write("# Empty placeholder file\n")
                    else:
                        f.write("# Empty placeholder file\n")

if __name__ == "__main__":
    # Setup data directory and files
    setup_data_directory()
    
    # Run the app
    main()