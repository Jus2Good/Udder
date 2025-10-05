import streamlit as st
from datetime import datetime, timedelta
import random

# Page config
st.set_page_config(
    page_title="Rafiq - Your AI Career Assistant",
    page_icon="🤝",
    layout="wide"
)

# ============================================================================
# MOCK DATA & ML MODEL
# ============================================================================

# Simulated user profiles for testing
TEST_USERS = {
    'fatima_hassan': {
        'name': 'Fatima Hassan',
        'cv_refresh_count': 0,
        'days_since_last_refresh': 14,
        'profile_completeness': 68,
        'emp_cv_views_last_week': 3,
        'applications_count': 1,
        'unique_jobs_applied': 3,
        'login_count': 4,
        'unique_skills_added': 3,
        'job_searches': 5,
        'industry': 'Data Analytics'
    },
    'omar_khalil': {
        'name': 'Omar Khalil',
        'cv_refresh_count': 2,
        'days_since_last_refresh': 2,
        'profile_completeness': 45,
        'emp_cv_views_last_week': 0,
        'applications_count': 0,
        'unique_jobs_applied': 1,
        'login_count': 2,
        'unique_skills_added': 2,
        'job_searches': 8,
        'industry': 'Software Engineering'
    },
    'layla_mansour': {
        'name': 'Layla Mansour',
        'cv_refresh_count': 1,
        'days_since_last_refresh': 3,
        'profile_completeness': 85,
        'emp_cv_views_last_week': 8,
        'applications_count': 0,
        'unique_jobs_applied': 5,
        'login_count': 6,
        'unique_skills_added': 7,
        'job_searches': 12,
        'industry': 'Marketing'
    },
    'youssef_ahmed': {
        'name': 'Youssef Ahmed',
        'cv_refresh_count': 3,
        'days_since_last_refresh': 21,
        'profile_completeness': 55,
        'emp_cv_views_last_week': 1,
        'applications_count': 2,
        'unique_jobs_applied': 2,
        'login_count': 1,
        'unique_skills_added': 4,
        'job_searches': 3,
        'industry': 'Finance'
    },
    'amira_said': {
        'name': 'Amira Said',
        'cv_refresh_count': 0,
        'days_since_last_refresh': 7,
        'profile_completeness': 92,
        'emp_cv_views_last_week': 12,
        'applications_count': 5,
        'unique_jobs_applied': 8,
        'login_count': 10,
        'unique_skills_added': 9,
        'job_searches': 15,
        'industry': 'Project Management'
    }
}

# Mock ML Model (simulates XGBoost until real one is ready)
def mock_ml_prediction(user_features):
    """
    Simulates ML model predictions based on user behavioral features.
    Returns the best nudge recommendation with confidence score.
    """
    predictions = {}
    
    # Rule 1: Refresh CV if stale
    if user_features['days_since_last_refresh'] > 7:
        predictions['refresh_cv'] = 0.65 + (user_features['days_since_last_refresh'] - 7) * 0.02
    else:
        predictions['refresh_cv'] = 0.15
    
    # Rule 2: Add skills if profile incomplete
    if user_features['profile_completeness'] < 70:
        gap = 70 - user_features['profile_completeness']
        predictions['add_skill'] = 0.50 + (gap * 0.01)
    else:
        predictions['add_skill'] = 0.10
    
    # Rule 3: Apply to jobs if searching but not applying
    if user_features['job_searches'] > 3 and user_features['applications_count'] == 0:
        predictions['apply_job'] = 0.70
    elif user_features['job_searches'] > 0 and user_features['applications_count'] < 2:
        predictions['apply_job'] = 0.45
    else:
        predictions['apply_job'] = 0.20
    
    # Normalize to sum to 1.0
    total = sum(predictions.values())
    predictions = {k: v/total for k, v in predictions.items()}
    
    # Get top prediction
    top_nudge = max(predictions, key=predictions.get)
    confidence = predictions[top_nudge]
    
    return {
        'nudge': top_nudge,
        'confidence': confidence,
        'all_predictions': predictions,
        'expected_outcomes': {
            'refresh_cv': 'emp_cv_views',
            'add_skill': 'emp_contact_flips',
            'apply_job': 'emp_reveals'
        }[top_nudge]
    }

