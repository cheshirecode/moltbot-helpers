"""
Shared UI Components for OpenClaw Systems
Reusable components for both main dashboard and demo
"""

import json
from datetime import datetime


class ChartComponent:
    """Reusable chart component with multiple visualization options."""
    
    @staticmethod
    def create_bar_chart(canvas_id, title, data_dict, colors=None):
        """Create a bar chart."""
        if colors is None:
            colors = [
                'rgba(67, 97, 238, 0.7)', 'rgba(76, 201, 240, 0.7)',
                'rgba(247, 37, 133, 0.7)', 'rgba(63, 55, 201, 0.7)',
                'rgba(118, 89, 171, 0.7)', 'rgba(25, 118, 210, 0.7)'
            ]
        
        labels = list(data_dict.keys())
        data = list(data_dict.values())
        
        chart_config = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': title,
                    'data': data,
                    'backgroundColor': colors[:len(data)],
                    'borderColor': [c.replace('0.7', '1') for c in colors[:len(data)]],
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': title
                    },
                    'legend': {'display': True}
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'ticks': {'precision': 0}
                    }
                }
            }
        }
        
        return f"""
        <div class="chart-container">
            <canvas id="{canvas_id}"></canvas>
        </div>
        <script>
            const ctx_{canvas_id} = document.getElementById('{canvas_id}').getContext('2d');
            new Chart(ctx_{canvas_id}, {json.dumps(chart_config)});
        </script>
        """
    
    @staticmethod
    def create_doughnut_chart(canvas_id, title, data_dict, colors=None):
        """Create a doughnut chart."""
        if colors is None:
            colors = [
                'rgba(67, 97, 238, 0.7)', 'rgba(76, 201, 240, 0.7)',
                'rgba(247, 37, 133, 0.7)', 'rgba(63, 55, 201, 0.7)',
                'rgba(118, 89, 171, 0.7)', 'rgba(25, 118, 210, 0.7)'
            ]
        
        labels = list(data_dict.keys())
        data = list(data_dict.values())
        
        chart_config = {
            'type': 'doughnut',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': title,
                    'data': data,
                    'backgroundColor': colors[:len(data)],
                    'borderColor': [c.replace('0.7', '1') for c in colors[:len(data)]],
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': title
                    },
                    'legend': {'display': True}
                }
            }
        }
        
        return f"""
        <div class="chart-container">
            <canvas id="{canvas_id}"></canvas>
        </div>
        <script>
            const ctx_{canvas_id} = document.getElementById('{canvas_id}').getContext('2d');
            new Chart(ctx_{canvas_id}, {json.dumps(chart_config)});
        </script>
        """


class TableComponent:
    """Reusable table component with sorting and filtering."""
    
    @staticmethod
    def create_data_table(id, headers, rows, sortable=True, filterable=True):
        """Create a data table with optional sorting and filtering."""
        table_html = f'<table id="{id}" class="data-table">'
        
        # Add header
        table_html += '<thead><tr>'
        for header in headers:
            if sortable:
                table_html += f'<th onclick="sortTable(\'{id}\', \'{header.lower()}\')">{header}</th>'
            else:
                table_html += f'<th>{header}</th>'
        table_html += '</tr></thead>'
        
        # Add filter row if enabled
        if filterable:
            table_html += '<tbody class="filterable"><tr class="filter-row">'
            for header in headers:
                table_html += f'<td><input type="text" placeholder="Filter {header}..." onchange="filterTable(\'{id}\', \'{header.lower()}\', this.value)"></td>'
            table_html += '</tr>'
        
        # Add data rows
        table_html += '<tbody class="data-body">'
        for row in rows:
            table_html += '<tr>'
            for cell in row:
                table_html += f'<td>{cell}</td>'
            table_html += '</tr>'
        table_html += '</tbody></table>'
        
        return table_html


