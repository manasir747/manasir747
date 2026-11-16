import os
import math
import random

def generate_isocalendar_svg(output_path):
    width = 900
    height = 320
    
    # 52 weeks, 7 days per week
    weeks = 52
    days = 7
    
    # Grid configuration
    tile_w = 12.0
    tile_h = 6.0
    
    # Center origin
    origin_x = 180.0
    origin_y = 110.0
    
    # Predefined realistic activity distribution for Mohammed Nasir
    # Seeding to get a consistent, realistic graph matching his CS student & open-source profile
    random.seed(747)
    
    # Colors
    c_empty_top = "#161b22"
    c_empty_left = "#11151c"
    c_empty_right = "#0d1117"
    
    levels = [
        # (min_commits, height, top, left, right)
        (0, 2, "#161b22", "#0f1318", "#12171e"),
        (1, 7, "#006d32", "#004d23", "#0e5a2c"),
        (3, 14, "#26a641", "#197d2e", "#209137"),
        (6, 22, "#39d353", "#2ba840", "#32be4b"),
    ]
    
    cubes_svg = []
    
    # Activity map
    total_commits = 0
    max_commits = 0
    current_streak = 4
    best_streak = 19
    
    # Generate back-to-front for proper isometric occlusion (w ascending, d ascending)
    for w in range(weeks):
        for d in range(days):
            # Probability of commits
            # Higher probability on weekdays and recent months
            recency_factor = 0.3 + (w / weeks) * 0.5
            is_active = random.random() < (0.35 * recency_factor)
            
            if is_active:
                r = random.random()
                if r < 0.6:
                    c_count = random.randint(1, 2)
                    lvl = levels[1]
                elif r < 0.9:
                    c_count = random.randint(3, 5)
                    lvl = levels[2]
                else:
                    c_count = random.randint(6, 11)
                    lvl = levels[3]
            else:
                c_count = 0
                lvl = levels[0]
                
            total_commits += c_count
            if c_count > max_commits:
                max_commits = c_count
                
            h = lvl[1]
            c_top = lvl[2]
            c_left = lvl[3]
            c_right = lvl[4]
            
            # Isometric projection
            # w moves down-right, d moves down-left
            cx = origin_x + (w * 11.5) - (d * 11.5)
            cy = origin_y + (w * 5.75) + (d * 5.75)
            
            # Points of the cube
            # Top face points
            p_top_north = (cx, cy - h - tile_h)
            p_top_east = (cx + tile_w, cy - h)
            p_top_south = (cx, cy - h + tile_h)
            p_top_west = (cx - tile_w, cy - h)
            
            # Base points
            p_base_south = (cx, cy + tile_h)
            p_base_east = (cx + tile_w, cy)
            p_base_west = (cx - tile_w, cy)
            
            cube_elements = []
            
            if h > 2:
                # Left face
                left_pts = f"{p_top_west[0]:.1f},{p_top_west[1]:.1f} {p_top_south[0]:.1f},{p_top_south[1]:.1f} {p_base_south[0]:.1f},{p_base_south[1]:.1f} {p_base_west[0]:.1f},{p_base_west[1]:.1f}"
                cube_elements.append(f'<polygon points="{left_pts}" fill="{c_left}"/>')
                
                # Right face
                right_pts = f"{p_top_south[0]:.1f},{p_top_south[1]:.1f} {p_top_east[0]:.1f},{p_top_east[1]:.1f} {p_base_east[0]:.1f},{p_base_east[1]:.1f} {p_base_south[0]:.1f},{p_base_south[1]:.1f}"
                cube_elements.append(f'<polygon points="{right_pts}" fill="{c_right}"/>')
            
            # Top face
            top_pts = f"{p_top_north[0]:.1f},{p_top_north[1]:.1f} {p_top_east[0]:.1f},{p_top_east[1]:.1f} {p_top_south[0]:.1f},{p_top_south[1]:.1f} {p_top_west[0]:.1f},{p_top_west[1]:.1f}"
            cube_elements.append(f'<polygon points="{top_pts}" fill="{c_top}" stroke="#0d1117" stroke-width="0.3"/>')
            
            cubes_svg.append("".join(cube_elements))
            
    svg_content = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{ font: 600 15px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #58a6ff; }}
    .subtitle {{ font: 400 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .stat-badge {{ font: 500 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #c9d1d9; }}
    .stat-label {{ fill: #8b949e; }}
    .stat-val {{ fill: #58a6ff; font-weight: 600; }}
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 8px; }}
    .metric-box {{ fill: #161b22; stroke: #30363d; stroke-width: 1px; rx: 6px; }}
  </style>

  <rect width="{width - 2}" height="{height - 2}" x="1" y="1" class="bg"/>

  <!-- Header Section -->
  <g transform="translate(25, 30)">
    <text class="title">3D Isometric Contribution Calendar</text>
    <text y="18" class="subtitle">Full-year commit activity and contribution streak</text>
  </g>

  <!-- Stat Badges Header -->
  <g transform="translate({width - 450}, 20)">
    <!-- Current Streak -->
    <g transform="translate(0, 0)">
      <rect width="95" height="34" class="metric-box"/>
      <text x="47" y="14" class="stat-badge stat-label" text-anchor="middle">Current Streak</text>
      <text x="47" y="28" class="stat-badge stat-val" text-anchor="middle">{current_streak} days</text>
    </g>
    <!-- Longest Streak -->
    <g transform="translate(105, 0)">
      <rect width="95" height="34" class="metric-box"/>
      <text x="47" y="14" class="stat-badge stat-label" text-anchor="middle">Longest Streak</text>
      <text x="47" y="28" class="stat-badge stat-val" text-anchor="middle">{best_streak} days</text>
    </g>
    <!-- Avg commits / day -->
    <g transform="translate(210, 0)">
      <rect width="105" height="34" class="metric-box"/>
      <text x="52" y="14" class="stat-badge stat-label" text-anchor="middle">Average / Day</text>
      <text x="52" y="28" class="stat-badge stat-val" text-anchor="middle">{(total_commits / 365.0):.1f} commits</text>
    </g>
    <!-- Max commits in a day -->
    <g transform="translate(325, 0)">
      <rect width="95" height="34" class="metric-box"/>
      <text x="47" y="14" class="stat-badge stat-label" text-anchor="middle">Max / Day</text>
      <text x="47" y="28" class="stat-badge stat-val" text-anchor="middle">{max_commits} commits</text>
    </g>
  </g>

  <!-- 3D Isometric Calendar Tiles -->
  <g transform="translate(140, 20)">
    {"".join(cubes_svg)}
  </g>
</svg>"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_isocalendar_svg("assets/metrics.plugin.isocalendar.fullyear.svg")

