# ATS Homekraft Marketing Dashboard

A comprehensive marketing task management and analytics dashboard built with Streamlit for tracking and visualizing the creative team's workflow and project performance.

## Overview

The ATS Homekraft Marketing Dashboard provides a visual interface to:

- Track task completion and productivity metrics
- Visualize project timelines and performance
- Analyze content types distribution across projects
- Measure team member performance and task allocation
- Explore detailed task communication history
- Analyze team communication patterns and efficiency
- View project documentation and timelines

## Features

- **Dashboard Overview**: High-level metrics, project cards, and visualizations of task volume, assignment distribution, and efficiency trends
- **Task Explorer**: Filterable task table with detailed view of individual task communication history and message timeline visualization
- **Project Timeline**: Visual timeline representation of project tasks organized chronologically
- **Team Performance**: Analytics on individual team member productivity, specialization, and task completion metrics with priority level workload distribution
- **Content Analysis**: Detailed information about content types, including best practices, tool usage, and priority distribution
- **Communication Analysis**: Team communication network visualization, message type distribution, and communication activity patterns
- **Documentation**: Detailed project timeline documentation in markdown format

## Installation

1. Clone this repository
2. Install requirements:
```
pip install -r requirements.txt
```
3. Run the setup script:
```
python dashboard.py
```
4. Launch the dashboard:
```
streamlit run app.py
```

## Data Structure

The dashboard uses the following data files:

- **tasks.csv**: Main task database with details on assignments, completion status, and metadata
- **projects.csv**: Project definitions with types, phases, and date ranges
- **team_members.csv**: Team member profiles with roles and specializations
- **content_types.csv**: Enhanced content type definitions with tools, priority levels, and best practices
- **messages.csv**: Comprehensive task communication history with message types and attachments
- **project_timelines.md**: Detailed project timeline documentation in markdown format

## Dashboard Pages

### Dashboard Overview
![Dashboard Overview](images/dashboard_overview.png)

Provides a high-level view of the marketing team's performance with key metrics:
- Total tasks and completion rate
- Average completion time
- Project cards with key performance indicators
- Monthly task volume chart
- Task assignment distribution
- Task completion time by content type
- Efficiency trend over time

### Task Explorer
![Task Explorer](images/task_explorer.png)

Enables detailed exploration of tasks with:
- Filterable task table by project, content type, team member, and status
- Detailed view of individual tasks including full communication history
- Message timeline visualization showing communication flow
- Revision cycles and completion time metrics

### Project Timeline
![Project Timeline](images/project_timeline.png)

Visualizes project progress with:
- Chronological timeline of tasks by month
- Expandable task details within timeline
- Content type distribution across projects

### Team Performance
![Team Performance](images/team_performance.png)

Analyzes individual team member productivity:
- Comparative metrics on task count, completion rate, and average time
- Content type specialization matrix showing expertise areas
- Priority level workload distribution by team member
- Efficiency analysis by priority level
- Recent task history and performance metrics

### Content Analysis
![Content Analysis](images/content_analysis.png)

Provides detailed information about content types:
- Comprehensive content type details including best practices
- Tool usage patterns across content types
- Priority distribution of different content categories
- Content type usage trends over time

### Communication Analysis
![Communication Analysis](images/communication_analysis.png)

Analyzes team communication patterns:
- Team communication network visualization
- Message type distribution (feedback, approvals, assignments, etc.)
- Communication activity over time
- Project-based communication volume

### Documentation
Provides access to detailed project timeline documentation in markdown format.

## Development

This dashboard is built with:
- Streamlit for the web interface
- Pandas for data manipulation
- Plotly for interactive visualizations

The application structure follows a modular approach with separate functions for:
- Data loading and preprocessing
- Metrics calculation
- Visualization components
- Page rendering

## Usage Examples

### Filtering Data
- Use the date range selector in the sidebar to focus on specific time periods
- Apply filters in the Task Explorer to narrow down specific projects, content types, or team members
- Use project-specific timelines in the Project Timeline page

### Performance Analysis
- View team member specialization in the Team Performance page
- Analyze content type efficiency in the Content Analysis page
- Examine communication patterns in the Communication Analysis page

### Documentation
- Review comprehensive project timelines in the Documentation page

## Contributors

- Botman - Dashboard design and development
- ATS Homekraft Marketing Team - Requirements and data

## License

This project is proprietary and confidential.