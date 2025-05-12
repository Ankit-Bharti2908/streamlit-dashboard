# ATS Homekraft Marketing Task Dashboard

A comprehensive Streamlit dashboard for analyzing and visualizing ATS Homekraft's marketing task data from July 2024 to April 2025.

## Features

- **Interactive Dashboard**: Visualize task distribution, assignment patterns, completion rates, and efficiency metrics
- **Task Explorer**: Search, filter, and examine detailed information about individual tasks
- **Project Timelines**: View structured project development phases and milestones
- **Raw Data Viewer**: Access and download the underlying datasets
- **Dynamic Filtering**: Filter data by project, date range, assignee, content type, and more

## Installation

1. Clone this repository:
```
git clone https://github.com/your-username/ats-homekraft-dashboard.git
cd ats-homekraft-dashboard
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Ensure your data files are placed in the `data` directory:
   - `tasks.csv`
   - `projects.csv`
   - `team_members.csv`
   - `content_types.csv`
   - `project_timelines.md`

2. Run the Streamlit app:
```
streamlit run app.py
```

3. Open your browser and go to `http://localhost:8501` to access the dashboard.

## Data Structure

The dashboard uses the following data files:

### tasks.csv
Contains detailed information about marketing tasks including:
- Task ID, name, and scope
- Assignment details (who assigned to whom)
- Project association
- Content type
- Dates (assigned, delivered)
- Status updates
- Completion metrics

### projects.csv
Contains information about various real estate projects:
- Project ID and name
- Project phase and type
- Start and end dates
- Description

### team_members.csv
Details about team members:
- Member ID and name
- Role and department
- Start date
- Expertise

### content_types.csv
Categorization of different marketing content types:
- Content ID and type
- Description
- Average completion days
- Average revision cycles

## Deployment

To deploy this dashboard to Streamlit Sharing or any other hosting service:

1. Create a GitHub repository with your dashboard code
2. Set up an account on [Streamlit Sharing](https://streamlit.io/sharing)
3. Connect your GitHub repository
4. Configure the deployment settings
5. Launch your app

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Data provided by ATS Homekraft Marketing Department
- Built with [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/)
