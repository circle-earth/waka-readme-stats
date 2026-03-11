import re
from manager_file import FileManager as FM

def create_svg_table(data_list, title="Programming Languages", save_path="assets/stats.svg"):
    """
    Creates an SVG table displaying statistics with progress bars. 
    Matches the user's provided design.
    """
    
    # SVG Constants
    width = 600
    row_height = 45
    header_height = 50
    padding = 20
    
    # Calculate dynamic height
    num_rows = len(data_list)
    total_height = header_height + (num_rows + 1) * row_height + padding * 2
    
    # SVG Header
    svg_content = f"""<svg width="{width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .bg {{ fill: #0d1117; }}
      .border {{ stroke: #30363d; stroke-width: 1; fill: none; }}
      .title {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #c9d1d9; }}
      .header {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #c9d1d9; }}
      .text {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif; font-size: 14px; fill: #c9d1d9; }}
      .progress-bg {{ fill: #30363d; rx: 5; ry: 5; }}
      .progress-fill {{ rx: 5; ry: 5; }}
    </style>
  </defs>

  <!-- Background -->
  <rect class="bg" width="{width-2}" height="{total_height-2}" x="1" y="1" rx="5" ry="5"/>
  <rect class="border" width="{width-2}" height="{total_height-2}" x="1" y="1" rx="5" ry="5"/>

  <!-- Title Section -->
  <text x="{width/2}" y="30" class="title" text-anchor="middle">💬 {title}</text>
  <line x1="0" y1="{header_height}" x2="{width}" y2="{header_height}" class="border"/>

  <!-- Table Headers -->
  <g transform="translate(0, {header_height})">
    <text x="50" y="30" class="header">Language</text>
    <text x="300" y="30" class="header" text-anchor="middle">Time Spent</text>
    <text x="480" y="30" class="header" text-anchor="middle">Progress</text>
    <line x1="0" y1="{row_height}" x2="{width}" y2="{row_height}" class="border"/>
  </g>
"""

    # Add Data Rows
    for i, item in enumerate(data_list):
        name = item.get("name", "Unknown")
        time_spent = item.get("text", "0 hrs")
        percent = item.get("percent", 0.0)
        
        # Color logic mapping (Simplified for demonstration)
        # Assuming you will pass colors according to language, here is a default mapping
        color_map = {
            "Python": "#fdb660",
            "Go": "#d04141",
            "JavaScript": "#d04141",
            "YML": "#d04141",
            "Java": "#d04141",
            "HTML": "#d04141"
        }
        
        bar_color = color_map.get(name, "#3fb950") # Default green 
        
        # Calculate bar width based on percentage (max width 120)
        bar_width = max((percent / 100.0) * 120, 10) 
        
        y_offset = header_height + row_height + (i * row_height)
        
        row_content = f"""
  <!-- Row {i+1} -->
  <g transform="translate(0, {y_offset})">
    <text x="30" y="28" class="text">{name}</text>
    <text x="300" y="28" class="text" text-anchor="middle">{time_spent}</text>
    
    <!-- Progress Bar -->
    <rect x="420" y="12" width="120" height="20" class="progress-bg"/>
    <rect x="420" y="12" width="{bar_width}" height="20" class="progress-fill" fill="{bar_color}"/>
    <text x="480" y="27" class="text" text-anchor="middle" font-size="12">{percent:.2f}%</text>
    
    <!-- Divider -->
    <line x1="0" y1="{row_height}" x2="{width}" y2="{row_height}" class="border"/>
  </g>
"""
        svg_content += row_content

    # Add vertical column lines
    bottom_y = header_height + (num_rows + 1) * row_height
    svg_content += f"""
  <line x1="200" y1="{header_height}" x2="200" y2="{bottom_y}" class="border"/>
  <line x1="400" y1="{header_height}" x2="400" y2="{bottom_y}" class="border"/>
</svg>
"""

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    return f"![{title}](assets/{save_path.split('/')[-1]})\n\n"