# ============================================================================
# CONVERSATION FLOWS
# ============================================================================

CONVERSATION_FLOWS = {
    'refresh_cv': {
        'initial': {
            'message': """Hey {name}! 👋 I've been analyzing your job search activity, and I found something that could really boost your visibility.

**What I noticed:**
Your profile got {emp_cv_views_last_week} employer views this week, but it's been {days_since_last_refresh} days since your last CV refresh.

**Here's what our data shows:**
Users in your situation who refresh their CV see an average of **3x more employer views** in the next week. I'm pretty confident ({confidence}% probability) this would help you too.

Want me to refresh it for you right now? Takes 2 seconds.""",
            'buttons': ['Yes, refresh it', 'Why does this help?', 'Not right now']
        },
        'why': {
            'message': """Great question! Here's what happens behind the scenes:

**The Algorithm:**
When you refresh, your profile moves to the top of "Recently Updated" lists that employers browse. It's like bumping a post on social media.

**The Data:**
I analyzed thousands of users with similar patterns to yours:
- {login_count} logins this week ✓
- {applications_count} applications ✓
- {days_since_last_refresh} days since last refresh ✓

72% of them got more employer views after refreshing, with an average increase of **5-8 new views** in the next 48 hours.

**Your Specific Situation:**
You're active (great!), but employers might not see you because older profiles get pushed down in search results.

Make sense? Should I refresh it?""",
            'buttons': ['Yes, refresh it', 'Maybe later']
        },
        'success': {
            'message': """Done! ✅ Your CV is now marked as "Updated today"

**What to expect:**
- Next 24-48 hours: 5-8 new employer views (based on prediction)
- Increased chance of contact flips (18% probability)
- Better visibility in employer searches

**Pro tip:** Our model found that users who refresh every 7-10 days stay consistently visible. Want me to remind you next week?""",
            'buttons': ['Yes, remind me', 'No thanks']
        },
        'remind_set': {
            'message': """Perfect! Reminder set for next Monday. 📅

By the way, I noticed your profile is {profile_completeness}% complete. While you're on a roll, want to quickly boost it? Adding 5-7 more skills could increase your contact flip rate even more.

(This was my second-best recommendation for you)""",
            'buttons': ['Sure, let\'s add skills', 'Maybe later', 'I\'m good for now']
        },
        'later': {
            'message': """No problem! I'll check back in with you in a couple days.

Quick tip: Even adding just your top 5 skills could make a big difference. It takes less than 2 minutes.

Is there anything else I can help you with?""",
            'buttons': ['Find jobs for me', 'Check my profile', 'I\'m all set']
        }
    },
    
    'add_skill': {
        'initial': {
            'message': """Hey {name}! 👋

I ran a quick analysis of your profile and found an opportunity to significantly boost your visibility.

**Current status:**
- Profile completeness: {profile_completeness}%
- Employer views this week: {emp_cv_views_last_week}

**The opportunity:**
Profiles above 85% complete get contacted **3x more often**. You're just a few skills away from hitting that threshold!

Our model predicts ({confidence}% confidence) that adding 5-7 key skills would increase your employer contact rate by **2.8x**.

Want me to show you which skills to add?""",
            'buttons': ['Yes, show me', 'Why does this matter?', 'Not interested']
        },
        'show_skills': {
            'message': """Perfect! Based on your work history in **{industry}**, here are 8 skills that match your background AND are trending in job postings right now:

**Top Skills for {industry}:**

Select your top 5-7 skills:""",
            'buttons': ['Python', 'SQL', 'Tableau', 'Machine Learning', 
                       'Data Visualization', 'Statistics', 'Excel', 'Communication']
        },
        'skills_added': {
            'message': """Excellent choices! ✅ Skills added to your profile.

**Your profile now:**
- Completeness: {profile_completeness}% → {new_completeness}% (+{improvement}%)
- Skills listed: {old_skills} → {new_skills} (+{skills_added})

**Impact prediction:**
Users who made similar updates saw:
- **2.8x increase** in employer contact flips
- **40% more** profile views within 7 days

I'll track your results and check back next week to see if you hit these benchmarks!

Anything else you need help with?""",
            'buttons': ['Find jobs for me', 'What else can I improve?', 'I\'m all set']
        },
        'why_matters': {
            'message': """Great question! Here's what the data shows:

📊 **Profiles 85%+ complete:**
• Get **3.2x more** employer views
• Receive **2.8x more** contact reveals
• Have **40% higher** application success rates

**Why?**
Employers use filters to search. Incomplete profiles often don't show up in results.

Think of it like a dating profile - the more someone knows about you (professionally!), the more likely they are to reach out.

Plus, adding skills takes less than 2 minutes and has the biggest impact on visibility.

Ready to fill in those gaps?""",
            'buttons': ['Yes, let\'s do it', 'I\'ll do it later']
        }
    },
    
    'apply_job': {
        'initial': {
            'message': """Hey {name}! 👋 I've got a time-sensitive opportunity for you.

**What I noticed:**
You've searched for {job_searches} jobs this week but haven't applied yet.

**The opportunity:**
I found 3 roles that match your profile (85%+ match). Here's why timing matters:

📊 **Applications in first 5 days:** 58% response rate  
📊 **Applications after day 7:** 12% response rate

Our model is {confidence}% confident that applying to 2-3 jobs this week would significantly increase your chances of getting contacted.

Want to see the top matches?""",
            'buttons': ['Yes, show me jobs', 'Why should I apply now?', 'Not interested']
        },
        'show_jobs': {
            'message': """Here are your top 3 matches based on your {industry} background:

**1. Senior Data Analyst at DataCo**
Match: 92% | Posted: 1 day ago | 🔥 Fresh  
Salary: $95K-115K | Remote  

**2. Data Scientist at TechCorp**
Match: 88% | Posted: 3 days ago  
Salary: $100K-130K | Hybrid - SF  

**3. Analytics Manager at FinanceHub**
Match: 85% | Posted: 2 days ago  
Salary: $110K-140K | Remote  

**Why these?**
They match your skills, are recently posted, and users with similar profiles got **58% response rates** when applying within 5 days.

Which one interests you most?""",
            'buttons': ['Tell me about #1', 'Tell me about #2', 'Tell me about #3', 'Not interested in any']
        },
        'job_details': {
            'message': """**Senior Data Analyst at DataCo**

**The Role:**
• Lead analytics for product launches
• Build predictive models
• Work with cross-functional teams

**Requirements:**
✅ Python - You have this  
✅ SQL - You have this  
✅ Tableau - You have this  
✅ 5+ years experience - You have {years} years  
⚠️ Hadoop - Nice to have (optional)

**Your Match: 92%**

**Company Info:**
• Series C startup, 200 employees
• Known for: Strong data culture, remote-friendly
• Glassdoor: 4.2/5

**Why apply NOW:**
• Posted yesterday (freshest applicants get seen first)
• You're missing only 1 optional skill
• 58% response rate for applications in first 5 days

Ready to apply?""",
            'buttons': ['Yes, apply now', 'I\'m not qualified enough', 'Maybe later']
        },
        'not_qualified': {
            'message': """I hear you - that's totally normal! But let's look at the facts:

**Skills Match: 92%**
You have 11 out of 12 requirements. Most candidates have fewer.

**Experience Match:**
They want 5+ years, you have 6. ✓

**The Gap:**
Hadoop is listed as "nice to have", not required. Only about 30% of hired candidates have every single preferred skill.

**Historical Data:**
Users with 85%+ match rates who applied within 3 days got contacted **58% of the time**. You're at 92%.

**What our model predicts:**
If you apply now: **13% probability** of employer contact reveal  
If you DON'T apply: **0% chance** 🤷‍♀️

The worst that happens is they don't respond. The best? You get an interview.

Want to go for it?""",
            'buttons': ['Okay, let\'s apply', 'Still not sure']
        },
        'application_submitted': {
            'message': """Submitted! ✅

**Application sent to DataCo**  
Role: Senior Data Analyst  
Time: Just now  

**What typically happens next:**
• Days 1-7: They review applications
• Days 7-14: First interviews scheduled
• Average response time: 6 days

**Your Success Probability:**
Based on the model and this role's match rate:
• 58% chance of getting viewed
• 13% chance of contact reveal

I'll track this for you and let you know if there's any activity!

**Keep Momentum Going:**
Want to apply to 1-2 more similar roles? Users who submit **3+ applications per week** have 40% higher overall success rates.""",
            'buttons': ['Yes, show me more', 'I\'ll wait to hear back', 'I\'m done for now']
        }
    }
}

