"""
AI service for Google Gemini integration
Handles AI-powered features like person blueprint and Q&A
Single Responsibility: AI operations
"""
from typing import Optional, Dict, List
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from models.person import Person
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class AIService:
    """
    AI service for Google Gemini integration
    Encapsulates all AI-related business logic
    """
    
    def __init__(self):
        """Initialize AI service with Gemini model"""
        self.enabled = Config.AI_ENABLED
        self.model = None
        
        if self.enabled:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            logger.info(f"AI service initialized with model: {Config.GEMINI_MODEL}")
        else:
            logger.warning("AI service disabled: GEMINI_API_KEY not configured")
    
    def is_enabled(self) -> bool:
        """Check if AI service is enabled"""
        return self.enabled and self.model is not None
    
    def generate_person_blueprint(self, person: Person) -> Dict[str, str]:
        """
        Generate comprehensive person blueprint
        
        Args:
            person: Person entity
            
        Returns:
            Dictionary with 'summary' and 'generated_at' keys
            
        Raises:
            ValueError: If AI is not enabled or person has no details
            Exception: If AI generation fails
        """
        if not self.is_enabled():
            raise ValueError("AI feature not configured. Please set GEMINI_API_KEY environment variable.")
        
        if not person.details:
            raise ValueError("No details available to summarize")
        
        # Create enhanced prompt for comprehensive person blueprint
        prompt = f"""You are an expert relationship manager and personal assistant. Analyze the following information about "{person.name}" and create a comprehensive "Person Blueprint".

Raw Details:
{person.details}

Create a detailed analysis with the following sections:

## 📋 KEY INFORMATION
Extract and list contact details, important dates, and basic facts.

## 👤 WHO THEY ARE
Describe their role, background, profession, interests, and key characteristics.

## 💡 PERSONALITY TRAITS
Analyze their personality based on interactions and notes. Include:
- Communication style
- Interests and passions
- Values and priorities
- Strengths and notable qualities

## 🤝 HOW TO APPROACH
Provide practical advice on:
- Best ways to communicate with them
- Topics they're interested in
- Things to remember when interacting
- Do's and don'ts

## 📅 RELATIONSHIP TIMELINE
Summarize key moments chronologically (when you met, important updates, last contact, etc.)

## 💭 QUICK INSIGHTS
3-5 bullet points of the most important things to remember about this person.

Format the response in clear sections with appropriate spacing. Be insightful, practical, and personable. Focus on actionable insights that help build better relationships."""
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            if not response.text:
                raise Exception("No summary generated. Please try again.")
            
            logger.info(f"Generated blueprint for person: {person.name} (ID: {person.id})")
            
            return {
                'summary': response.text.strip(),
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating blueprint: {e}")
            raise
    
    def answer_question(self, question: str, people: List[Person]) -> Dict[str, str]:
        """
        Answer question about people using AI
        
        Args:
            question: User's question
            people: List of Person entities for context
            
        Returns:
            Dictionary with 'question', 'answer', and 'generated_at' keys
            
        Raises:
            ValueError: If AI is not enabled, question is empty, or no people provided
            Exception: If AI generation fails
        """
        if not self.is_enabled():
            raise ValueError("AI feature not configured. Please set GEMINI_API_KEY environment variable.")
        
        if not question.strip():
            raise ValueError("Question is required")
        
        if not people:
            raise ValueError("No people in your contacts yet")
        
        # Build comprehensive context from all people
        context = "You have access to information about the following people:\n\n"
        
        for person in people:
            context += f"=== {person.name} ===\n"
            if person.details:
                context += f"{person.details}\n"
            else:
                context += "No details available.\n"
            context += "\n"
        
        # Create prompt for central Q&A
        prompt = f"""You are a personal assistant helping manage relationships and contacts. You have access to notes about multiple people.

{context}

User Question: {question}

Instructions:
1. Analyze the question and determine which person(s) it relates to
2. Provide a clear, helpful answer based on the available information
3. If the question is about a specific person, mention their name in your answer
4. If the question involves multiple people, list them clearly
5. If the information isn't available, say so honestly
6. Be conversational and helpful
7. Keep answers concise (2-4 sentences) unless more detail is needed

Answer the question now:"""
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            if not response.text:
                raise Exception("No answer generated. Please try again.")
            
            logger.info(f"Answered question for {len(people)} people")
            
            return {
                'question': question,
                'answer': response.text.strip(),
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

