"""
Health Configuration Module
Contains user health parameters and configuration settings
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class HealthProfile:
    """Manages user health profile and parameters"""
    
    def __init__(self, config_file: str = "user_health_profile.json"):
        self.config_file = config_file
        self.profile = self.load_profile()
    
    def load_profile(self) -> Dict:
        """Load user health profile from file"""
        default_profile = {
            "personal_info": {
                "age": None,
                "gender": None,
                "height_cm": None,
                "weight_kg": None
            },
            "medical_history": {
                "allergies": [],
                "chronic_conditions": [],
                "medications": [],
                "dietary_restrictions": []
            },
            "health_goals": {
                "weight_goal": None,
                "activity_level": "moderate",
                "primary_goal": "maintain_health"
            },
            "diet_preferences": {
                "preferred_cuisines": [],
                "meal_frequency": 3,
                "water_intake_goal_liters": 2.5
            },
            "health_metrics": {
                "bmi": None,
                "last_updated": None
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    profile = json.load(f)
                # Merge with default profile to ensure all keys exist
                return self._merge_dicts(default_profile, profile)
            else:
                return default_profile
        except Exception as e:
            print(f"Error loading profile: {e}")
            return default_profile
    
    def save_profile(self):
        """Save user health profile to file"""
        try:
            self.profile["health_metrics"]["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w') as f:
                json.dump(self.profile, f, indent=2)
        except Exception as e:
            print(f"Error saving profile: {e}")
    
    def update_personal_info(self, age: int = None, gender: str = None, 
                           height_cm: float = None, weight_kg: float = None):
        """Update personal information"""
        if age is not None:
            self.profile["personal_info"]["age"] = age
        if gender is not None:
            self.profile["personal_info"]["gender"] = gender
        if height_cm is not None:
            self.profile["personal_info"]["height_cm"] = height_cm
        if weight_kg is not None:
            self.profile["personal_info"]["weight_kg"] = weight_kg
        
        # Calculate BMI if height and weight are available
        self._calculate_bmi()
        self.save_profile()
    
    def update_medical_history(self, allergies: List[str] = None, 
                             chronic_conditions: List[str] = None,
                             medications: List[str] = None,
                             dietary_restrictions: List[str] = None):
        """Update medical history"""
        if allergies is not None:
            self.profile["medical_history"]["allergies"] = allergies
        if chronic_conditions is not None:
            self.profile["medical_history"]["chronic_conditions"] = chronic_conditions
        if medications is not None:
            self.profile["medical_history"]["medications"] = medications
        if dietary_restrictions is not None:
            self.profile["medical_history"]["dietary_restrictions"] = dietary_restrictions
        
        self.save_profile()
    
    def update_health_goals(self, weight_goal: float = None, 
                          activity_level: str = None, 
                          primary_goal: str = None):
        """Update health goals"""
        if weight_goal is not None:
            self.profile["health_goals"]["weight_goal"] = weight_goal
        if activity_level is not None:
            self.profile["health_goals"]["activity_level"] = activity_level
        if primary_goal is not None:
            self.profile["health_goals"]["primary_goal"] = primary_goal
        
        self.save_profile()
    
    def _calculate_bmi(self):
        """Calculate BMI based on current height and weight"""
        height = self.profile["personal_info"]["height_cm"]
        weight = self.profile["personal_info"]["weight_kg"]
        
        if height and weight:
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            self.profile["health_metrics"]["bmi"] = round(bmi, 2)
    
    def _merge_dicts(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge dictionaries"""
        for key, value in user.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    default[key] = self._merge_dicts(default[key], value)
                else:
                    default[key] = value
        return default
    
    def get_profile_summary(self) -> str:
        """Get a formatted summary of the health profile"""
        info = self.profile["personal_info"]
        medical = self.profile["medical_history"]
        goals = self.profile["health_goals"]
        metrics = self.profile["health_metrics"]
        
        summary = []
        
        # Personal Info
        if info["age"]:
            summary.append(f"Age: {info['age']} years")
        if info["gender"]:
            summary.append(f"Gender: {info['gender']}")
        if info["height_cm"]:
            summary.append(f"Height: {info['height_cm']} cm")
        if info["weight_kg"]:
            summary.append(f"Weight: {info['weight_kg']} kg")
        if metrics["bmi"]:
            summary.append(f"BMI: {metrics['bmi']}")
        
        # Medical History
        if medical["allergies"]:
            summary.append(f"Allergies: {', '.join(medical['allergies'])}")
        if medical["chronic_conditions"]:
            summary.append(f"Chronic Conditions: {', '.join(medical['chronic_conditions'])}")
        if medical["medications"]:
            summary.append(f"Medications: {', '.join(medical['medications'])}")
        if medical["dietary_restrictions"]:
            summary.append(f"Dietary Restrictions: {', '.join(medical['dietary_restrictions'])}")
        
        # Goals
        if goals["weight_goal"]:
            summary.append(f"Weight Goal: {goals['weight_goal']} kg")
        summary.append(f"Activity Level: {goals['activity_level']}")
        summary.append(f"Primary Goal: {goals['primary_goal']}")
        
        return "\n".join(summary) if summary else "No health information available"