# Skills database for different industries
INDUSTRY_SKILLS = {
    'Data Analytics': ['Python', 'SQL', 'Tableau', 'Machine Learning', 
                       'Data Visualization', 'Statistics', 'Excel', 'Communication'],
    'Software Engineering': ['JavaScript', 'Python', 'React', 'Node.js', 
                            'AWS', 'Docker', 'Git', 'Agile'],
    'Marketing': ['SEO', 'Google Analytics', 'Content Marketing', 'Social Media', 
                  'Email Marketing', 'Copywriting', 'A/B Testing', 'CRM']
}

# ============================================================================
# STREAMLIT APP
# ============================================================================

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_flow' not in st.session_state:
        st.session_state.conversation_flow = None
    if 'conversation_step' not in st.session_state:
        st.session_state.conversation_step = None
    if 'ml_prediction' not in st.session_state:
        st.session_state.ml_prediction = None
    if 'skills_selected' not in st.session_state:
        st.session_state.skills_selected = []

def format_message(template, user_profile, **kwargs):
    """Format message template with user data"""
    format_dict = {**user_profile, **kwargs}
    return template.format(**format_dict)

def add_message(role, content):
    """Add message to chat history"""
    st.session_state.messages.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now()
    })

def start_conversation(flow_type, user_profile, ml_prediction):
    """Start a new conversation flow"""
    st.session_state.conversation_flow = flow_type
    st.session_state.conversation_step = 'initial'
    st.session_state.ml_prediction = ml_prediction
    
    # Get initial message
    flow = CONVERSATION_FLOWS[flow_type]
    initial = flow['initial']
    
    confidence = int(ml_prediction['confidence'] * 100)
    message = format_message(
        initial['message'], 
        user_profile,
        confidence=confidence
    )
    
    add_message('assistant', message)

