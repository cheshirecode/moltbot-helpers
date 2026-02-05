"""
Template renderer for shared dashboard UI
"""

def render_dashboard_template(**kwargs):
    """Render the dashboard template with provided parameters."""
    
    # Default values
    defaults = {
        'title': 'OpenClaw Dashboard',
        'header_title': 'OpenClaw Task Management Dashboard',
        'subtitle': 'Visualizing tasks by project from database',
        'show_disclaimer': False,
        'disclaimer_text': '',
        'intro_title': 'Welcome to the Dashboard',
        'intro_text': 'This dashboard displays project and task information.',
        'project_label': 'project',
        'show_refresh_button': True,
        'api_base_url': '.',
        'projects_endpoint': 'api/projects',
        'project_detail_endpoint': 'api/project'
    }
    
    # Update defaults with provided values
    params = {**defaults, **kwargs}
    
    # Read the template
    with open('templates/dashboard.html', 'r') as f:
        template_content = f.read()
    
    # Replace placeholders
    html_content = template_content
    for key, value in params.items():
        placeholder = '{{ ' + key + ' }}'
        html_content = html_content.replace(placeholder, str(value))
    
    return html_content


def render_dashboard_for_main_system():
    """Render dashboard for the main OpenClaw system."""
    return render_dashboard_template(
        title='OpenClaw Task Management Dashboard',
        header_title='OpenClaw Task Management Dashboard',
        subtitle='Visualizing tasks by project from PostgreSQL database',
        show_disclaimer=False,
        intro_title='Welcome to the OpenClaw Dashboard',
        intro_text='This dashboard displays project and task information from your PostgreSQL database.',
        project_label='project',
        show_refresh_button=True,
        api_base_url='.',
        projects_endpoint='api/projects',
        project_detail_endpoint='api/project'
    )


def render_dashboard_for_demo_system():
    """Render dashboard for the public demo system."""
    return render_dashboard_template(
        title='OpenClaw Demo Dashboard',
        header_title='OpenClaw Demo Dashboard',
        subtitle='Showcasing task management capabilities',
        show_disclaimer=True,
        disclaimer_text='This is a demonstration system using synthetic data. The actual OpenClaw system operates independently with real data.',
        intro_title='Welcome to the OpenClaw Demo',
        intro_text='This dashboard showcases the task management capabilities of the OpenClaw system. All data shown here is synthetic and generated for demonstration purposes only.',
        project_label='demo project',
        show_refresh_button=False,
        api_base_url='.',
        projects_endpoint='api/demo/projects',
        project_detail_endpoint='api/demo/project'
    )