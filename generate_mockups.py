import os

pages = [
    "main_page", "login", "news", "branchs", "user_profile",
    "account_profile", "transfer", "bill_type", "show_history", "summary"
]

shared_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-main: #F8FAFC;
    --bg-card: #FFFFFF;
    --bg-alt: #F1F5F9;
    --text-primary: #111827;
    --text-secondary: #4B5563;
    --text-muted: #6B7280;
    --accent-primary: #334155;
    --accent-hover: #1E293B;
    --border-color: #E5E7EB;
    
    --font-family: 'Inter', sans-serif;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: var(--font-family);
    background-color: var(--bg-main);
    color: var(--text-primary);
    line-height: 1.6;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

h1, h2, h3, h4 {
    line-height: 1.2;
    color: var(--text-primary);
    margin-bottom: 16px;
}

h1 { font-size: 48px; }
h2 { font-size: 36px; }
h3 { font-size: 28px; }
h4 { font-size: 22px; }
p { font-size: 16px; margin-bottom: 16px; color: var(--text-secondary); }
small { font-size: 14px; color: var(--text-muted); }

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px;
    width: 100%;
}

.navbar {
    background-color: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    padding: 16px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-logo {
    font-size: 24px;
    font-weight: 700;
    color: var(--accent-primary);
    text-decoration: none;
}

.nav-links {
    list-style: none;
    display: flex;
    gap: 24px;
    align-items: center;
}

.nav-links a {
    text-decoration: none;
    color: var(--text-secondary);
    font-weight: 500;
    transition: color 150ms ease;
}

.nav-links a:hover {
    color: var(--accent-primary);
}

.btn-primary {
    background-color: var(--accent-primary);
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 150ms ease;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.btn-primary:hover {
    background-color: var(--accent-hover);
}

.btn-secondary {
    background-color: #FFFFFF;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 16px;
    cursor: pointer;
    transition: all 150ms ease;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.btn-secondary:hover {
    border-color: var(--text-muted);
}

.card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.grid {
    display: grid;
    gap: 24px;
}
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }

.flex { display: flex; }
.flex-col { flex-direction: column; }
.gap-8 { gap: 8px; }
.gap-16 { gap: 16px; }
.gap-24 { gap: 24px; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }

.text-center { text-align: center; }
.mt-16 { margin-top: 16px; }
.mt-32 { margin-top: 32px; }
.mb-16 { margin-bottom: 16px; }
.mb-32 { margin-bottom: 32px; }

input, select, textarea {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-family: var(--font-family);
    font-size: 16px;
    color: var(--text-primary);
    background-color: var(--bg-card);
    transition: border-color 150ms ease;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--accent-primary);
}

label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--text-primary);
}
"""

def generate_html(name):
    title = name.replace("_", " ").title()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>36Bank - {title}</title>
    <link rel="stylesheet" href="shared.css">
    <link rel="stylesheet" href="{name}.css">
</head>
<body>
    <nav class="navbar">
        <a href="main_page.html" class="nav-logo">36Bank</a>
        <ul class="nav-links">
            <li><a href="main_page.html">Home</a></li>
            <li><a href="transfer.html">Transfer</a></li>
            <li><a href="show_history.html">History</a></li>
            <li><a href="summary.html">Summary</a></li>
            <li><a href="user_profile.html">Profile</a></li>
            <li><a href="login.html" class="btn-primary" style="padding: 8px 16px;">Login</a></li>
        </ul>
    </nav>
    <div class="container">
        <h1>{title}</h1>
        <div class="card">
            <p>Welcome to the {title} page.</p>
        </div>
    </div>
</body>
</html>
"""

with open("shared.css", "w") as f:
    f.write(shared_css)

for page in pages:
    html_file = f"{page}.html"
    css_file = f"{page}.css"
    
    with open(html_file, "w") as f:
        f.write(generate_html(page))
    
    with open(css_file, "w") as f:
        f.write(f"/* Specific styles for {page} */\n")

print("Generated files successfully.")
