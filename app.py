import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Page configuration
st.set_page_config(
    page_title="Mr Eyobed's Auto Grader",
    page_icon="🎓",
    layout="centered"
)

# Custom CSS with white background
st.markdown("""
<style>
    .stApp {
        background-color: #0D1117;
        color: #C9D1D9;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background-color: #0D1117;
    }
    .motto {
        font-style: italic;
        color: #58A6FF;
        font-size: 1.3rem;
        font-weight: 500;
        text-align: center;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
    }
    .grade-display {
        text-align: center;
        font-size: 4rem;
        font-weight: bold;
        color: #00FF00;
        padding: 2rem 0;
        background-color: #0D1117;
        text-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        font-family: 'Courier New', monospace;
    }
    .found-class {
        background-color: #1F6E43;
        color: #3FB950;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem;
        display: inline-block;
        font-size: 0.9rem;
        font-family: 'Courier New', monospace;
        border: 1px solid #3FB950;
        box-shadow: 0 0 5px rgba(63, 185, 80, 0.3);
    }
    .missing-class {
        background-color: #5A1E1E;
        color: #F85149;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem;
        display: inline-block;
        font-size: 0.9rem;
        font-family: 'Courier New', monospace;
        border: 1px solid #F85149;
        box-shadow: 0 0 5px rgba(248, 81, 73, 0.3);
    }
    .suggestion-box {
        background-color: #161B22;
        border-left: 4px solid #58A6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        box-shadow: 0 0 10px rgba(88, 166, 255, 0.2);
    }
    div[data-testid="stForm"] {
        background-color: #0D1117;
    }
    /* Additional tech-vibe styling */
    h1, h2, h3 {
        color: #58A6FF !important;
        font-family: 'Courier New', monospace;
    }
    .stTextInput input {
        background-color: #161B22 !important;
        color: #C9D1D9 !important;
        border: 1px solid #30363D !important;
        font-family: 'Courier New', monospace;
    }
    .stButton button {
        background-color: #238636 !important;
        color: #FFFFFF !important;
        border: 1px solid #2EA043 !important;
        font-family: 'Courier New', monospace;
        box-shadow: 0 0 10px rgba(46, 160, 67, 0.4);
    }
    .stButton button:hover {
        background-color: #2EA043 !important;
        box-shadow: 0 0 15px rgba(46, 160, 67, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# Required Bootstrap classes
REQUIRED_CLASSES = [
    'text-center',
    'text-primary',
    'fw-bold',
    'text-success',
    'text-danger',
    'text-warning',
    'text-info',
    'text-muted',
    'mb-4',
    'bg-primary',
    'text-white',
    'bg-success',
    'bg-danger',
    'bg-warning',
    'bg-dark',
    'text-light'
]

def check_bootstrap_classes(html_content):
    """Check for required Bootstrap classes in HTML content"""
    found_classes = []
    missing_classes = []
    
    for class_name in REQUIRED_CLASSES:
        # Use regex to find class in class attributes
        pattern = rf'class=["' + "'][^\"']*\\b" + re.escape(class_name) + r"\\b[^\"']*[\"']"
        if re.search(pattern, html_content):
            found_classes.append(class_name)
        else:
            missing_classes.append(class_name)
    
    return found_classes, missing_classes

def generate_suggestions(missing_classes, grade):
    """Generate suggestions based on missing classes"""
    suggestions = []
    
    if len(missing_classes) > 0:
        suggestions.append(f"❌ Missing {len(missing_classes)} required Bootstrap classes")
        
        missing_text = [c for c in missing_classes if c.startswith('text-')]
        missing_bg = [c for c in missing_classes if c.startswith('bg-')]
        missing_utility = [c for c in missing_classes if not c.startswith('text-') and not c.startswith('bg-')]
        
        if missing_text:
            suggestions.append(f"📝 Add text utility classes: {', '.join(missing_text)}")
        if missing_bg:
            suggestions.append(f"🎨 Add background classes: {', '.join(missing_bg)}")
        if missing_utility:
            suggestions.append(f"🔧 Add utility classes: {', '.join(missing_utility)}")
    
    if grade == 10:
        suggestions.append("🎉 Perfect! All required Bootstrap classes are present!")
        suggestions.append("✨ Consider adding more Bootstrap components for extra practice")
    elif grade >= 7:
        suggestions.append("👍 Great work! Just a few more classes needed")
    elif grade >= 5:
        suggestions.append("📚 Good start! Review Bootstrap documentation for missing classes")
    else:
        suggestions.append("💪 Keep practicing! Make sure to include all required Bootstrap utility classes")
    
    return suggestions

def fetch_html_from_url(url):
    """Fetch HTML content from a given URL"""
    try:
        # Clean the URL
        url = url.strip()
        
        # If it's a GitHub Pages URL, convert to raw content URL
        if 'github.io' in url:
            # Extract username and repo from GitHub Pages URL
            # Example: https://username.github.io/repo/ or https://username.github.io/
            parts = url.replace('https://', '').replace('http://', '').split('/')
            username = parts[0].replace('.github.io', '')
            
            # Try different possible paths for index.html
            possible_paths = [
                f"https://raw.githubusercontent.com/{username}/{username}.github.io/main/index.html",
                f"https://raw.githubusercontent.com/{username}/{username}.github.io/master/index.html",
            ]
            
            # If there's a repo path in the URL
            if len(parts) > 1 and parts[1]:
                repo = parts[1]
                possible_paths.insert(0, f"https://raw.githubusercontent.com/{username}/{repo}/main/index.html")
                possible_paths.insert(1, f"https://raw.githubusercontent.com/{username}/{repo}/master/index.html")
            
            # Try each possible path
            for path in possible_paths:
                try:
                    response = requests.get(path, timeout=10)
                    if response.status_code == 200:
                        return response.text, None
                except:
                    continue
            
            return None, "Could not fetch index.html from any of the attempted paths"
        
        # For direct raw GitHub URLs or other URLs
        else:
            # Ensure it's a raw GitHub URL if it's a GitHub link
            if 'github.com' in url and 'raw.githubusercontent.com' not in url:
                url = url.replace('github.com', 'raw.githubusercontent.com')
                url = url.replace('/blob/', '/')
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.text, None
            else:
                return None, f"Could not fetch HTML (Status code: {response.status_code})"
                
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching URL: {str(e)}"

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🎓 Mr Eyobed's Auto Grader")
st.markdown('<p class="motto">"Do things genuinely"</p>', unsafe_allow_html=True)
st.markdown("**Bootstrap Class Checker**")
st.markdown('</div>', unsafe_allow_html=True)

# Input form
with st.container():
    st.markdown("### 📋 Student Information")
    
    student_name = st.text_input("👤 Student Name", placeholder="Enter your full name")
    
    github_url = st.text_input(
        "🔗 GitHub Public Link (where index.html is located)", 
        placeholder="e.g., https://username.github.io or https://raw.githubusercontent.com/.../index.html"
    )
    
    st.info("""
    **Accepted URL formats:**
    - GitHub Pages: `https://username.github.io`
    - GitHub Pages with repo: `https://username.github.io/repo-name`
    - Direct raw link: `https://raw.githubusercontent.com/username/repo/main/index.html`
    """)
    
    submit_button = st.button("📝 Submit for Grading", type="primary", use_container_width=True)

# Process submission
if submit_button:
    if not student_name.strip() or not github_url.strip():
        st.error("⚠️ Please enter both your name and GitHub public link!")
    else:
        with st.spinner("🔍 Fetching and analyzing your code..."):
            html_content, error = fetch_html_from_url(github_url.strip())
            
            if error:
                st.error(f"❌ **Error:** {error}")
                st.warning("""
                **Make sure:**
                1. Your URL is correct and publicly accessible
                2. The repository/page contains an `index.html` file
                3. The repository is public (not private)
                4. You're using one of the accepted URL formats shown above
                """)
            else:
                # Check classes
                found_classes, missing_classes = check_bootstrap_classes(html_content)
                
                # Calculate grade
                grade = round((len(found_classes) / len(REQUIRED_CLASSES)) * 10)
                
                # Generate suggestions
                suggestions = generate_suggestions(missing_classes, grade)
                
                # Display results
                st.success("✅ Successfully analyzed your code!")
                
                # Grade display
                st.markdown("---")
                st.markdown(f"### 🎯 Results for {student_name}")
                st.markdown(f'<div class="grade-display">{grade}/10</div>', unsafe_allow_html=True)
                
                # Progress bar
                st.progress(grade / 10)
                st.markdown(f"**{len(found_classes)} out of {len(REQUIRED_CLASSES)} classes found**")
                
                # Found classes
                if found_classes:
                    st.markdown("---")
                    st.markdown(f"### ✅ Found Classes ({len(found_classes)})")
                    found_html = "".join([f'<span class="found-class">{cls}</span>' for cls in found_classes])
                    st.markdown(found_html, unsafe_allow_html=True)
                
                # Missing classes
                if missing_classes:
                    st.markdown("---")
                    st.markdown(f"### ❌ Missing Classes ({len(missing_classes)})")
                    missing_html = "".join([f'<span class="missing-class">{cls}</span>' for cls in missing_classes])
                    st.markdown(missing_html, unsafe_allow_html=True)
                
                # Suggestions
                st.markdown("---")
                st.markdown("### 💡 Suggestions & Feedback")
                suggestions_html = '<div class="suggestion-box">'
                for suggestion in suggestions:
                    suggestions_html += f"<p>• {suggestion}</p>"
                suggestions_html += '</div>'
                st.markdown(suggestions_html, unsafe_allow_html=True)
                
                # Celebration
                if grade == 10:
                    st.balloons()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 2rem 0;'>
    <p><strong>Tip:</strong> You can use your GitHub Pages URL, repository URL, or direct raw link to your index.html file.</p>
</div>
""", unsafe_allow_html=True)