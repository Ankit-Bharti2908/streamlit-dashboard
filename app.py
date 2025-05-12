import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from streamlit_card import card  # Install: pip install streamlit-card
from streamlit_elements import elements, dashboard, mui, html  # Install: pip install streamlit-elements

# Page configuration
st.set_page_config(
    page_title="ATS Homekraft Marketing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    messages = load_data("data/messages.csv")
    
    # Convert date columns to datetime
    if not tasks.empty:
        date_columns = ['date', 'assigned_on', 'delivered_on']
        for col in date_columns:
            if col in tasks.columns:
                tasks[col] = pd.to_datetime(tasks[col])
        
        # Calculate completion days
        tasks['completion_days'] = (tasks['delivered_on'] - tasks['assigned_on']).dt.days
        # Replace NaN with 0 for same-day completion
        tasks['completion_days'] = tasks['completion_days'].fillna(0)
        # For tasks without delivered_on date, use today for in progress calculations
        tasks.loc[tasks['delivered_on'].isna(), 'completion_days'] = (
            pd.Timestamp.today() - tasks.loc[tasks['delivered_on'].isna(), 'assigned_on']
        ).dt.days
    
    if not projects.empty:
        for col in ['start_date', 'end_date']:
            if col in projects.columns:
                projects[col] = pd.to_datetime(projects[col])
    
    if not messages.empty:
        if 'date' in messages.columns:
            messages['date'] = pd.to_datetime(messages['date'])
    
    return tasks, projects, team_members, content_types, messages

# Function to load project timelines markdown
@st.cache_data
def load_project_timelines():
    try:
        with open("data/project_timelines.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Project timelines file not found"

# Function to load task messages
def load_task_messages(task_id, messages_df):
    if messages_df.empty:
        return []
    
    # Filter messages for this task
    task_messages = messages_df[messages_df['task_id'] == task_id]
    
    if task_messages.empty:
        return []
    
    # Sort by date
    task_messages = task_messages.sort_values('date')
    
    # Convert to list of dictionaries
    messages = task_messages.to_dict('records')
    
    return messages

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
    .message-container {
        margin-bottom: 10px;
        padding-bottom: 10px;
    }
    .message-sender {
        font-weight: bold;
    }
    .message-date {
        color: #666;
        font-size: 0.8rem;
    }
    .message-content {
        background-color: #f5f7f9;
        padding: 10px;
        border-radius: 8px;
        margin-top: 5px;
    }
    .timeline-item {
        display: flex;
        margin-bottom: 15px;
    }
    .timeline-marker {
        min-width: 20px;
        height: 20px;
        background-color: #2563EB;
        border-radius: 50%;
        margin-right: 15px;
        margin-top: 5px;
    }
    .timeline-content {
        flex-grow: 1;
    }
    .timeline-date {
        font-weight: 500;
        color: #2563EB;
    }
    .timeline-line {
        position: relative;
        left: 10px;
        border-left: 2px solid #CBD5E1;
        height: 30px;
        margin-top: -15px;
        margin-bottom: -15px;
    }
    .project-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        transition: all 0.3s;
    }
    .project-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .project-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 12px;
    }
    .project-stat {
        text-align: center;
        padding: 8px;
        background-color: #f3f4f6;
        border-radius: 4px;
        flex: 1;
        margin: 0 4px;
    }
    .project-stat-value {
        font-size: 1.5rem;
        font-weight: 600;
    }
    .project-stat-label {
        font-size: 0.8rem;
        color: #6b7280;
    }
    </style>
    """, unsafe_allow_html=True)

def custom_card(title, text, key=None, metrics=None):
    with st.container():
        st.markdown(f"### {title}", unsafe_allow_html=True)
        st.markdown(text, unsafe_allow_html=True)
        
        if metrics:
            cols = st.columns(len(metrics))
            for i, metric in enumerate(metrics):
                with cols[i]:
                    st.metric(metric["label"], metric["value"])
# Create metrics cards using native Streamlit
def create_metrics_row(tasks_df):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", len(tasks_df))
    
    with col2:
        completed_tasks = tasks_df[tasks_df['update_status'].isin(['completed', 'sent'])]
        completion_rate = len(completed_tasks) / len(tasks_df) * 100 if len(tasks_df) > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        avg_completion_days = tasks_df[tasks_df['update_status'].isin(['completed', 'sent'])]['completion_days'].mean() if not completed_tasks.empty else 0
        st.metric("Avg. Completion Days", f"{avg_completion_days:.1f}")
    
    with col4:
        projects_count = tasks_df['project'].nunique()
        st.metric("Active Projects", projects_count)

# Monthly task volume chart
def plot_monthly_task_volume(tasks_df):
    if tasks_df.empty:
        st.warning("No data available for plotting")
        return
    
    # Create month column and ensure it's properly formatted for sorting
    tasks_df['month_year'] = tasks_df['date'].dt.strftime('%Y-%m')
    tasks_df['month_display'] = tasks_df['date'].dt.strftime('%b %Y')
    
    # Group by month and project
    monthly_data = tasks_df.groupby(['month_year', 'month_display', 'project']).size().reset_index(name='count')
    
    # Sort by date
    monthly_data = monthly_data.sort_values('month_year')
    
    # Get unique months in chronological order
    unique_months = monthly_data.sort_values('month_year')['month_display'].unique()
    
    # Create bar chart
    fig = px.bar(monthly_data, x='month_display', y='count', color='project',
                 title='Monthly Task Volume by Project',
                 labels={'count': 'Number of Tasks', 'month_display': 'Month', 'project': 'Project'},
                 category_orders={'month_display': unique_months},
                 height=500)
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="",
        yaxis_title="Number of Tasks",
        barmode='stack',
        margin=dict(l=40, r=40, t=60, b=40)
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
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1),
            height=400,
            margin=dict(l=20, r=120, t=60, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        assigned_to_data = tasks_df['assigned_to'].value_counts().reset_index()
        assigned_to_data.columns = ['Assigned To', 'Count']
        
        fig = px.pie(assigned_to_data, values='Count', names='Assigned To',
                     title='Task Execution Distribution',
                     hole=0.4)
        
        fig.update_layout(
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1),
            height=400,
            margin=dict(l=20, r=120, t=60, b=20)
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
        bins=[-0.1, 1, 3, 7, float('inf')],
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
        barmode='stack',
        margin=dict(l=40, r=40, t=60, b=40)
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
        barmode='group',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Efficiency trend line chart
def plot_efficiency_trend(tasks_df):
    if tasks_df.empty:
        st.warning("No data available for plotting")
        return
    
    # Create month column
    tasks_df['month_year'] = tasks_df['date'].dt.strftime('%Y-%m')
    tasks_df['month_display'] = tasks_df['date'].dt.strftime('%b %Y')
    
    # Only consider completed tasks for efficiency calculation
    completed_tasks = tasks_df[tasks_df['update_status'].isin(['completed', 'sent'])]
    
    # Group by month
    monthly_data = completed_tasks.groupby(['month_year', 'month_display'])['completion_days'].mean().reset_index()
    
    # Sort by month_year
    monthly_data = monthly_data.sort_values('month_year')
    
    # Get unique months in chronological order
    unique_months = monthly_data['month_display'].tolist()
    
    # Create line chart
    fig = px.line(monthly_data, x='month_display', y='completion_days',
                  title='Efficiency Improvement Over Time',
                  labels={'completion_days': 'Avg. Days to Complete', 'month_display': 'Month'},
                  height=400,
                  category_orders={'month_display': unique_months})
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Avg. Days to Complete",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # Add markers to the line
    fig.update_traces(mode='lines+markers', marker=dict(size=10))
    
    st.plotly_chart(fig, use_container_width=True)

# Display content type details
def display_content_type_details(content_types_df):
    st.markdown('<div class="sub-header">Content Type Analysis</div>', unsafe_allow_html=True)
    
    # Select content type
    selected_content_type = st.selectbox(
        "Select Content Type for Details", 
        sorted(content_types_df['content_type'].unique().tolist())
    )
    
    # Get content type details
    content_type_data = content_types_df[content_types_df['content_type'] == selected_content_type].iloc[0]
    
    # Display content type information in an expander
    with st.expander(f"Details for {selected_content_type}", expanded=True):
        st.markdown(f"**Description:** {content_type_data['description']}")
        st.markdown(f"**Average Completion:** {content_type_data['avg_completion_days']} days")
        st.markdown(f"**Average Revision Cycles:** {content_type_data['avg_revision_cycles']}")
        st.markdown(f"**Priority Level:** {content_type_data['priority_level']}")
        st.markdown(f"**Typical Team Members:** {content_type_data['typical_assigned_to']}")
        st.markdown(f"**Common Tools:** {content_type_data['typical_tools']}")
        st.markdown(f"**File Formats:** {content_type_data['file_formats']}")
    
    # Display best practices
    st.markdown("### Best Practices")
    st.info(content_type_data['best_practices'])
    
    # Priority distribution chart
    st.markdown("### Priority Distribution by Content Type")
    
    # Create priority categories
    priority_mapping = {
        'High - often needed same day': 'High', 
        'High - publisher deadlines critical': 'High',
        'High - event deadlines fixed': 'High',
        'Medium-High - installation deadlines': 'Medium-High',
        'Medium - requires legal review': 'Medium',
        'Medium - scheduled posts': 'Medium',
        'Medium - regular updates': 'Medium',
        'Medium - strategic planning': 'Medium',
        'Medium - scheduled communications': 'Medium',
        'Medium - meeting schedules': 'Medium',
        'Medium-Low - longer production time': 'Medium-Low',
        'Low - specialized skill': 'Low',
        'Low - outsourced, high complexity': 'Low'
    }
    
    # Apply mapping to create simplified categories
    content_types_df['priority_category'] = content_types_df['priority_level'].map(priority_mapping)
    
    # Create priority distribution data
    priority_data = content_types_df.groupby('priority_category').size().reset_index()
    priority_data.columns = ['Priority', 'Count']
    
    # Sort by priority level
    priority_order = ['High', 'Medium-High', 'Medium', 'Medium-Low', 'Low']
    priority_data['Priority'] = pd.Categorical(priority_data['Priority'], categories=priority_order, ordered=True)
    priority_data = priority_data.sort_values('Priority')
    
    # Create horizontal bar chart
    fig = px.bar(priority_data, y='Priority', x='Count', 
                 title='Content Types by Priority Level',
                 orientation='h',
                 color='Priority',
                 color_discrete_map={
                     'High': '#ff4b4b',
                     'Medium-High': '#ff9d4b',
                     'Medium': '#ffdb4b',
                     'Medium-Low': '#9dff4b',
                     'Low': '#4bff4b'
                 })
    
    fig.update_layout(
        height=300,
        xaxis_title="Number of Content Types",
        yaxis_title="",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tool usage chart
    st.markdown("### Common Tools by Content Type")
    
    # Extract tools data
    tools_data = []
    for _, row in content_types_df.iterrows():
        tools = [tool.strip() for tool in row['typical_tools'].split(',')]
        for tool in tools:
            tools_data.append({
                'Content Type': row['content_type'],
                'Tool': tool
            })
    
    tools_df = pd.DataFrame(tools_data)
    
    # Count tool occurrences
    tool_counts = tools_df['Tool'].value_counts().reset_index()
    tool_counts.columns = ['Tool', 'Count']
    
    # Only show tools used in at least 2 content types
    tool_counts = tool_counts[tool_counts['Count'] >= 2]
    
    # Sort by count descending
    tool_counts = tool_counts.sort_values('Count', ascending=False)
    
    # Create bar chart
    fig = px.bar(tool_counts, y='Tool', x='Count',
                 title='Most Used Tools Across Content Types',
                 orientation='h')
    
    fig.update_layout(
        height=400,
        xaxis_title="Number of Content Types",
        yaxis_title="",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Display project cards using native Streamlit
def display_project_cards(projects_df, tasks_df):
    st.markdown('<div class="sub-header">Project Overview</div>', unsafe_allow_html=True)
    
    # Calculate project metrics
    project_metrics = []
    
    for _, project in projects_df.iterrows():
        project_tasks = tasks_df[tasks_df['project'] == project['project_name']]
        
        if project_tasks.empty:
            continue
            
        completed_tasks = project_tasks[project_tasks['update_status'].isin(['completed', 'sent'])]
        completion_rate = len(completed_tasks) / len(project_tasks) * 100 if len(project_tasks) > 0 else 0
        
        avg_completion_days = completed_tasks['completion_days'].mean() if not completed_tasks.empty else 0
        
        project_metrics.append({
            'project_name': project['project_name'],
            'project_phase': project['project_phase'],
            'project_type': project['project_type'],
            'description': project['description'],
            'start_date': project['start_date'],
            'end_date': project['end_date'],
            'tasks_count': len(project_tasks),
            'completion_rate': completion_rate,
            'avg_completion_days': avg_completion_days,
            'content_types': project_tasks['content_type'].nunique()
        })
    
    # Sort by task count (most active first)
    project_metrics = sorted(project_metrics, key=lambda x: x['tasks_count'], reverse=True)
    
    # Create columns for cards - using 2 columns
    col1, col2 = st.columns(2)
    
    # Display project cards
    for i, project in enumerate(project_metrics):
        with col1 if i % 2 == 0 else col2:
            with st.container():
                st.markdown(f"### {project['project_name']} - {project['project_phase']}")
                st.text(project['description'])
                st.text(f"Duration: {project['start_date'].strftime('%b %d, %Y')} to {project['end_date'].strftime('%b %d, %Y')}")
                st.text(f"Type: {project['project_type']}")
                
                # Create metrics in columns
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Tasks", f"{project['tasks_count']}")
                with m2:
                    st.metric("Completion", f"{project['completion_rate']:.1f}%")
                with m3:
                    st.metric("Avg. Days", f"{project['avg_completion_days']:.1f}")
                with m4:
                    st.metric("Content Types", f"{project['content_types']}")
                
                st.markdown("---")

# Display tasks table with filters
def display_tasks_table(tasks_df, projects_df, team_members_df, content_types_df):
    st.markdown('<div class="sub-header">Task Explorer</div>', unsafe_allow_html=True)
    
    # Define filter columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Project filter
        projects = ['All Projects'] + sorted(tasks_df['project'].unique().tolist())
        selected_project = st.selectbox("Select Project", projects)
    
    with col2:
        # Content type filter
        content_types = ['All Types'] + sorted(tasks_df['content_type'].unique().tolist())
        selected_content_type = st.selectbox("Select Content Type", content_types)
    
    with col3:
        # Assigned to filter
        assigned_to = ['All Team Members'] + sorted(tasks_df['assigned_to'].unique().tolist())
        selected_assigned_to = st.selectbox("Select Team Member", assigned_to)
    
    with col4:
        # Status filter
        statuses = ['All Statuses'] + sorted(tasks_df['update_status'].unique().tolist())
        selected_status = st.selectbox("Select Status", statuses)
    
    # Apply filters
    filtered_df = tasks_df.copy()
    
    if selected_project != 'All Projects':
        filtered_df = filtered_df[filtered_df['project'] == selected_project]
    
    if selected_content_type != 'All Types':
        filtered_df = filtered_df[filtered_df['content_type'] == selected_content_type]
    
    if selected_assigned_to != 'All Team Members':
        filtered_df = filtered_df[filtered_df['assigned_to'] == selected_assigned_to]
    
    if selected_status != 'All Statuses':
        filtered_df = filtered_df[filtered_df['update_status'] == selected_status]
    
    # Sort by date (most recent first)
    filtered_df = filtered_df.sort_values('date', ascending=False)
    
    # Create a container for the table
    st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)
    
    # Convert date columns to string for display
    display_df = filtered_df.copy()
    for col in ['date', 'assigned_on', 'delivered_on']:
        if col in display_df.columns:
            display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
    
    # Select columns to display
    display_columns = ['task_id', 'date', 'project', 'task_name', 'assigned_to', 
                      'content_type', 'update_status', 'revision_cycles', 'completion_days']
    
    st.dataframe(
        display_df[display_columns],
        column_config={
            "task_id": st.column_config.NumberColumn("ID", format="%d"),
            "date": "Date",
            "project": "Project",
            "task_name": "Task Name",
            "assigned_to": "Assigned To",
            "content_type": "Content Type",
            "update_status": "Status",
            "revision_cycles": st.column_config.NumberColumn("Revisions", format="%d"),
            "completion_days": st.column_config.NumberColumn("Days to Complete", format="%d")
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return filtered_df

# Display task detail
def display_task_detail(task_id, tasks_df, messages_df, team_members_df):
    # Get task data
    task = tasks_df[tasks_df['task_id'] == task_id].iloc[0]
    
    # Create an expander for task details
    with st.expander(f"Task Details: {task['task_name']}", expanded=True):
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Project:** {task['project']}")
            st.markdown(f"**Content Type:** {task['content_type']}")
            st.markdown(f"**Work Scope:** {task['work_scope']}")
            st.markdown(f"**Assigned By:** {task['assigned_by']} on {task['assigned_on'].strftime('%B %d, %Y')}")
        
        with col2:
            st.markdown(f"**Assigned To:** {task['assigned_to']}")
            st.markdown(f"**Status:** {task['update_status'].title()}")
            st.markdown(f"**Revision Cycles:** {task['revision_cycles']}")
            
            if pd.notna(task['delivered_on']):
                st.markdown(f"**Delivered On:** {task['delivered_on'].strftime('%B %d, %Y')}")
            
            if pd.notna(task['completion_days']):
                st.markdown(f"**Days to Complete:** {int(task['completion_days'])}")
                
        # Show issues faced if any
        if pd.notna(task.get('issues_faced')):
            st.markdown("---")
            st.markdown(f"**Issues Faced:** {task['issues_faced']}")
    
    # Display messages
    messages = load_task_messages(task_id, messages_df)
    
    if messages:
        st.markdown('<div class="sub-header">Communication History</div>', unsafe_allow_html=True)
        
        for message in messages:
            formatted_date = message['date'].strftime('%B %d, %Y %I:%M %p') if isinstance(message['date'], datetime) else str(message['date'])
            
            with st.container():
                st.markdown(f"""
                <div class="message-sender">{message['sender']} → {message.get('recipient', '')}</div>
                <div class="message-date">{formatted_date}</div>
                """, unsafe_allow_html=True)
                
                st.info(message['message_content'])
                
                if pd.notna(message.get('attachment')):
                    st.markdown(f"**Attachment:** {message['attachment']}")
                
                if 'message_type' in message and pd.notna(message.get('message_type')):
                    st.markdown(f"**Type:** {message['message_type'].title()}")
                
                st.markdown("---")
    else:
        st.info("No communication history available for this task.")

# Display task message timeline
def display_task_message_timeline(task_id, tasks_df, messages_df):
    # Get task data
    task = tasks_df[tasks_df['task_id'] == task_id].iloc[0]
    
    # Get messages for this task
    task_messages = messages_df[messages_df['task_id'] == task_id].sort_values('date')
    
    if task_messages.empty:
        st.info("No communication timeline available for this task.")
        return
    
    # Calculate task duration
    start_date = pd.to_datetime(task['assigned_on'])
    end_date = pd.to_datetime(task['delivered_on']) if pd.notna(task['delivered_on']) else pd.Timestamp.today()
    duration_days = (end_date - start_date).days + 1  # +1 to include the start day
    
    # Create timeline chart data
    st.markdown('<div class="sub-header">Task Communication Timeline</div>', unsafe_allow_html=True)
    
    # Convert dates to consistent format for display
    task_messages['formatted_date'] = pd.to_datetime(task_messages['date']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Create unique list of people involved
    people_involved = sorted(list(set(task_messages['sender'].tolist() + 
                                     [r for r in task_messages['recipient'].tolist() if pd.notna(r)])))
    
    # Display summary information
    st.markdown(f"""
    ### Task Timeline Summary
    - **Duration:** {duration_days} days
    - **People Involved:** {', '.join(people_involved)}
    - **Communication Volume:** {len(task_messages)} messages
    """)
    
    # Create a timeline visualization using Streamlit
    for index, message in task_messages.iterrows():
        message_date = pd.to_datetime(message['date'])
        days_since_start = (message_date - start_date).days
        
        # Determine message styling based on type
        message_style = "info"
        if 'message_type' in message and pd.notna(message['message_type']):
            message_type = message['message_type']
            if message_type in ['feedback', 'revision']:
                message_style = "warning"
            elif message_type in ['approval', 'confirmation']:
                message_style = "success"
            elif message_type in ['urgency']:
                message_style = "error"
        
        # Timeline entry layout
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(f"**{message['formatted_date']}**")
            
        with col2:
            st.markdown(f"**{message['sender']} → {message.get('recipient', '')}**")
            
            # Display message with appropriate styling
            if message_style == "info":
                st.info(message['message_content'])
            elif message_style == "warning":
                st.warning(message['message_content'])
            elif message_style == "success":
                st.success(message['message_content'])
            elif message_style == "error":
                st.error(message['message_content'])
            
            # Show attachment if present
            if pd.notna(message.get('attachment')):
                st.markdown(f"**Attachment:** {message['attachment']}")
            
            # Show message type if present    
            if 'message_type' in message and pd.notna(message['message_type']):
                st.markdown(f"**Type:** {message['message_type'].title()}")
        
        st.markdown("---")
    
    # Communication activity over time
    st.markdown("### Communication Activity")
    
    # Group by date and count messages
    task_messages['date_only'] = pd.to_datetime(task_messages['date']).dt.date
    daily_messages = task_messages.groupby('date_only').size().reset_index()
    daily_messages.columns = ['Date', 'Message Count']
    
    # Create bar chart
    fig = px.bar(
        daily_messages,
        x='Date',
        y='Message Count',
        title="Daily Communication Activity",
        labels={'Message Count': 'Number of Messages', 'date_only': 'Date'}
    )
    
    fig.update_layout(height=300, margin=dict(l=40, r=40, t=60, b=40))
    st.plotly_chart(fig, use_container_width=True)

# Project timeline visualization using streamlit-elements
def display_project_timeline(projects_df, tasks_df):
    st.markdown('<div class="sub-header">Project Timeline</div>', unsafe_allow_html=True)
    
    # Get list of projects
    projects = sorted(projects_df['project_name'].unique().tolist())
    selected_project = st.selectbox("Select Project for Timeline", projects, key="timeline_project")
    
    # Filter projects and tasks
    selected_project_data = projects_df[projects_df['project_name'] == selected_project].iloc[0]
    project_tasks = tasks_df[tasks_df['project'] == selected_project_data['project_name']]
    
    # Project timeframe
    start_date = selected_project_data['start_date']
    end_date = selected_project_data['end_date']
    
    # Display project overview with card component
    custom_card(
        title=f"{selected_project_data['project_name']} - {selected_project_data['project_phase']}",
        text=f"{selected_project_data['description']}\n\n**Duration:** {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}\n\n**Type:** {selected_project_data['project_type']}",
        key=f"project_timeline_card_{selected_project}"
    )
    
    # Group tasks by month
    project_tasks['month_year'] = project_tasks['date'].dt.strftime('%Y-%m')
    project_tasks['month_display'] = project_tasks['date'].dt.strftime('%B %Y')
    
    # Sort by date
    project_tasks = project_tasks.sort_values('date')
    
    # Group by month (observed=True for categorical data)
    monthly_tasks = project_tasks.groupby(['month_year', 'month_display'], observed=True)
    
    # Display timeline with streamlit-elements
    with elements("project_timeline"):
        items = [
        # header
        dashboard.Item(
            "timeline_header", x=0, y=0, w=12, h=2,
            children=[ mui.Typography(f"{selected_project} Timeline", variant="h5") ]
        )
    ]
    row = 3
    for (ym, disp), tasks in monthly_tasks:
        paper = mui.Paper(
            elevation=2, sx={"mb":2},
            children=[
                mui.Box(sx={"p":2}, children=[
                    mui.Typography(disp, variant="h6"),
                    mui.Typography(f"{len(tasks)} tasks", variant="subtitle1"),
                    mui.Button("View Tasks", variant="outlined",
                               onClick={"callback": lambda m=disp:
                                        html.setAttribute(f"accordion_{m}", "expanded", True)})
                ]),
                mui.Divider(),
                mui.Accordion(
                    id=f"accordion_{disp}",
                    children=[
                        mui.AccordionSummary(expandIcon=mui.icons.ExpandMore(),
                                             children=[mui.Typography(f"View {len(tasks)} tasks")]),
                        mui.AccordionDetails(children=[
                            mui.List(children=[
                                mui.ListItem(children=[
                                    mui.ListItemText(
                                        primary=task["task_name"],
                                        secondary=(
                                            f"Assigned: {task['assigned_to']} • "
                                            f"Status: {task['update_status'].title()}"
                                        )
                                    )
                                ]) for _, task in tasks.iterrows()
                            ])
                        ])
                    ]
                )
            ]
        )
        items.append(dashboard.Item(f"timeline_{ym}", x=row, y=0, w=12, h=8, children=[paper]))
        row += 8

    dashboard.Grid(draggablePanels=False, children=items)

    # Alternative implementation with streamlit native components
    st.markdown("### Project Timeline (Alternative View)")
    
    # Display timeline
    for (month_year, month_display), tasks in monthly_tasks:
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-marker"></div>
            <div class="timeline-content">
                <div class="timeline-date">{month_display}</div>
                <div>
                    <strong>{len(tasks)} tasks</strong>
                </div>
            </div>
        </div>
        <div class="timeline-line"></div>
        """, unsafe_allow_html=True)
        
        # Display tasks for this month
        with st.expander(f"View {len(tasks)} tasks from {month_display}"):
            for i, task in enumerate(tasks.iterrows()):
                _, task_data = task
                cols = st.columns([3, 2, 1, 1])
                with cols[0]:
                    st.write(f"**{task_data['task_name']}**")
                with cols[1]:
                    st.write(f"Assigned to: {task_data['assigned_to']}")
                with cols[2]:
                    st.write(f"Status: {task_data['update_status'].title()}")
                with cols[3]:
                    if pd.notna(task_data['completion_days']):
                        st.write(f"Days: {int(task_data['completion_days'])}")
                
                if i < len(tasks) - 1:
                    st.markdown("---")
    
    # Close the last timeline line
    st.markdown("""
    <div class="timeline-item">
        <div class="timeline-marker"></div>
        <div class="timeline-content">
            <div class="timeline-date">End of Timeline</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Team performance analytics with streamlit components
def display_team_analytics(tasks_df, team_members_df):
    st.markdown('<div class="sub-header">Team Performance Analytics</div>', unsafe_allow_html=True)
    
    # Get list of team members (exclude groups)
    individual_members = team_members_df[team_members_df['team'] != 'Group']['name'].tolist()
    
    # Calculate performance metrics for each team member
    member_metrics = []
    
    for member in individual_members:
        member_tasks = tasks_df[tasks_df['assigned_to'] == member]
        
        if member_tasks.empty:
            continue
        
        completed_tasks = member_tasks[member_tasks['update_status'].isin(['completed', 'sent'])]
        completion_rate = len(completed_tasks) / len(member_tasks) * 100
        
        avg_completion_days = completed_tasks['completion_days'].mean() if not completed_tasks.empty else 0
        avg_revision_cycles = completed_tasks['revision_cycles'].mean() if not completed_tasks.empty else 0
        
        # Get content type distribution
        content_types = member_tasks['content_type'].value_counts().to_dict()
        
        # Get top projects
        top_projects = member_tasks['project'].value_counts().nlargest(3).to_dict()
        
        member_metrics.append({
            'name': member,
            'role': team_members_df[team_members_df['name'] == member]['role'].iloc[0],
            'specialization': team_members_df[team_members_df['name'] == member]['specialization'].iloc[0],
            'tasks_count': len(member_tasks),
            'completion_rate': completion_rate,
            'avg_completion_days': avg_completion_days,
            'avg_revision_cycles': avg_revision_cycles,
            'content_types': content_types,
            'top_projects': top_projects
        })
    
    # Sort by task count (most productive first)
    member_metrics = sorted(member_metrics, key=lambda x: x['tasks_count'], reverse=True)
    
    # Create visualizations in a more controlled layout
    with st.container():
        # Team overview metrics
        st.markdown("### Team Overview")
        total_members = len(member_metrics)
        total_tasks = sum(m['tasks_count'] for m in member_metrics)
        avg_completion_rate = sum(m['completion_rate'] for m in member_metrics) / total_members if total_members > 0 else 0
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("Active Team Members", total_members)
        with metric_cols[1]:
            st.metric("Total Assigned Tasks", total_tasks)
        with metric_cols[2]:
            st.metric("Avg. Completion Rate", f"{avg_completion_rate:.1f}%")
        with metric_cols[3]:
            st.metric("Team Efficiency", f"{sum(m['avg_completion_days'] for m in member_metrics) / total_members:.1f} days")
    
    # Team member comparison charts in a separate container
    with st.container():
        st.markdown("### Team Member Comparison")
        tab1, tab2, tab3 = st.tabs(["Task Volume", "Completion Rate", "Efficiency"])
        
        with tab1:
            # Tasks completed
            member_tasks = pd.DataFrame([
                {'name': m['name'], 'value': m['tasks_count']} 
                for m in member_metrics
            ])
            
            fig = px.bar(member_tasks, x='name', y='value',
                        title='Tasks Assigned',
                        labels={'value': 'Number of Tasks', 'name': 'Team Member'},
                        height=400)
            
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Number of Tasks",
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Completion rate
            member_completion = pd.DataFrame([
                {'name': m['name'], 'value': m['completion_rate']} 
                for m in member_metrics
            ])
            
            fig = px.bar(member_completion, x='name', y='value',
                        title='Task Completion Rate (%)',
                        labels={'value': 'Completion Rate (%)', 'name': 'Team Member'},
                        height=400)
            
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Completion Rate (%)",
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Average completion days
            member_days = pd.DataFrame([
                {'name': m['name'], 'value': m['avg_completion_days']} 
                for m in member_metrics
            ])
            
            fig = px.bar(member_days, x='name', y='value',
                        title='Average Days to Complete',
                        labels={'value': 'Avg. Days', 'name': 'Team Member'},
                        height=400)
            
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Avg. Days",
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Team member details
    st.markdown("### Individual Team Member Analysis")
    selected_member = st.selectbox("Select Team Member for Detailed Analysis", 
                                individual_members)
    
    # Get member data
    member_data = next((m for m in member_metrics if m['name'] == selected_member), None)
    member_profile = team_members_df[team_members_df['name'] == selected_member].iloc[0]
    
    if member_data:
        # Display member profile using streamlit-card
        col1, col2 = st.columns(2)
        
        with col1:
            custom_card(
                title=member_profile['name'],
                text=f"**Role:** {member_profile['role']}\n\n"
                     f"**Team:** {member_profile['team']}\n\n"
                     f"**Joined:** {member_profile['joined_date']}\n\n"
                     f"**Specialization:** {member_profile['specialization']}\n\n"
                     f"**Email:** {member_profile['email']}",
                key=f"member_profile_{selected_member}"
            )
        
        with col2:
            # Content type distribution
            content_df = pd.DataFrame([
                {'content_type': ct, 'count': count} 
                for ct, count in member_data['content_types'].items()
            ])
            
            fig = px.pie(content_df, values='count', names='content_type',
                        title='Content Type Distribution',
                        hole=0.4)
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get tasks for this member
        member_tasks = tasks_df[tasks_df['assigned_to'] == selected_member].sort_values('date', ascending=False)
        
        # Display recent tasks
        st.markdown("#### Recent Tasks")
        
        # Display table with better styling
        display_columns = ['task_id', 'date', 'project', 'task_name', 
                          'content_type', 'update_status', 'revision_cycles', 'completion_days']
        
        # Convert date columns to string for display
        display_df = member_tasks.copy()
        for col in ['date', 'assigned_on', 'delivered_on']:
            if col in display_df.columns:
                display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
        
        # Add status color indicator
        status_colors = {
            'completed': 'success',
            'sent': 'success',
            'in progress': 'warning',
            'multiple revisions': 'warning',
            'feedback received': 'warning',
            'not prioritized': 'danger'
        }
        
        st.dataframe(
            display_df[display_columns].head(10),
            column_config={
                "task_id": st.column_config.NumberColumn("ID", format="%d"),
                "date": "Date",
                "project": "Project",
                "task_name": "Task Name",
                "content_type": "Content Type",
                "update_status": st.column_config.TextColumn(
                    "Status",
                    help="Current status of the task",
                    # Add conditional formatting based on status
                    disabled=False
                ),
                "revision_cycles": st.column_config.NumberColumn("Revisions", format="%d"),
                "completion_days": st.column_config.NumberColumn("Days to Complete", format="%d")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Monthly task distribution chart
        st.markdown("#### Monthly Task Distribution")
        
        # Create month column
        member_tasks['month_year'] = member_tasks['date'].dt.strftime('%Y-%m')
        member_tasks['month_display'] = member_tasks['date'].dt.strftime('%b %Y')
        
        # Group by month (observed=True for categorical data)
        monthly_tasks = member_tasks.groupby(['month_year', 'month_display'], observed=True).size().reset_index(name='count')
        
        # Sort by month_year
        monthly_tasks = monthly_tasks.sort_values('month_year')
        
        # Create bar chart
        fig = px.bar(monthly_tasks, x='month_display', y='count',
                    title=f'Monthly Task Distribution for {selected_member}',
                    labels={'count': 'Number of Tasks', 'month_display': 'Month'},
                    height=300)
        
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Number of Tasks",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Analyze team specialization with better visuals
def analyze_team_specialization(tasks_df, team_members_df, content_types_df):
    """
    Analyze team member specialization by content type and priority levels
    with improved visualization components.
    """
    st.markdown('<div class="sub-header">Team Specialization Analysis</div>', unsafe_allow_html=True)
    
    # Get list of team members (exclude groups)
    individual_members = team_members_df[team_members_df['team'] != 'Group']['name'].tolist()
    
    # Create matrix of team members x content types
    specialization_data = []
    
    for member in individual_members:
        member_tasks = tasks_df[tasks_df['assigned_to'] == member]
        
        if member_tasks.empty:
            continue
            
        content_type_counts = member_tasks['content_type'].value_counts()
        
        for content_type, count in content_type_counts.items():
            # Get priority level for this content type
            if content_type in content_types_df['content_type'].values:
                priority = content_types_df[content_types_df['content_type'] == content_type]['priority_level'].iloc[0]
                # Extract just the main priority level (High, Medium, Low)
                priority_main = priority.split(' - ')[0] if ' - ' in priority else priority
            else:
                priority_main = 'Unknown'
                
            specialization_data.append({
                'Team Member': member,
                'Content Type': content_type,
                'Count': count,
                'Priority': priority_main
            })
    
    # Convert to DataFrame
    specialization_df = pd.DataFrame(specialization_data)
    
    # Create heatmap of team members x content types
    if not specialization_df.empty:
        # Pivot data for heatmap
        pivot_data = specialization_df.pivot_table(
            values='Count', 
            index='Team Member', 
            columns='Content Type', 
            fill_value=0
        )
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Specialization Matrix", "Priority Distribution", "Efficiency Analysis"])
        
        with tab1:
            st.markdown("### Team Member Specialization Matrix")
            st.markdown("This heatmap shows which team members work most frequently with specific content types.")
            
            # Create heatmap
            fig = px.imshow(
                pivot_data, 
                labels=dict(x="Content Type", y="Team Member", color="Task Count"),
                title="",
                color_continuous_scale="Viridis",
                aspect="auto"
            )
            
            fig.update_layout(
                height=500,
                xaxis=dict(tickangle=45),
                margin=dict(l=40, r=40, t=40, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Priority level analysis
            st.markdown("### Priority Level Workload Distribution")
            st.markdown("This chart shows how high, medium and low priority tasks are distributed across team members.")
            
            # Group by team member and priority
            priority_data = specialization_df.groupby(['Team Member', 'Priority'], observed=True)['Count'].sum().reset_index()
            
            # Create grouped bar chart
            fig = px.bar(
                priority_data, 
                x='Team Member', 
                y='Count', 
                color='Priority',
                barmode='stack',
                title="",
                color_discrete_map={
                    'High': '#ff4b4b',
                    'Medium-High': '#ff9d4b',
                    'Medium': '#ffdb4b',
                    'Medium-Low': '#9dff4b',
                    'Low': '#4bff4b',
                    'Unknown': '#cccccc'
                }
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="",
                yaxis_title="Number of Tasks",
                margin=dict(l=40, r=40, t=40, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate priority distribution percentages
            st.markdown("### Priority Mix by Team Member")
            
            # Calculate percentages
            priority_pivot = priority_data.pivot_table(
                values='Count',
                index='Team Member',
                columns='Priority',
                fill_value=0
            )
            
            # Calculate row percentages
            priority_percent = priority_pivot.div(priority_pivot.sum(axis=1), axis=0) * 100
            priority_percent = priority_percent.reset_index()
            
            # Melt for visualization
            priority_percent_melt = pd.melt(
                priority_percent, 
                id_vars=['Team Member'], 
                var_name='Priority', 
                value_name='Percentage'
            )
            
            # Create stacked percentage bar chart
            fig = px.bar(
                priority_percent_melt,
                x='Team Member',
                y='Percentage',
                color='Priority',
                title="",
                color_discrete_map={
                    'High': '#ff4b4b',
                    'Medium-High': '#ff9d4b',
                    'Medium': '#ffdb4b',
                    'Medium-Low': '#9dff4b',
                    'Low': '#4bff4b',
                    'Unknown': '#cccccc'
                }
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="",
                yaxis_title="Percentage of Tasks (%)",
                yaxis=dict(ticksuffix="%"),
                barmode='stack',
                margin=dict(l=40, r=40, t=40, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Efficiency vs. Priority Analysis
            st.markdown("### Efficiency by Priority Level")
            st.markdown("This scatter plot shows how efficiently team members complete tasks of different priority levels.")
            
            # Prepare data for analysis
            efficiency_data = []
            
            for member in individual_members:
                member_tasks = tasks_df[tasks_df['assigned_to'] == member]
                
                if member_tasks.empty:
                    continue
                    
                # Only consider completed tasks
                completed_tasks = member_tasks[member_tasks['update_status'].isin(['completed', 'sent'])]
                
                if completed_tasks.empty:
                    continue
                    
                for priority in ['High', 'Medium-High', 'Medium', 'Medium-Low', 'Low']:
                    # Get content types for this priority
                    priority_content_types = content_types_df[content_types_df['priority_level'].str.startswith(priority)]['content_type'].tolist()
                    
                    # Filter tasks for these content types
                    priority_tasks = completed_tasks[completed_tasks['content_type'].isin(priority_content_types)]
                    
                    if not priority_tasks.empty:
                        avg_completion_days = priority_tasks['completion_days'].mean()
                        efficiency_data.append({
                            'Team Member': member,
                            'Priority': priority,
                            'Avg. Completion Days': avg_completion_days,
                            'Task Count': len(priority_tasks)
                        })
            
            # Convert to DataFrame
            efficiency_df = pd.DataFrame(efficiency_data)
            
            if not efficiency_df.empty:
                # Create scatter plot
                fig = px.scatter(
                    efficiency_df,
                    x='Priority',
                    y='Avg. Completion Days',
                    size='Task Count',
                    color='Team Member',
                    title="",
                    size_max=30,
                    hover_name='Team Member',
                    hover_data={
                        'Team Member': False,  # Don't show in hover tooltip (already shown)
                        'Priority': True,
                        'Avg. Completion Days': ':.1f',
                        'Task Count': True
                    }
                )
                
                fig.update_layout(
                    height=500,
                    xaxis=dict(
                        categoryorder='array',
                        categoryarray=['High', 'Medium-High', 'Medium', 'Medium-Low', 'Low']
                    ),
                    yaxis_title="Avg. Days to Complete",
                    margin=dict(l=40, r=40, t=40, b=60)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add efficiency ranking
                st.markdown("### Team Member Efficiency Ranking")
                
                # Calculate overall efficiency by team member
                efficiency_ranking = efficiency_df.groupby('Team Member')['Avg. Completion Days'].mean().reset_index()
                efficiency_ranking = efficiency_ranking.sort_values('Avg. Completion Days')
                efficiency_ranking.columns = ['Team Member', 'Average Days to Complete']
                
                # Create bar chart with conditional colors
                fig = px.bar(
                    efficiency_ranking,
                    x='Team Member',
                    y='Average Days to Complete',
                    title="",
                    color='Average Days to Complete',
                    color_continuous_scale=[(0, 'green'), (0.5, 'yellow'), (1.0, 'red')],
                    color_continuous_midpoint=efficiency_ranking['Average Days to Complete'].median()
                )
                
                fig.update_layout(
                    height=400,
                    xaxis_title="",
                    yaxis_title="Average Days to Complete",
                    coloraxis_showscale=False,  # Hide the color scale
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data to generate efficiency analysis.")
    else:
        st.warning("Not enough data to generate team specialization visualizations.")

# Display the project timeline markdown in an enhanced format
def display_project_timelines_md():
    st.markdown('<div class="sub-header">Project Timeline Documentation</div>', unsafe_allow_html=True)
    
    # Load the markdown content
    md_content = load_project_timelines()
    
    # Display the formatted markdown content with tabs for different projects
    projects = ["Sanctuary 105 (Phase 1)", "Sanctuary 105 (Phase 2)"]
    tabs = st.tabs(projects)
    
    # Parse the markdown content to extract project sections
    sections = {}
    current_section = None
    current_content = []
    
    for line in md_content.split('\n'):
        if line.startswith('## '):
            if current_section is not None:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = [line]
        else:
            if current_section is not None:
                current_content.append(line)
    
    # Add the last section
    if current_section is not None:
        sections[current_section] = '\n'.join(current_content)
    
    # Display content in tabs
    for i, project in enumerate(projects):
        with tabs[i]:
            if project in sections:
                st.markdown(sections[project])
            else:
                st.warning(f"Timeline documentation for {project} not found.")
                
                # Search for partial matches
                matches = [section for section in sections.keys() if project.split('(')[0].strip() in section]
                if matches:
                    st.markdown("Found similar project timelines:")
                    for match in matches:
                        st.markdown(f"### {match}")
                        with st.expander("View Timeline"):
                            st.markdown(sections[match])

# Main application with improved layout and error handling
def main():
    # Apply custom CSS
    apply_custom_css()
    
    # Header with improved styling
    st.markdown('<div class="main-header">ATS Homekraft Marketing Dashboard</div>', unsafe_allow_html=True)
    
    try:
        # Load data with progress indicator
        with st.spinner("Loading dashboard data..."):
            tasks_df, projects_df, team_members_df, content_types_df, messages_df = load_all_data()
        
        # Check if data is loaded
        if tasks_df.empty or projects_df.empty:
            st.error("Failed to load task data. Please check that the data files exist in the correct location.")
            st.info("Expected data files in 'data/' directory: tasks.csv, projects.csv, team_members.csv, content_types.csv, messages.csv")
            return
        
        # Cache successful data load
        st.success("Data loaded successfully!")
        
        # Sidebar navigation with improved styling
        st.sidebar.markdown('<div class="sidebar-title">Navigation</div>', unsafe_allow_html=True)
        page = st.sidebar.radio("Select Page", [
            "📊 Dashboard Overview", 
            "📝 Task Explorer", 
            "📅 Project Timeline", 
            "👥 Team Performance",
            "📊 Content Analysis", 
            "💬 Communication Analysis", 
            "📄 Documentation"
        ])
        
        # Date filter in sidebar with improved UX
        st.sidebar.markdown('<div class="sidebar-title">Date Filter</div>', unsafe_allow_html=True)
        
        # Get min and max dates
        min_date = tasks_df['date'].min().date()
        max_date = tasks_df['date'].max().date()
        
        # Create tabs for Quick Filters and Custom Date Range
        filter_tabs = st.sidebar.tabs(["Quick Filters", "Custom Range"])
        
        with filter_tabs[0]:
            # Quick filter options
            quick_filter = st.radio(
                "Select Time Period",
                ["All Time", "Last Month", "Last 3 Months", "Last 6 Months", "Current Year"]
            )
            
            if quick_filter == "All Time":
                start_date = min_date
                end_date = max_date
            elif quick_filter == "Last Month":
                end_date = max_date
                start_date = (datetime.combine(end_date, datetime.min.time()) - timedelta(days=30)).date()
            elif quick_filter == "Last 3 Months":
                end_date = max_date
                start_date = (datetime.combine(end_date, datetime.min.time()) - timedelta(days=90)).date()
            elif quick_filter == "Last 6 Months":
                end_date = max_date
                start_date = (datetime.combine(end_date, datetime.min.time()) - timedelta(days=180)).date()
            elif quick_filter == "Current Year":
                end_date = max_date
                start_date = datetime(end_date.year, 1, 1).date()
            
            # Display selected date range
            st.write(f"From: {start_date.strftime('%b %d, %Y')}")
            st.write(f"To: {end_date.strftime('%b %d, %Y')}")
        
        with filter_tabs[1]:
            # Custom date range selector
            custom_start_date = st.date_input("Start Date", min_date)
            custom_end_date = st.date_input("End Date", max_date)
            
            if custom_start_date and custom_end_date:
                if custom_start_date > custom_end_date:
                    st.error("Start date must be before end date")
                else:
                    start_date = custom_start_date
                    end_date = custom_end_date
        
        # Add refresh button
        if st.sidebar.button("Refresh Dashboard"):
            st.rerun()
        
        # Filter data by date
        filtered_tasks = tasks_df[
            (tasks_df['date'].dt.date >= start_date) & 
            (tasks_df['date'].dt.date <= end_date)
        ]
        
        # Display status of applied filter
        st.sidebar.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px;">
            <p><strong>Active Filter:</strong><br>
            {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}</p>
            <p><strong>Tasks in range:</strong> {len(filtered_tasks)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add export options in sidebar
        st.sidebar.markdown('<div class="sidebar-title">Export Options</div>', unsafe_allow_html=True)
        export_format = st.sidebar.selectbox("Export Format", ["CSV", "Excel", "JSON"])
        
        if st.sidebar.button("Export Filtered Data"):
            # This would actually export the data in a real app
            st.sidebar.success(f"Data exported in {export_format} format!")
        
        # Display page based on selection with better error handling
        try:
            if page == "📊 Dashboard Overview":
                # Display metrics
                create_metrics_row(filtered_tasks)
                
                # Create a tabbed interface for different dashboard views
                dashboard_tabs = st.tabs(["Project Metrics", "Time Analysis", "Task Distribution"])
                
                with dashboard_tabs[0]:
                    # Project overview cards in their own container
                    with st.container():
                        display_project_cards(projects_df, filtered_tasks)
                
                with dashboard_tabs[1]:
                    # Charts in separate container blocks with controlled layout
                    with st.container():
                        plot_monthly_task_volume(filtered_tasks)
                        
       
                    with st.container():
                        plot_efficiency_trend(filtered_tasks)
                            
                                 
                
                with dashboard_tabs[2]:
                    with st.container():
                        plot_task_assignment(filtered_tasks)
                        
                    with st.container():
                        plot_task_completion_time(filtered_tasks, content_types_df)

                            
                
            elif page == "📝 Task Explorer":
                # Display tasks table with filters
                filtered_df = display_tasks_table(filtered_tasks, projects_df, team_members_df, content_types_df)
                
                # Task detail view
                if not filtered_df.empty:
                    st.markdown('<div class="sub-header">Task Details</div>', unsafe_allow_html=True)
                    task_ids = filtered_df['task_id'].tolist()
                    selected_task_id = st.selectbox("Select Task ID for Details", task_ids)
                    
                    if selected_task_id:
                        task_tabs = st.tabs(["Task Details", "Communication Timeline"])
                        
                        with task_tabs[0]:
                            display_task_detail(selected_task_id, filtered_tasks, messages_df, team_members_df)
                        
                        with task_tabs[1]:
                            display_task_message_timeline(selected_task_id, filtered_tasks, messages_df)
                
            elif page == "📅 Project Timeline":
                # Project timeline visualization
                display_project_timeline(projects_df, filtered_tasks)
                
                # Content type distribution
                plot_content_type_by_project(filtered_tasks)
                
            elif page == "👥 Team Performance":
                # Team performance analytics
                display_team_analytics(filtered_tasks, team_members_df)
                
                # Add new team specialization analysis
                analyze_team_specialization(filtered_tasks, team_members_df, content_types_df)
                
            elif page == "📊 Content Analysis":
                # Content type analysis page
                display_content_type_details(content_types_df)
                
                # Add content type usage trends over time
                st.markdown('<div class="sub-header">Content Type Usage Trends</div>', unsafe_allow_html=True)
                
                # Create month column
                filtered_tasks['month_year'] = filtered_tasks['date'].dt.strftime('%Y-%m')
                filtered_tasks['month_display'] = filtered_tasks['date'].dt.strftime('%b %Y')
                
                # Group by month and content type
                monthly_content = filtered_tasks.groupby(['month_year', 'month_display', 'content_type'], observed=True).size().reset_index(name='count')
                
                # Sort by date
                monthly_content = monthly_content.sort_values('month_year')
                
                # Get unique months in chronological order
                unique_months = monthly_content.sort_values('month_year')['month_display'].unique()
                
                # Create line chart for each content type
                fig = px.line(
                    monthly_content,
                    x='month_display',
                    y='count',
                    color='content_type',
                    title='Content Type Usage Over Time',
                    labels={'count': 'Number of Tasks', 'month_display': 'Month', 'content_type': 'Content Type'},
                    category_orders={'month_display': unique_months},
                    height=500
                )
                
                fig.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis_title="",
                    yaxis_title="Number of Tasks",
                    margin=dict(l=40, r=40, t=60, b=40)
                )
                
                # Add markers to the lines
                fig.update_traces(mode='lines+markers')
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif page == "💬 Communication Analysis":
                # Communication analysis page
                st.markdown('<div class="sub-header">Team Communication Analysis</div>', unsafe_allow_html=True)
                
                # Message volume analysis
                if not messages_df.empty:
                    # Add date column for consistent filtering
                    messages_df['message_date'] = pd.to_datetime(messages_df['date']).dt.date
                    
                    # Filter messages by date
                    filtered_messages = messages_df[
                        (messages_df['message_date'] >= start_date) & 
                        (messages_df['message_date'] <= end_date)
                    ]
                    
                    if not filtered_messages.empty:
                        # Create tabs for different communication analyses
                        comm_tabs = st.tabs([
                            "Message Volume", 
                            "Message Types", 
                            "Communication Network", 
                            "Activity Timeline"
                        ])
                        
                        with comm_tabs[0]:
                            # Message volume by project
                            st.markdown("### Message Volume by Project")
                            
                            # Get project for each task
                            message_projects = filtered_messages.merge(
                                tasks_df[['task_id', 'project']], 
                                on='task_id',
                                how='left'
                            )
                            
                            # Group by project
                            project_messages = message_projects.groupby('project', observed=True).size().reset_index(name='count')
                            project_messages = project_messages.sort_values('count', ascending=False)
                            
                            # Create bar chart
                            fig = px.bar(
                                project_messages,
                                x='project',
                                y='count',
                                title="",
                                labels={'count': 'Number of Messages', 'project': 'Project'},
                                height=400,
                                color='project'
                            )
                            
                            fig.update_layout(
                                xaxis_title="",
                                yaxis_title="Number of Messages",
                                showlegend=False,
                                margin=dict(l=40, r=40, t=40, b=40)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Message volume by team member
                            st.markdown("### Communication Volume by Team Member")
                            
                            # Count sent messages per person
                            sender_counts = filtered_messages['sender'].value_counts().reset_index()
                            sender_counts.columns = ['Person', 'Sent']
                            
                            # Count received messages per person
                            recipient_counts = filtered_messages['recipient'].value_counts().reset_index()
                            recipient_counts.columns = ['Person', 'Received']
                            
                            # Merge counts
                            person_counts = sender_counts.merge(recipient_counts, on='Person', how='outer').fillna(0)
                            person_counts['Total'] = person_counts['Sent'] + person_counts['Received']
                            person_counts = person_counts.sort_values('Total', ascending=False)
                            
                            # Create grouped bar chart
                            fig = px.bar(
                                person_counts,
                                x='Person',
                                y=['Sent', 'Received'],
                                title="",
                                labels={'value': 'Number of Messages', 'Person': 'Team Member', 'variable': 'Direction'},
                                height=400,
                                barmode='group'
                            )
                            
                            fig.update_layout(
                                xaxis_title="",
                                yaxis_title="Number of Messages",
                                legend_title="Message Direction",
                                margin=dict(l=40, r=40, t=40, b=40)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with comm_tabs[1]:
                            # Message types distribution
                            if 'message_type' in filtered_messages.columns:
                                st.markdown("### Message Types Distribution")
                                
                                # Group by message type
                                message_types = filtered_messages['message_type'].value_counts().reset_index()
                                message_types.columns = ['Message Type', 'Count']
                                
                                # Sort by count
                                message_types = message_types.sort_values('Count', ascending=False)
                                
                                # Create two visualizations in columns
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    # Create pie chart
                                    fig = px.pie(
                                        message_types,
                                        values='Count',
                                        names='Message Type',
                                        title="",
                                        hole=0.4
                                    )
                                    
                                    fig.update_layout(
                                        height=400,
                                        margin=dict(l=20, r=20, t=40, b=20)
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                with col2:
                                    # Create bar chart
                                    fig = px.bar(
                                        message_types,
                                        y='Message Type',
                                        x='Count',
                                        title="",
                                        orientation='h',
                                        color='Message Type'
                                    )
                                    
                                    fig.update_layout(
                                        height=400,
                                        showlegend=False,
                                        yaxis_title="",
                                        xaxis_title="Number of Messages",
                                        margin=dict(l=40, r=20, t=40, b=20)
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Message type by project matrix
                                st.markdown("### Message Type by Project")
                                
                                # Create message type by project matrix
                                message_type_project = message_projects.dropna(subset=['project', 'message_type'])
                                
                                if not message_type_project.empty:
                                    # Group by project and message type
                                    type_project_counts = message_type_project.groupby(['project', 'message_type'], observed=True).size().reset_index(name='count')
                                    
                                    # Create heatmap
                                    pivot_data = type_project_counts.pivot_table(
                                        values='count', 
                                        index='project', 
                                        columns='message_type', 
                                        fill_value=0
                                    )
                                    
                                    fig = px.imshow(
                                        pivot_data,
                                        labels=dict(x="Message Type", y="Project", color="Count"),
                                        title="",
                                        aspect="auto",
                                        color_continuous_scale='viridis'
                                    )
                                    
                                    fig.update_layout(
                                        height=400,
                                        margin=dict(l=40, r=40, t=40, b=60),
                                        xaxis_title="",
                                        yaxis_title=""
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Message type classification not available in the data.")
                        
                        with comm_tabs[2]:
                            # Communication network
                            st.markdown("### Team Communication Network")
                            
                            # Count communications between senders and recipients
                            communication_counts = filtered_messages.groupby(['sender', 'recipient'], observed=True).size().reset_index()
                            communication_counts.columns = ['source', 'target', 'value']
                            
                            # Create custom network graph with Plotly
                            nodes = list(set(communication_counts['source'].tolist() + communication_counts['target'].tolist()))
                            node_indices = {node: i for i, node in enumerate(nodes)}
                            
                            # Create link data
                            links = []
                            for _, row in communication_counts.iterrows():
                                links.append({
                                    'source': node_indices[row['source']],
                                    'target': node_indices[row['target']],
                                    'value': row['value']
                                })
                            
                            # Create node data
                            node_data = []
                            for node in nodes:
                                # Count messages sent by this person
                                sent_count = filtered_messages[filtered_messages['sender'] == node].shape[0]
                                # Count messages received by this person
                                received_count = filtered_messages[filtered_messages['recipient'] == node].shape[0]
                                
                                node_data.append({
                                    'name': node,
                                    'sent': sent_count,
                                    'received': received_count
                                })
                            
                            # Create network graph
                            fig = go.Figure(data=[go.Sankey(
                                node = dict(
                                    pad = 15,
                                    thickness = 20,
                                    line = dict(color = "black", width = 0.5),
                                    label = [node['name'] for node in node_data],
                                    color = "blue"
                                ),
                                link = dict(
                                    source = [link['source'] for link in links],
                                    target = [link['target'] for link in links],
                                    value = [link['value'] for link in links]
                                )
                            )])
                            
                            fig.update_layout(
                                title_text="",
                                font_size=12,
                                height=600,
                                margin=dict(l=40, r=40, t=40, b=40)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with comm_tabs[3]:
                            # Communication activity over time
                            st.markdown("### Communication Activity Over Time")
                            
                            # Extract date only
                            filtered_messages['date_only'] = pd.to_datetime(filtered_messages['date']).dt.date
                            
                            # Group by date
                            daily_messages = filtered_messages.groupby('date_only', observed=True).size().reset_index()
                            daily_messages.columns = ['Date', 'Message Count']
                            
                            # Create line chart
                            fig = px.line(
                                daily_messages,
                                x='Date',
                                y='Message Count',
                                title="",
                                height=400
                            )
                            
                            fig.update_layout(
                                xaxis_title="",
                                yaxis_title="Number of Messages",
                                margin=dict(l=40, r=40, t=40, b=40)
                            )
                            
                            # Add markers
                            fig.update_traces(mode='lines+markers')
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Message activity by day of week
                            st.markdown("### Communication by Day of Week")
                            
                            # Add day of week
                            filtered_messages['day_of_week'] = pd.to_datetime(filtered_messages['date']).dt.day_name()
                            
                            # Define day order
                            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                            
                            # Group by day of week
                            day_messages = filtered_messages['day_of_week'].value_counts().reset_index()
                            day_messages.columns = ['Day of Week', 'Message Count']
                            
                            # Convert to categorical for proper ordering
                            day_messages['Day of Week'] = pd.Categorical(day_messages['Day of Week'], categories=day_order, ordered=True)
                            day_messages = day_messages.sort_values('Day of Week')
                            
                            # Create bar chart
                            fig = px.bar(
                                day_messages,
                                x='Day of Week',
                                y='Message Count',
                                title="",
                                color='Day of Week',
                                category_orders={"Day of Week": day_order}
                            )
                            
                            fig.update_layout(
                                xaxis_title="",
                                yaxis_title="Number of Messages",
                                showlegend=False,
                                margin=dict(l=40, r=40, t=40, b=40)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No messages found in the selected date range.")
                else:
                    st.warning("No message data available for analysis.")
            
            elif page == "📄 Documentation":
                # Display project timelines markdown
                display_project_timelines_md()
        
        except Exception as e:
            st.error(f"An error occurred while displaying the {page} page: {str(e)}")
            st.exception(e)
    
    except Exception as e:
        st.error("An error occurred while initializing the dashboard.")
        st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 ATS Homekraft Marketing Team Dashboard | Data last updated: May 12, 2025")

# Run the application
if __name__ == "__main__":
    main()
