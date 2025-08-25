"""
HealthAra - AI-Powered Health and Nutrition Assistant
Interactive Streamlit Application
"""

import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from health_config import HealthProfile, get_nutrition_prompt, analyze_diet_compatibility
from health_config import ACTIVITY_LEVELS, PRIMARY_GOALS, COMMON_ALLERGIES, DIETARY_RESTRICTIONS
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HealthAra - AI Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Azure OpenAI client
@st.cache_resource
def init_openai_client():
    endpoint = "https://ai-shshaik2664ai279782049336.cognitiveservices.azure.com/"
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = "2024-12-01-preview"
    
    if not subscription_key:
        st.error("AZURE_OPENAI_API_KEY not found in environment variables!")
        st.stop()
    
    return AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=subscription_key,
    )

# Initialize session state
def init_session_state():
    if 'health_profile' not in st.session_state:
        st.session_state.health_profile = HealthProfile()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_conversation' not in st.session_state:
        st.session_state.current_conversation = []

def main():
    init_session_state()
    client = init_openai_client()
    
    # Header
    st.title("🏥 HealthAra - AI Health & Nutrition Assistant")
    st.markdown("---")
    
    # Sidebar for health profile management
    with st.sidebar:
        st.header("👤 Health Profile")
        
        # Profile tabs
        profile_tab1, profile_tab2, profile_tab3 = st.tabs(["📊 Basic Info", "🩺 Medical", "🎯 Goals"])
        
        with profile_tab1:
            st.subheader("Personal Information")
            
            age = st.number_input("Age", min_value=1, max_value=120, 
                                value=st.session_state.health_profile.profile["personal_info"]["age"] or 30)
            
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                index=["Male", "Female", "Other"].index(
                                    st.session_state.health_profile.profile["personal_info"]["gender"] or "Male"))
            
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, step=0.1,
                                   value=st.session_state.health_profile.profile["personal_info"]["height_cm"] or 170.0)
            
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, step=0.1,
                                   value=st.session_state.health_profile.profile["personal_info"]["weight_kg"] or 70.0)
            
            if st.button("💾 Update Basic Info"):
                st.session_state.health_profile.update_personal_info(age, gender, height, weight)
                st.success("✅ Basic information updated!")
                st.rerun()
        
        with profile_tab2:
            st.subheader("Medical History")
            
            # Allergies
            allergies = st.multiselect("Allergies", COMMON_ALLERGIES,
                                     default=st.session_state.health_profile.profile["medical_history"]["allergies"])
            
            # Chronic conditions
            chronic_conditions = st.text_area("Chronic Conditions (one per line)",
                                            value="\n".join(st.session_state.health_profile.profile["medical_history"]["chronic_conditions"]))
            chronic_conditions_list = [c.strip() for c in chronic_conditions.split('\n') if c.strip()]
            
            # Medications
            medications = st.text_area("Current Medications (one per line)",
                                     value="\n".join(st.session_state.health_profile.profile["medical_history"]["medications"]))
            medications_list = [m.strip() for m in medications.split('\n') if m.strip()]
            
            # Dietary restrictions
            dietary_restrictions = st.multiselect("Dietary Restrictions", DIETARY_RESTRICTIONS,
                                                default=st.session_state.health_profile.profile["medical_history"]["dietary_restrictions"])
            
            if st.button("💾 Update Medical Info"):
                st.session_state.health_profile.update_medical_history(
                    allergies, chronic_conditions_list, medications_list, dietary_restrictions)
                st.success("✅ Medical information updated!")
                st.rerun()
        
        with profile_tab3:
            st.subheader("Health Goals")
            
            weight_goal = st.number_input("Weight Goal (kg)", min_value=30.0, max_value=300.0, step=0.1,
                                        value=st.session_state.health_profile.profile["health_goals"]["weight_goal"] or weight)
            
            activity_level = st.selectbox("Activity Level", ACTIVITY_LEVELS,
                                        index=ACTIVITY_LEVELS.index(st.session_state.health_profile.profile["health_goals"]["activity_level"]))
            
            primary_goal = st.selectbox("Primary Health Goal", PRIMARY_GOALS,
                                      index=PRIMARY_GOALS.index(st.session_state.health_profile.profile["health_goals"]["primary_goal"]))
            
            if st.button("💾 Update Goals"):
                st.session_state.health_profile.update_health_goals(weight_goal, activity_level, primary_goal)
                st.success("✅ Health goals updated!")
                st.rerun()
        
        # Display current profile summary
        st.markdown("---")
        st.subheader("📋 Profile Summary")
        with st.expander("View Current Profile", expanded=False):
            profile_summary = st.session_state.health_profile.get_profile_summary()
            st.text(profile_summary)
        
        # BMI display
        bmi = st.session_state.health_profile.profile["health_metrics"]["bmi"]
        if bmi:
            st.metric("BMI", f"{bmi}", help="Body Mass Index")
            if bmi < 18.5:
                st.info("Underweight")
            elif 18.5 <= bmi < 25:
                st.success("Normal weight")
            elif 25 <= bmi < 30:
                st.warning("Overweight")
            else:
                st.error("Obese")
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(" Chat with Your AI Ara")
        
        # Chat history display
        chat_container = st.container()
        with chat_container:
            if st.session_state.current_conversation:
                for message in st.session_state.current_conversation:
                    if message["role"] == "user":
                        with st.chat_message("user"):
                            st.write(message["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message["content"])
        
        # Chat input
        user_input = st.chat_input("Ask me anything about nutrition and health...")
        
        if user_input:
            # Add user message to conversation
            st.session_state.current_conversation.append({"role": "user", "content": user_input})
            
            # Generate response
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analyzing your health profile and generating response..."):
                    try:
                        # Generate personalized prompt
                        nutrition_prompt = get_nutrition_prompt(st.session_state.health_profile, user_input)
                        
                        # Call Azure OpenAI
                        response = client.chat.completions.create(
                            model="gpt-4.1",
                            messages=[
                                {"role": "system", "content": nutrition_prompt},
                                {"role": "user", "content": user_input}
                            ],
                            max_tokens=2000,
                            temperature=0.7,
                            stream=True
                        )
                        
                        # Stream response
                        response_container = st.empty()
                        full_response = ""
                        
                        for chunk in response:
                            if chunk.choices and chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                                response_container.markdown(full_response + "▌")
                        
                        response_container.markdown(full_response)
                        
                        # Add assistant response to conversation
                        st.session_state.current_conversation.append({"role": "assistant", "content": full_response})
                        
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
        
        # Control buttons
        col_clear, col_save, col_export = st.columns(3)
        
        with col_clear:
            if st.button("🗑️ Clear Conversation"):
                st.session_state.current_conversation = []
                st.rerun()
        
        with col_save:
            if st.button("💾 Save Conversation") and st.session_state.current_conversation:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append({
                    "timestamp": timestamp,
                    "conversation": st.session_state.current_conversation.copy()
                })
                st.success("Conversation saved!")
        
        with col_export:
            if st.button("📄 Export Profile & Chats"):
                export_data = {
                    "health_profile": st.session_state.health_profile.profile,
                    "chat_history": st.session_state.chat_history,
                    "export_timestamp": datetime.now().isoformat()
                }
                st.download_button(
                    label="⬇️ Download Data",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"healthara_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    with col2:
        st.header("🍎 Diet Analysis")
        
        # Quick diet check
        st.subheader("Quick Food Compatibility Check")
        food_items = st.text_area("Enter foods (one per line):", 
                                placeholder="apple\nchicken breast\nwhole wheat bread\nsalmon")
        
        if st.button("🔍 Analyze Foods") and food_items:
            foods_list = [f.strip() for f in food_items.split('\n') if f.strip()]
            analysis = analyze_diet_compatibility(foods_list, st.session_state.health_profile)
            
            if analysis["compatible_foods"]:
                st.success("✅ Compatible Foods:")
                for food in analysis["compatible_foods"]:
                    st.write(f"• {food}")
            
            if analysis["restricted_foods"]:
                st.warning("⚠️ Restricted Foods:")
                for food in analysis["restricted_foods"]:
                    st.write(f"• {food}")
            
            if analysis["allergen_warnings"]:
                st.error("🚨 Allergen Warnings:")
                for warning in analysis["allergen_warnings"]:
                    st.write(f"• {warning}")
        
        # Quick suggestions
        st.subheader("💡 Quick Health Tips")
        profile = st.session_state.health_profile.profile
        
        tips = []
        if profile["health_metrics"]["bmi"]:
            bmi = profile["health_metrics"]["bmi"]
            if bmi < 18.5:
                tips.append("💪 Consider increasing caloric intake with nutrient-dense foods")
            elif bmi > 25:
                tips.append("🏃‍♀️ Focus on portion control and regular exercise")
        
        if profile["health_goals"]["primary_goal"] == "lose_weight":
            tips.append("🥗 Prioritize vegetables and lean proteins")
        elif profile["health_goals"]["primary_goal"] == "build_muscle":
            tips.append("🥩 Ensure adequate protein intake (1.6-2.2g per kg body weight)")
        
        if profile["personal_info"]["age"] and profile["personal_info"]["age"] > 50:
            tips.append("🦴 Consider calcium and vitamin D supplementation")
        
        for tip in tips[:3]:  # Show max 3 tips
            st.info(tip)
        
        # Chat history
        st.subheader("📚 Conversation History")
        if st.session_state.chat_history:
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 conversations
                with st.expander(f"Chat {len(st.session_state.chat_history) - i} - {chat['timestamp']}"):
                    for msg in chat['conversation'][-4:]:  # Show last 4 messages
                        if msg["role"] == "user":
                            st.write(f"**You:** {msg['content'][:100]}...")
                        else:
                            st.write(f"**Assistant:** {msg['content'][:100]}...")
        else:
            st.info("No conversation history yet. Start chatting to see your history here!")

if __name__ == "__main__":
    main()
