import os
import random

def generate_isocalendar_svg(output_path):
    width = 890
    height = 290
    
    # 52 weeks, 7 days per week
    weeks = 52
    days = 7
    
    # Cube geometry
    tile_w = 6.8
    tile_h = 3.6
    
    # Isometric grid step vectors
    # Moving along weeks moves primarily right and slightly up/down
    step_w_x = 14.5
    step_w_y = -1.1
    
    # Moving along days moves down and slightly left
    step_d_x = -6.5
    step_d_y = 11.2
    
    # Origin positioned so min_x >= 45 and max_x <= width - 45
    origin_x = 95.0
    origin_y = 158.0
    
    random.seed(747)
    
    levels = [
        # (min_commits, height, top, left, right)
        (0, 0, "#161b22", "#0f1318", "#12171e"),
        (1, 5, "#006d32", "#004d23", "#0e5a2c"),
        (3, 11, "#26a641", "#197d2e", "#209137"),
        (6, 18, "#39d353", "#2ba840", "#32be4b"),
    ]
    
    # Pre-generate counts for realistic timeline
    # Months of the year have activity spikes
    activity_grid = []
    total_commits = 0
    max_commits = 0
    
    for w in range(weeks):
        week_data = []
        for d in range(days):
            # Recency & pattern weighting
            recency = 0.4 + (w / weeks) * 0.6
            is_weekend = (d == 0 or d == 6)
            prob = 0.45 * recency if not is_weekend else 0.25 * recency
            
            if random.random() < prob:
                r = random.random()
                if r < 0.65:
                    c = random.randint(1, 2)
                    lvl = levels[1]
                elif r < 0.90:
                    c = random.randint(3, 5)
                    lvl = levels[2]
                else:
                    c = random.randint(6, 11)
                    lvl = levels[3]
            else:
                c = 0
                lvl = levels[0]
                
            total_commits += c
            if c > max_commits:
                max_commits = c
            week_data.append((c, lvl))
        activity_grid.append(week_data)
        
    current_streak = 4
    best_streak = 19
    avg_per_day = round(total_commits / 365.0, 1)
    
    # Painter's Algorithm:
    # Back to front order:
    # Back-most day is d=0, front-most is d=6
    # For weeks, w=0 to w=51 can be drawn column by column or diagonal by diagonal
    # Since step_w_x > 2*tile_w, columns barely overlap horizontally.
    # To be strictly correct: sort tiles by depth (cy) ascending
    tiles_to_draw = []
    for w in range(weeks):
        for d in range(days):
            c, lvl = activity_grid[w][d]
            h = lvl[1]
            cx = origin_x + (w * step_w_x) + (d * step_d_x)
            cy = origin_y + (w * step_w_y) + (d * step_d_y)
            # depth key: back elements (smaller cy) first, front elements (larger cy) last
            depth_key = (cy, cx)
            tiles_to_draw.append((depth_key, cx, cy, h, lvl))
            
    tiles_to_draw.sort(key=lambda t: t[0])
    
    cubes_svg = []
    for _, cx, cy, h, lvl in tiles_to_draw:
        c_top = lvl[2]
        c_left = lvl[3]
        c_right = lvl[4]
        
        # Base tile points
        p_base_north = (cx, cy - tile_h)
        p_base_east = (cx + tile_w, cy)
        p_base_south = (cx, cy + tile_h)
        p_base_west = (cx - tile_w, cy)
        
        # Top points (lifted by h)
        p_top_north = (cx, cy - h - tile_h)
        p_top_east = (cx + tile_w, cy - h)
        p_top_south = (cx, cy - h + tile_h)
        p_top_west = (cx - tile_w, cy - h)
        
        if h > 0:
            # Left Face
            left_pts = f"{p_top_west[0]:.1f},{p_top_west[1]:.1f} {p_top_south[0]:.1f},{p_top_south[1]:.1f} {p_base_south[0]:.1f},{p_base_south[1]:.1f} {p_base_west[0]:.1f},{p_base_west[1]:.1f}"
            cubes_svg.append(f'<polygon points="{left_pts}" fill="{c_left}"/>')
            
            # Right Face
            right_pts = f"{p_top_south[0]:.1f},{p_top_south[1]:.1f} {p_top_east[0]:.1f},{p_top_east[1]:.1f} {p_base_east[0]:.1f},{p_base_east[1]:.1f} {p_base_south[0]:.1f},{p_base_south[1]:.1f}"
            cubes_svg.append(f'<polygon points="{right_pts}" fill="{c_right}"/>')
            
            # Top Face
            top_pts = f"{p_top_north[0]:.1f},{p_top_north[1]:.1f} {p_top_east[0]:.1f},{p_top_east[1]:.1f} {p_top_south[0]:.1f},{p_top_south[1]:.1f} {p_top_west[0]:.1f},{p_top_west[1]:.1f}"
            cubes_svg.append(f'<polygon points="{top_pts}" fill="{c_top}" stroke="#0d1117" stroke-width="0.3"/>')
        else:
            # Flat tile (empty day)
            flat_pts = f"{p_base_north[0]:.1f},{p_base_north[1]:.1f} {p_base_east[0]:.1f},{p_base_east[1]:.1f} {p_base_south[0]:.1f},{p_base_south[1]:.1f} {p_base_west[0]:.1f},{p_base_west[1]:.1f}"
            cubes_svg.append(f'<polygon points="{flat_pts}" fill="{c_top}" stroke="#0d1117" stroke-width="0.4"/>')

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
      <text x="52" y="28" class="stat-badge stat-val" text-anchor="middle">{avg_per_day} commits</text>
    </g>
    <!-- Max commits in a day -->
    <g transform="translate(325, 0)">
      <rect width="95" height="34" class="metric-box"/>
      <text x="47" y="14" class="stat-badge stat-label" text-anchor="middle">Max / Day</text>
      <text x="47" y="28" class="stat-badge stat-val" text-anchor="middle">{max_commits} commits</text>
    </g>
  </g>

  <!-- 3D Isometric Calendar Grid -->
  <g>
    {"".join(cubes_svg)}
  </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_isocalendar_svg("assets/metrics.plugin.isocalendar.fullyear.svg")
    generate_isocalendar_svg("assets/isocalendar.svg")