def handle_user_response(response):
    """Handle user button click"""
    # Add user's response to chat
    add_message('user', response)
    
    current_flow = st.session_state.conversation_flow
    current_step = st.session_state.conversation_step
    user_profile = st.session_state.user_profile
    
    flow = CONVERSATION_FLOWS[current_flow]
    
    # Determine next step based on response
    next_step = None
    
    if current_flow == 'refresh_cv':
        if response == 'Yes, refresh it':
            next_step = 'success'
        elif response == 'Why does this help?':
            next_step = 'why'
        elif response == 'Not right now' or response == 'Maybe later':
            next_step = 'later'
        elif response == 'Yes, remind me':
            next_step = 'remind_set'
        elif response == "Sure, let's add skills":
            # Switch to add_skill flow
            st.session_state.conversation_flow = 'add_skill'
            st.session_state.conversation_step = 'show_skills'
            next_step = 'show_skills'
            current_flow = 'add_skill'
            flow = CONVERSATION_FLOWS['add_skill']
    
    elif current_flow == 'add_skill':
        if response == 'Yes, show me':
            next_step = 'show_skills'
        elif response == 'Why does this matter?':
            next_step = 'why_matters'
        elif response in ['Yes, let\'s do it', 'I\'ll do it later']:
            next_step = 'show_skills' if response == 'Yes, let\'s do it' else 'initial'
        elif response in INDUSTRY_SKILLS.get(user_profile['industry'], []):
            # User is selecting skills
            if response not in st.session_state.skills_selected:
                st.session_state.skills_selected.append(response)
            return  # Don't send message yet, wait for more selections
    
    elif current_flow == 'apply_job':
        if response == 'Yes, show me jobs':
            next_step = 'show_jobs'
        elif response in ['Tell me about #1', 'Tell me about #2', 'Tell me about #3']:
            next_step = 'job_details'
        elif response == 'Yes, apply now' or response == 'Okay, let\'s apply':
            next_step = 'application_submitted'
        elif response == 'I\'m not qualified enough':
            next_step = 'not_qualified'
    
    # Send next message
    if next_step and next_step in flow:
        st.session_state.conversation_step = next_step
        step_data = flow[next_step]
        
        # Special handling for skills_added
        if next_step == 'skills_added':
            old_completeness = user_profile['profile_completeness']
            skills_added = len(st.session_state.skills_selected)
            new_completeness = min(100, old_completeness + (skills_added * 3))
            
            message = format_message(
                step_data['message'],
                user_profile,
                new_completeness=new_completeness,
                improvement=new_completeness - old_completeness,
                old_skills=user_profile['unique_skills_added'],
                new_skills=user_profile['unique_skills_added'] + skills_added,
                skills_added=skills_added
            )
        else:
            message = format_message(step_data['message'], user_profile, years=6)
        
        add_message('assistant', message)

