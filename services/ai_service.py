"""
AI service for Google Gemini integration
Handles AI-powered features: blueprints, Q&A, auto-tagging
"""
from typing import Optional, Dict, List
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import markdown
import bleach

from models.person import Person
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4',
    'blockquote', 'code', 'pre', 'hr', 'a', 'span',
]
ALLOWED_HTML_ATTRS = {'a': ['href', 'title'], 'span': ['class']}

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}


def sanitize_ai_html(text: str) -> str:
    """Convert markdown to HTML and sanitize to prevent XSS"""
    html = markdown.markdown(text, extensions=['extra', 'nl2br'])
    return bleach.clean(html, tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRS)


class AIService:
    """AI service for Google Gemini integration"""

    def __init__(self):
        self.enabled = Config.AI_ENABLED
        self.model = None
        if self.enabled:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            logger.info(f"AI service initialized with model: {Config.GEMINI_MODEL}")
        else:
            logger.warning("AI service disabled: GEMINI_API_KEY not configured")

    def is_enabled(self) -> bool:
        return self.enabled and self.model is not None

    def generate_person_blueprint(self, person: Person, notes: List = None) -> Dict[str, str]:
        if not self.is_enabled():
            raise ValueError("AI feature not configured. Please set GEMINI_API_KEY environment variable.")
        if not person.details and not notes:
            raise ValueError("No details or notes available to analyze")

        notes_context = ""
        if notes:
            notes_context = "\n\nInteraction History:\n"
            for note in notes[:30]:
                notes_context += f"- [{note.note_type}] {note.created_at[:10]}: {note.content}\n"

        contact_context = f"Name: {person.name}\n"
        if person.company:
            contact_context += f"Company: {person.company}\n"
        if person.job_title:
            contact_context += f"Title: {person.job_title}\n"
        if person.email:
            contact_context += f"Email: {person.email}\n"
        if person.location:
            contact_context += f"Location: {person.location}\n"
        if person.how_we_met:
            contact_context += f"How we met: {person.how_we_met}\n"
        if person.tags:
            contact_context += f"Tags: {', '.join(person.tags)}\n"

        prompt = f"""You are an expert relationship manager. Analyze the following information about "{person.name}" and create a comprehensive "Person Blueprint".

{contact_context}

Raw Notes/Details:
{person.details}
{notes_context}

Create a detailed analysis with these sections (use markdown formatting):

## Key Information
Extract contact details, important dates, and basic facts.

## Who They Are
Describe their role, background, profession, interests, and key characteristics.

## Personality Traits
- Communication style
- Interests and passions
- Values and priorities
- Strengths and notable qualities

## How to Approach
- Best ways to communicate
- Topics they're interested in
- Things to remember when interacting
- Do's and don'ts

## Relationship Timeline
Summarize key moments chronologically.

## Quick Insights
3-5 bullet points of the most important things to remember.

Be insightful, practical, and personable. Focus on actionable relationship-building insights."""

        try:
            response = self.model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
            if not response.text:
                raise Exception("No summary generated. Please try again.")

            logger.info(f"Generated blueprint for person: {person.name} (ID: {person.id})")
            return {
                'summary': sanitize_ai_html(response.text.strip()),
                'summary_raw': response.text.strip(),
                'generated_at': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error generating blueprint: {e}")
            raise

    def answer_question(self, question: str, people: List[Person]) -> Dict[str, str]:
        if not self.is_enabled():
            raise ValueError("AI feature not configured. Please set GEMINI_API_KEY environment variable.")
        if not question.strip():
            raise ValueError("Question is required")
        if not people:
            raise ValueError("No people in your contacts yet")

        context = "You have access to information about the following people:\n\n"
        for person in people:
            context += f"=== {person.name} ===\n"
            if person.company:
                context += f"Company: {person.company}\n"
            if person.job_title:
                context += f"Title: {person.job_title}\n"
            if person.tags:
                context += f"Tags: {', '.join(person.tags)}\n"
            if person.details:
                context += f"Details: {person.details[:500]}\n"
            if person.relationship_status:
                context += f"Relationship status: {person.relationship_status}\n"
            if person.next_follow_up:
                context += f"Follow-up due: {person.next_follow_up}\n"
            context += "\n"

        prompt = f"""You are a personal assistant helping manage relationships and contacts.

{context}

User Question: {question}

Instructions:
1. Analyze the question and determine which person(s) it relates to
2. Provide a clear, helpful answer based on available information
3. If the question is about a specific person, mention their name
4. If the question involves multiple people, list them clearly
5. If the information isn't available, say so honestly
6. Be conversational and helpful
7. Use markdown for formatting when helpful
8. Keep answers concise (2-4 sentences) unless more detail is needed

Answer:"""

        try:
            response = self.model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
            if not response.text:
                raise Exception("No answer generated. Please try again.")

            logger.info(f"Answered question for {len(people)} people")
            return {
                'question': question,
                'answer': sanitize_ai_html(response.text.strip()),
                'answer_raw': response.text.strip(),
                'generated_at': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

    def suggest_tags(self, person: Person) -> List[str]:
        """AI-powered tag suggestions based on person details"""
        if not self.is_enabled() or not person.details:
            return []

        prompt = f"""Based on this person's information, suggest 3-5 short tags (single words or short phrases) for categorization.

Name: {person.name}
Company: {person.company}
Title: {person.job_title}
Details: {person.details[:1000]}

Return ONLY a comma-separated list of tags, nothing else. Example: investor, AI/ML, San Francisco, mentor"""

        try:
            response = self.model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
            if response.text:
                tags = [t.strip() for t in response.text.strip().split(',') if t.strip()]
                return tags[:5]
        except Exception as e:
            logger.error(f"Error suggesting tags: {e}")
        return []
