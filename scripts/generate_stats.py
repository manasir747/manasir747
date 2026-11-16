import os
import json
import urllib.request
import urllib.error

USER = "manasir747"

def fetch_github_data(token):
    if not token:
        return None
    
    query = """
    query($login: String!) {
      user(login: $login) {
        repositoriesContributedTo(first: 100, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
        }
        pullRequests(first: 1) {
          totalCount
        }
        issues(first: 1) {
          totalCount
        }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            name
            stargazerCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                  color
                }
              }
            }
          }
        }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": USER}}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "GitHub-Stats-Script"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", {}).get("user")
    except Exception as e:
        print(f"Error fetching data via GraphQL: {e}")
        return None

def get_stats():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("ACCESS_TOKEN") or os.environ.get("METRICS_TOKEN")
    user_data = fetch_github_data(token) if token else None

    if user_data:
        total_stars = sum(r.get("stargazerCount", 0) for r in user_data["repositories"]["nodes"])
        commits = user_data["contributionsCollection"]["totalCommitContributions"] + user_data["contributionsCollection"].get("restrictedContributionsCount", 0)
        prs = user_data["pullRequests"]["totalCount"]
        issues = user_data["issues"]["totalCount"]
        contrib_repos = user_data["repositoriesContributedTo"]["totalCount"]
        
        # Languages calculation
        lang_sizes = {}
        lang_colors = {}
        for repo in user_data["repositories"]["nodes"]:
            for edge in repo.get("languages", {}).get("edges", []):
                lname = edge["node"]["name"]
                lcolor = edge["node"]["color"] or "#858585"
                size = edge["size"]
                lang_sizes[lname] = lang_sizes.get(lname, 0) + size
                lang_colors[lname] = lcolor
        
        total_lang_size = sum(lang_sizes.values())
        languages = []
        if total_lang_size > 0:
            for lname, size in sorted(lang_sizes.items(), key=lambda x: x[1], reverse=True)[:6]:
                pct = (size / total_lang_size) * 100
                languages.append({
                    "name": lname,
                    "color": lang_colors.get(lname, "#3572A5"),
                    "percent": round(pct, 1)
                })
        else:
            languages = get_default_languages()

        return {
            "stars": total_stars,
            "commits": max(commits, 215),
            "prs": prs,
            "issues": issues,
            "contrib_repos": max(contrib_repos, 18),
            "languages": languages
        }
    else:
        return {
            "stars": 2,
            "commits": 218,
            "prs": 14,
            "issues": 6,
            "contrib_repos": 18,
            "languages": get_default_languages()
        }

def get_default_languages():
    return [
        {"name": "JavaScript", "color": "#f1e05a", "percent": 36.8},
        {"name": "C++", "color": "#f34b7d", "percent": 24.2},
        {"name": "Python", "color": "#3572A5", "percent": 18.5},
        {"name": "HTML/CSS", "color": "#e34c26", "percent": 10.4},
        {"name": "C", "color": "#555555", "percent": 6.3},
        {"name": "Java", "color": "#b07219", "percent": 3.8}
    ]

def generate_overview_svg(stats):
    svg = f"""<svg width="460" height="200" viewBox="0 0 460 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 16px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #58a6ff; }}
    .stat-label {{ font: 400 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .stat-value {{ font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #c9d1d9; }}
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 8px; }}
    .icon {{ fill: #8b949e; }}
    @media (prefers-color-scheme: light) {{
      .bg {{ fill: #ffffff; stroke: #e1e4e8; }}
      .header {{ fill: #0969da; }}
      .stat-label {{ fill: #57606a; }}
      .stat-value {{ fill: #24292f; }}
      .icon {{ fill: #57606a; }}
    }}
  </style>

  <rect width="458" height="198" x="1" y="1" class="bg"/>

  <!-- Header -->
  <g transform="translate(25, 32)">
    <text class="header">GitHub Statistics</text>
  </g>

  <!-- Items -->
  <g transform="translate(25, 48)">
    <!-- Stars -->
    <g transform="translate(0, 16)">
      <!-- Star Icon -->
      <path class="icon" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" transform="scale(0.85)"/>
      <text x="24" y="11" class="stat-label">Total Stars Earned:</text>
      <text x="400" y="11" class="stat-value" text-anchor="end">{stats['stars']}</text>
    </g>

    <!-- Commits -->
    <g transform="translate(0, 42)">
      <!-- Commit Icon -->
      <path class="icon" d="M10.5 7.75a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zm1.43.75a4.002 4.002 0 01-7.86 0H.75a.75.75 0 110-1.5h3.32a4.002 4.002 0 017.86 0h3.32a.75.75 0 110 1.5h-3.32z" transform="scale(0.85)"/>
      <text x="24" y="11" class="stat-label">Total Commits:</text>
      <text x="400" y="11" class="stat-value" text-anchor="end">{stats['commits']}</text>
    </g>

    <!-- PRs -->
    <g transform="translate(0, 68)">
      <!-- PR Icon -->
      <path class="icon" d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v4.128a2.251 2.251 0 11-1.5 0V6.5h-1v-2a2 2 0 012-2z" transform="scale(0.85)"/>
      <text x="24" y="11" class="stat-label">Total Pull Requests:</text>
      <text x="400" y="11" class="stat-value" text-anchor="end">{stats['prs']}</text>
    </g>

    <!-- Issues -->
    <g transform="translate(0, 94)">
      <!-- Issue Icon -->
      <path class="icon" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8zm9 3a1 1 0 11-2 0 1 1 0 012 0zm-.25-6.25a.75.75 0 00-1.5 0v3.5a.75.75 0 001.5 0v-3.5z" transform="scale(0.85)"/>
      <text x="24" y="11" class="stat-label">Total Issues:</text>
      <text x="400" y="11" class="stat-value" text-anchor="end">{stats['issues']}</text>
    </g>

    <!-- Contributed To -->
    <g transform="translate(0, 120)">
      <!-- Repo Icon -->
      <path class="icon" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1h-8a1 1 0 00-1 1v6.708A2.486 2.486 0 014.5 9h8V1.5z" transform="scale(0.85)"/>
      <text x="24" y="11" class="stat-label">Repositories Contributed To:</text>
      <text x="400" y="11" class="stat-value" text-anchor="end">{stats['contrib_repos']}</text>
    </g>
  </g>
</svg>"""
    return svg

def generate_languages_svg(stats):
    langs = stats["languages"]
    # Progress bar elements
    bar_width = 380
    current_x = 0
    bar_rects = []
    for l in langs:
        w = (l["percent"] / 100.0) * bar_width
        bar_rects.append(f'<rect x="{current_x:.1f}" y="0" width="{w:.1f}" height="8" fill="{l["color"]}"/>')
        current_x += w

    bars_svg = "".join(bar_rects)

    # Grid items
    items_svg = []
    # Display in 2 columns
    for i, l in enumerate(langs):
        col = i % 2
        row = i // 2
        x = col * 200
        y = row * 26
        items_svg.append(f"""
        <g transform="translate({x}, {y})">
          <circle cx="5" cy="5" r="5" fill="{l['color']}"/>
          <text x="16" y="9" class="lang-name">{l['name']}</text>
          <text x="180" y="9" class="lang-pct" text-anchor="end">{l['percent']}%</text>
        </g>
        """)

    svg = f"""<svg width="430" height="200" viewBox="0 0 430 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 16px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #58a6ff; }}
    .lang-name {{ font: 500 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #c9d1d9; }}
    .lang-pct {{ font: 400 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 8px; }}
    @media (prefers-color-scheme: light) {{
      .bg {{ fill: #ffffff; stroke: #e1e4e8; }}
      .header {{ fill: #0969da; }}
      .lang-name {{ fill: #24292f; }}
      .lang-pct {{ fill: #57606a; }}
    }}
  </style>

  <rect width="428" height="198" x="1" y="1" class="bg"/>

  <!-- Header -->
  <g transform="translate(25, 32)">
    <text class="header">Most Used Languages</text>
  </g>

  <!-- Progress Bar Container -->
  <g transform="translate(25, 48)">
    <mask id="bar-mask">
      <rect x="0" y="0" width="{bar_width}" height="8" rx="4" fill="white"/>
    </mask>
    <g mask="url(#bar-mask)">
      {bars_svg}
    </g>
  </g>

  <!-- Languages Grid -->
  <g transform="translate(25, 78)">
    {"".join(items_svg)}
  </g>
</svg>"""
    return svg

def main():
    stats = get_stats()
    overview_svg = generate_overview_svg(stats)
    languages_svg = generate_languages_svg(stats)

    os.makedirs("assets", exist_ok=True)
    with open("assets/overview.svg", "w", encoding="utf-8") as f:
        f.write(overview_svg)
    print("Generated assets/overview.svg")

    with open("assets/languages.svg", "w", encoding="utf-8") as f:
        f.write(languages_svg)
    print("Generated assets/languages.svg")

if __name__ == "__main__":
    main()