class ModalComponent:
    """Reusable modal component."""
    
    @staticmethod
    def create_modal(id, title, content, footer_content=""):
        """Create a modal component."""
        return f"""
        <div id="{id}" class="modal" style="display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background-color:rgba(0,0,0,0.5);">
            <div class="modal-content" style="background-color:#fefefe; margin:15% auto; padding:20px; border:1px solid #888; width:80%; border-radius:8px;">
                <div class="modal-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <h3>{title}</h3>
                    <span class="close" onclick="document.getElementById('{id}').style.display='none'" style="font-size:28px; font-weight:bold; cursor:pointer;">&times;</span>
                </div>
                <div class="modal-body">
                    {content}
                </div>
                <div class="modal-footer" style="margin-top:15px; padding-top:15px; border-top:1px solid #eee;">
                    {footer_content}
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def show_modal_js(id):
        """JavaScript to show modal."""
        return f"document.getElementById('{id}').style.display='block';"


class FormComponent:
    """Reusable form component with validation."""
    
    @staticmethod
    def create_form(id, fields, submit_handler=None):
        """Create a form with validation."""
        form_html = f'<form id="{id}" class="universal-form">'
        
        for field in fields:
            field_type = field.get('type', 'text')
            field_label = field.get('label', field['name'])
            field_name = field['name']
            field_required = field.get('required', False)
            field_placeholder = field.get('placeholder', '')
            field_options = field.get('options', [])
            
            required_attr = 'required' if field_required else ''
            
            if field_type == 'select':
                form_html += f'<div class="form-group"><label for="{field_name}">{field_label}</label>'
                form_html += f'<select id="{field_name}" name="{field_name}" {required_attr}>'
                for option in field_options:
                    form_html += f'<option value="{option}">{option}</option>'
                form_html += '</select></div>'
            elif field_type == 'textarea':
                form_html += f'<div class="form-group"><label for="{field_name}">{field_label}</label>'
                form_html += f'<textarea id="{field_name}" name="{field_name}" placeholder="{field_placeholder}" {required_attr}></textarea></div>'
            else:
                form_html += f'<div class="form-group"><label for="{field_name}">{field_label}</label>'
                form_html += f'<input type="{field_type}" id="{field_name}" name="{field_name}" placeholder="{field_placeholder}" {required_attr}></div>'
        
        submit_btn = f'<button type="submit" onclick="{submit_handler}(\'{id}\')"' if submit_handler else '<button type="submit"'
        form_html += f'{submit_btn}>Submit</button></form>'
        
        return form_html


class StateManager:
    """Centralized state management system."""
    
    def __init__(self):
        self.state = {}
        self.listeners = {}
    
    def set_state(self, key, value):
        """Set a state value."""
        old_value = self.state.get(key)
        self.state[key] = value
        
        # Notify listeners if value changed
        if old_value != value and key in self.listeners:
            for listener in self.listeners[key]:
                listener(key, old_value, value)
    
    def get_state(self, key, default=None):
        """Get a state value."""
        return self.state.get(key, default)
    
    def subscribe(self, key, callback):
        """Subscribe to state changes."""
        if key not in self.listeners:
            self.listeners[key] = []
        self.listeners[key].append(callback)
    
    def unsubscribe(self, key, callback):
        """Unsubscribe from state changes."""
        if key in self.listeners and callback in self.listeners[key]:
            self.listeners[key].remove(callback)


class ThemeManager:
    """CSS theme management system."""
    
    @staticmethod
    def get_css_variables(theme='default'):
        """Get CSS variables for a specific theme."""
        themes = {
            'default': {
                '--primary-color': '#4361ee',
                '--secondary-color': '#3f37c9',
                '--success-color': '#4cc9f0',
                '--warning-color': '#f72585',
                '--light-bg': '#f8f9fa',
                '--dark-text': '#212529',
                '--border-color': '#dee2e6'
            },
            'dark': {
                '--primary-color': '#4895ef',
                '--secondary-color': '#4361ee',
                '--success-color': '#4cc9f0',
                '--warning-color': '#f72585',
                '--light-bg': '#212529',
                '--dark-text': '#f8f9fa',
                '--border-color': '#495057'
            },
            'minimal': {
                '--primary-color': '#6a4c93',
                '--secondary-color': '#1982c4',
                '--success-color': '#8ac926',
                '--warning-color': '#ffca3a',
                '--light-bg': '#f0f0f0',
                '--dark-text': '#333333',
                '--border-color': '#cccccc'
            }
        }
        
        selected_theme = themes.get(theme, themes['default'])
        css_vars = ':root {\n'
        for var, value in selected_theme.items():
            css_vars += f'  {var}: {value};\n'
        css_vars += '}'
        
        return css_vars


# Example usage functions
def render_dashboard_card(title, content, card_class="card"):
    """Render a standard dashboard card."""
    return f"""
    <div class="{card_class}">
        <h3 class="card-title">{title}</h3>
        {content}
    </div>
    """

def render_stats_grid(stats):
    """Render a grid of statistics."""
    grid_html = '<div class="stats-grid">'
    for stat in stats:
        grid_html += f"""
        <div class="stat-card">
            <div class="stat-value">{stat['value']}</div>
            <div class="stat-label">{stat['label']}</div>
        </div>
        """
    grid_html += '</div>'
    return grid_html


# JavaScript utilities for client-side functionality
JS_UTILS = """
<script>
// Sorting function for tables
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('.data-body');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.toLowerCase();
        const bValue = b.cells[columnIndex].textContent.toLowerCase();
        return aValue.localeCompare(bValue);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// Filtering function for tables
function filterTable(tableId, columnIndex, filterValue) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('.data-body');
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cellValue = row.cells[columnIndex].textContent.toLowerCase();
        const isVisible = cellValue.includes(filterValue.toLowerCase());
        row.style.display = isVisible ? '' : 'none';
    });
}

// Theme switching function
function switchTheme(themeName) {
    // In a real implementation, this would apply the theme
    localStorage.setItem('theme', themeName);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'default';
    switchTheme(savedTheme);
});
</script>
"""