# Diet tracking and analysis functions
def analyze_diet_compatibility(food_items: List[str], health_profile: HealthProfile) -> Dict:
    """Analyze if food items are compatible with user's health profile"""
    restrictions = health_profile.profile["medical_history"]["dietary_restrictions"]
    allergies = health_profile.profile["medical_history"]["allergies"]
    
    analysis = {
        "compatible_foods": [],
        "restricted_foods": [],
        "allergen_warnings": [],
        "recommendations": []
    }
    
    for food in food_items:
        food_lower = food.lower()
        
        # Check for allergies
        allergen_found = False
        for allergen in allergies:
            if allergen.lower() in food_lower:
                analysis["allergen_warnings"].append(f"{food} - Contains {allergen}")
                allergen_found = True
                break
        
        # Check for dietary restrictions
        restriction_found = False
        for restriction in restrictions:
            if restriction.lower() in food_lower:
                analysis["restricted_foods"].append(f"{food} - Violates {restriction} restriction")
                restriction_found = True
                break
        
        # If no issues found, it's compatible
        if not allergen_found and not restriction_found:
            analysis["compatible_foods"].append(food)
    
    return analysis

def get_nutrition_prompt(health_profile: HealthProfile, user_query: str) -> str:
    """Generate a comprehensive nutrition prompt based on health profile"""
    profile_summary = health_profile.get_profile_summary()
    
    prompt = f"""
You are a certified nutritionist and health advisor. You have access to the following health profile:

{profile_summary}

Based on this health information, please provide personalized nutrition advice. Consider:

1. Current health metrics (BMI, age, weight, height)
2. Any medical conditions, allergies, or dietary restrictions
3. Health goals and activity level
4. Medication interactions with food (if applicable)

Guidelines for your response:
- Provide specific, actionable dietary recommendations
- Consider portion sizes appropriate for the person's metrics
- Suggest meal timing and frequency
- Include hydration recommendations
- Mention any foods to avoid based on medical history
- Provide future health predictions and preventive measures
- Include specific nutrients that might be beneficial
- Suggest monitoring parameters (weight, blood sugar, etc.)

User Query: {user_query}

Please provide a comprehensive, personalized response that addresses their specific needs and health profile.
"""
    
    return prompt

# Example usage and constants
ACTIVITY_LEVELS = ["sedentary", "light", "moderate", "active", "very_active"]
PRIMARY_GOALS = ["lose_weight", "gain_weight", "maintain_health", "build_muscle", "improve_energy"]
COMMON_ALLERGIES = ["nuts", "dairy", "gluten", "shellfish", "eggs", "soy", "fish"]
DIETARY_RESTRICTIONS = ["vegetarian", "vegan", "keto", "low_carb", "low_fat", "diabetic", "heart_healthy"]
