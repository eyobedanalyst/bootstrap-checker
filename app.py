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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .motto {
        font-style: italic;
        color: #4F46E5;
        font-size: 1.3rem;
        font-weight: 500;
        text-align: center;
    }
    .grade-display {
        text-align: center;
        font-size: 4rem;
        font-weight: bold;
        color: #4F46E5;
        padding: 2rem 0;
    }
    .found-class {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        margin: 0.25rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    .missing-class {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        margin: 0.25rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    .suggestion-box {
        background-color: #DBEAFE;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
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

def fetch_github_html(username):
    """Fetch index.html from GitHub Pages repository"""
    try:
        url = f"https://raw.githubusercontent.com/{username}/{username}.github.io/main/index.html"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.text, None
        else:
            return None, f"Could not fetch index.html (Status code: {response.status_code})"
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching repository: {str(e)}"

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🎓 Mr Eyobed's Auto Grader")
st.markdown('<p class="motto">"Do things genuinely"</p>', unsafe_allow_html=True)
st.markdown("**Bootstrap Class Checker**")
st.markdown('</div>', unsafe_allow_html=True)

# Input form
with st.container():
    st.markdown("### 📋 Student Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        student_name = st.text_input("👤 Student Name", placeholder="Enter your full name")
    
    with col2:
        github_username = st.text_input("🐙 GitHub Username", placeholder="Enter your GitHub username")
    
    if github_username:
        st.info(f"📍 Will check: `https://github.com/{github_username}/{github_username}.github.io`")
    
    submit_button = st.button("📝 Submit for Grading", type="primary", use_container_width=True)

# Process submission
if submit_button:
    if not student_name.strip() or not github_username.strip():
        st.error("⚠️ Please enter both your name and GitHub username!")
    else:
        with st.spinner("🔍 Fetching and analyzing your code..."):
            html_content, error = fetch_github_html(github_username.strip())
            
            if error:
                st.error(f"❌ **Error:** {error}")
                st.warning("""
                **Make sure:**
                1. Your GitHub username is correct
                2. You have a repository named `{username}.github.io`
                3. There's an `index.html` file in the `main` branch
                4. The repository is public
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
    <p><strong>Note:</strong> Make sure your GitHub repository is public and named as <code>username.github.io</code> 
    with an <code>index.html</code> file in the main branch.</p>
</div>
""", unsafe_allow_html=True)