def main():
    initialize_session_state()
    
    # Header
    st.title("🤝 Rafiq - Your AI Career Assistant")
    st.caption("Powered by behavioral intelligence to maximize your job search success")
    
    # Sidebar - User Selection & Stats
    with st.sidebar:
        st.header("Demo Controls")
        
        # User selection
        user_id = st.selectbox(
            "Select Demo User:",
            options=list(TEST_USERS.keys()),
            format_func=lambda x: TEST_USERS[x]['name']
        )
        
        if st.button("Load User Profile"):
            st.session_state.user_profile = TEST_USERS[user_id]
            st.session_state.messages = []
            st.session_state.conversation_flow = None
            st.success(f"Loaded profile for {TEST_USERS[user_id]['name']}")
        
        # Display user stats if loaded
        if st.session_state.user_profile:
            st.divider()
            st.subheader("User Profile")
            profile = st.session_state.user_profile
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Profile Complete", f"{profile['profile_completeness']}%")
                st.metric("CV Views", profile['emp_cv_views_last_week'])
            with col2:
                st.metric("Applications", profile['applications_count'])
                st.metric("Days Since Refresh", profile['days_since_last_refresh'])
            
            st.divider()
            
            # ML Model Prediction
            if st.button("Run ML Model Prediction"):
                prediction = mock_ml_prediction(profile)
                st.session_state.ml_prediction = prediction
                
                st.subheader("ML Model Output")
                st.write(f"**Top Recommendation:** `{prediction['nudge']}`")
                st.write(f"**Confidence:** {prediction['confidence']:.1%}")
                st.write(f"**Expected Outcome:** `{prediction['expected_outcomes']}`")
                
                st.write("**All Predictions:**")
                for nudge, prob in sorted(prediction['all_predictions'].items(), 
                                         key=lambda x: x[1], reverse=True):
                    st.progress(prob, text=f"{nudge}: {prob:.1%}")
            
            st.divider()
            
            # Start conversation buttons
            st.subheader("Start Conversation")
            if st.button("🔄 Refresh CV Nudge"):
                start_conversation('refresh_cv', profile, 
                                 mock_ml_prediction(profile))
                st.rerun()
            
            if st.button("⚡ Add Skills Nudge"):
                start_conversation('add_skill', profile, 
                                 mock_ml_prediction(profile))
                st.rerun()
            
            if st.button("📋 Apply to Jobs Nudge"):
                start_conversation('apply_job', profile, 
                                 mock_ml_prediction(profile))
                st.rerun()
            
            if st.button("🔄 Reset Conversation"):
                st.session_state.messages = []
                st.session_state.conversation_flow = None
                st.rerun()
    
    # Main chat area
    if not st.session_state.user_profile:
        st.info("👈 Select a demo user from the sidebar to get started!")
        
        # Show demo info
        st.subheader("About Rafiq")
        st.write("""
        Rafiq is a conversational AI career assistant that uses behavioral intelligence 
        to help job seekers maximize their success.
        
        **Key Features:**
        - 🤖 ML-driven nudge recommendations
        - 💬 Natural conversational interface
        - 📊 Data-backed insights and predictions
        - 🎯 Personalized action recommendations
        
        **How it works:**
        1. Analyzes user behavioral features (CV refreshes, applications, profile completeness)
        2. Predicts which action will maximize employer engagement
        3. Delivers personalized nudges at the right time
        4. Tracks outcomes to validate predictions
        """)
        
        st.subheader("Demo Users")
        for user_id, profile in TEST_USERS.items():
            with st.expander(f"{profile['name']} - {profile['industry']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Profile:** {profile['profile_completeness']}%")
                    st.write(f"**Views:** {profile['emp_cv_views_last_week']}")
                with col2:
                    st.write(f"**Applications:** {profile['applications_count']}")
                    st.write(f"**Searches:** {profile['job_searches']}")
                with col3:
                    st.write(f"**Days Since Refresh:** {profile['days_since_last_refresh']}")
                    st.write(f"**Skills:** {profile['unique_skills_added']}")
        
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    
    # Display buttons for current conversation step
    if st.session_state.conversation_flow and st.session_state.conversation_step:
        flow = CONVERSATION_FLOWS[st.session_state.conversation_flow]
        step = flow[st.session_state.conversation_step]
        
        if 'buttons' in step:
            st.divider()
            
            # Special handling for skill selection
            if st.session_state.conversation_step == 'show_skills':
                st.write("**Select 5-7 skills:**")
                
                # Show industry-specific skills
                industry = st.session_state.user_profile['industry']
                skills = INDUSTRY_SKILLS.get(industry, [])
                
                cols = st.columns(4)
                for i, skill in enumerate(skills):
                    with cols[i % 4]:
                        if st.button(
                            skill, 
                            key=f"skill_{skill}",
                            type="primary" if skill in st.session_state.skills_selected else "secondary"
                        ):
                            if skill in st.session_state.skills_selected:
                                st.session_state.skills_selected.remove(skill)
                            else:
                                st.session_state.skills_selected.append(skill)
                            st.rerun()
                
                st.write(f"Selected: {len(st.session_state.skills_selected)} skills")
                
                if len(st.session_state.skills_selected) >= 5:
                    if st.button("✅ Add These Skills", type="primary"):
                        st.session_state.conversation_step = 'skills_added'
                        
                        profile = st.session_state.user_profile
                        old_completeness = profile['profile_completeness']
                        skills_added = len(st.session_state.skills_selected)
                        new_completeness = min(100, old_completeness + (skills_added * 3))
                        
                        flow_data = CONVERSATION_FLOWS['add_skill']['skills_added']
                        message = format_message(
                            flow_data['message'],
                            profile,
                            new_completeness=new_completeness,
                            improvement=new_completeness - old_completeness,
                            old_skills=profile['unique_skills_added'],
                            new_skills=profile['unique_skills_added'] + skills_added,
                            skills_added=skills_added
                        )
                        add_message('assistant', message)
                        st.rerun()
            else:
                # Regular buttons
                cols = st.columns(len(step['buttons']))
                for i, button_text in enumerate(step['buttons']):
                    with cols[i]:
                        if st.button(button_text, key=f"btn_{i}"):
                            handle_user_response(button_text)
                            st.rerun()
    
    # Show welcome message if no conversation started
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(f"""
            👋 Hi {st.session_state.user_profile['name']}! I'm **Rafiq**, your AI career assistant.
            
            I analyze your job search activity to help you get more employer attention and land interviews faster.
            
            Click one of the buttons in the sidebar to see how I can help you today!
            """)

if __name__ == "__main__":
    main()