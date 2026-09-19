import os
from dotenv import load_dotenv
from groq import Groq
from google import genai
import traceback

from ai.repository_search import search_repository

load_dotenv()

# -----------------------------
# AI CLIENTS
# -----------------------------

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------
# REPOSITORY CONTEXT
# -----------------------------
def build_repository_context(question, analysis_data):

    question_lower = question.lower()

    def compact(value, max_chars):
        text = str(value)

        if len(text) > max_chars:
            return text[:max_chars] + "\n[truncated]"

        return text

    # --------------------------------
    # Repository information
    # --------------------------------

    repository_name = analysis_data.get(
        "repository_name",
        "Unknown"
    )

    repository_url = analysis_data.get(
        "repository_url",
        "Unknown"
    )

    languages = analysis_data.get("languages", {})
    tech = analysis_data.get("tech", {})
    dependencies = analysis_data.get("dependencies", {})
    overview = analysis_data.get("overview", {})
    statistics = analysis_data.get("statistics", {})
    complexity = analysis_data.get("complexity", {})
    health = analysis_data.get("health_prediction", {})

    # --------------------------------
    # Always keep basic identity
    # --------------------------------

    context = f"""
REPOSITORY:
{repository_name}

URL:
{repository_url}
"""

    # --------------------------------
    # Technology questions
    # --------------------------------

    technology_keywords = [
        "language",
        "languages",
        "technology",
        "technologies",
        "tech stack",
        "framework",
        "frameworks",
        "tools",
        "used in this project"
    ]

    if any(keyword in question_lower for keyword in technology_keywords):
        context += f"""

LANGUAGES:
{compact(languages, 1500)}

TECHNOLOGIES:
{compact(tech, 2000)}
"""

    # --------------------------------
    # Dependency questions
    # --------------------------------

    dependency_keywords = [
        "dependency",
        "dependencies",
        "package",
        "packages",
        "library",
        "libraries",
        "requirements"
    ]

    if any(keyword in question_lower for keyword in dependency_keywords):
        context += f"""

DEPENDENCIES:
{compact(dependencies, 2500)}
"""

    # --------------------------------
    # Project overview questions
    # --------------------------------

    overview_keywords = [
        "explain the project",
        "project overview",
        "purpose",
        "what does this project do",
        "what is this project",
        "about this project",
        "overview"
    ]

    if any(keyword in question_lower for keyword in overview_keywords):
        context += f"""

REPOSITORY OVERVIEW:
{compact(overview, 2500)}

LANGUAGES:
{compact(languages, 1000)}

TECHNOLOGIES:
{compact(tech, 1500)}
"""

    # --------------------------------
    # Health / quality questions
    # --------------------------------

    health_keywords = [
        "health",
        "health score",
        "health grade",
        "score",
        "grade",
        "code quality",
        "quality",
        "improve",
        "improvement",
        "weakness",
        "problem"
    ]

    if any(keyword in question_lower for keyword in health_keywords):
        context += f"""

HEALTH PREDICTION:
{compact(health, 1500)}

COMPLEXITY:
{compact(complexity, 1800)}

STATISTICS:
{compact(statistics, 1800)}
"""

    # --------------------------------
    # Architecture questions
    # --------------------------------

    architecture_keywords = [
        "architecture",
        "project flow",
        "application flow",
        "system flow",
        "how does the project work",
        "how does this project work",
        "how does the system work",
        "structure",
        "components"
    ]

    if any(keyword in question_lower for keyword in architecture_keywords):

        context += f"""

REPOSITORY OVERVIEW:
{compact(overview, 2000)}

LANGUAGES:
{compact(languages, 1000)}

TECHNOLOGIES:
{compact(tech, 1500)}
"""

    # --------------------------------
    # Source-code search
    # --------------------------------

    if needs_code_search(question):

        repo_path = analysis_data.get("repo_path")

        if repo_path:

            search_results = search_repository(
                repo_path,
                question,
                max_results=3
            )

            code_context = ""
            total_chars = 0

            for score, file_path, content in search_results:

                if total_chars >= 4500:
                    break

                relative_path = os.path.relpath(
                    file_path,
                    repo_path
                )

                snippet = content[:1500]

                code_context += f"""
FILE: {relative_path}

{snippet}

--------------------
"""

                total_chars += len(snippet)

            if code_context:
                context += f"""

RELEVANT SOURCE CODE:
{code_context}
"""

    # --------------------------------
    # Final safety limit
    # --------------------------------

    MAX_CONTEXT_CHARS = 8000

    if len(context) > MAX_CONTEXT_CHARS:
        context = (
            context[:MAX_CONTEXT_CHARS]
            + "\n[context truncated]"
        )

    print(
        "Final repository context characters:",
        len(context)
    )

    return context


# -----------------------------
# QUESTION ROUTING
# -----------------------------

def needs_code_search(question):

    question_lower = question.lower()

    code_keywords = [
        "which file",
        "what file",
        "where is",
        "where are",
        "function",
        "class",
        "method",
        "implemented",
        "implementation",
        "source code",
        "authentication",
        "login",
        "signup",
        "database",
        "route",
        "endpoint",
        "api",
        "bug",
        "error",
        "how does",
        "how do",
        "project flow",
        "architecture"
    ]

    return any(
        keyword in question_lower
        for keyword in code_keywords
    )


def should_use_gemini(question):
    question_lower = question.lower()

    gemini_keywords = [
        "complete architecture",
        "entire architecture",
        "overall architecture",
        "complete project flow",
        "entire project flow",
        "deep analysis",
        "deeply analyze",
        "generate documentation",
        "write documentation",
        "security analysis",
        "analyze the code",
        "analyze the project",
        "explain the entire project",
        "explain the complete project",
    ]

    return any(keyword in question_lower for keyword in gemini_keywords)

# -----------------------------
# GROQ
# -----------------------------
def ask_groq(question, repository_context):

    prompt = f"""
You are the AI assistant of a Developer Intelligence Platform.

Answer questions about the specific GitHub repository provided below.

===== REPOSITORY CONTEXT =====

{repository_context}

===== USER QUESTION =====

{question}

===== RULES =====

- Use only information from the repository context.
- Never invent files, functions, technologies, frameworks,
  databases, routes, APIs, or features.
- If information is unavailable, clearly say so.
- Mention actual files when available.
- Base recommendations on repository evidence.
- Keep the answer concise and useful.
- Use headings and bullet points when useful.
- Do not use HTML.

Answer the user's question directly.
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        reasoning_effort="low",
        include_reasoning=False,
        max_completion_tokens=1024,
        temperature=0.2
    )

    return response.choices[0].message.content or ""
# -----------------------------
# MAIN CHATBOT FUNCTION
# -----------------------------
def ask_gemini(question, repository_context):

    prompt = f"""
You are the deep-analysis AI assistant of a Developer Intelligence Platform.

You are analyzing ONE specific GitHub repository.

===== REPOSITORY CONTEXT =====

{repository_context}

===== USER QUESTION =====

{question}

===== STRICT RULES =====

- Answer only using the repository context.
- Never invent files, functions, technologies, frameworks,
  databases, routes, APIs, or features.
- If information is unavailable, clearly say so.
- For architecture questions, explain the actual components
  and their relationships.
- For project-flow questions, explain the flow step by step.
- Mention actual file names when available.
- Base recommendations on repository evidence.
- Do not assume technologies that are not shown.
- Do not use HTML.
- Use headings and bullet points when useful.
- Keep the answer clear and understandable.

The user wants a repository-specific answer, not generic
software-development advice.
"""

    interaction = gemini_client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text or ""

def get_chatbot_response(question, analysis_data):

    try:
        repository_context = build_repository_context(
            question,
            analysis_data
        )



        if should_use_gemini(question):
            print("Using Gemini...")
            answer = ask_gemini(
                question,
                repository_context
            )
        else:
            print("Using Groq...")
            answer = ask_groq(
                question,
                repository_context
            )

        if not answer:
            return "I couldn't generate an answer. Please try again."

        return answer
    except Exception as error:
        print(f"Chatbot error: {error}")  
        return (
            "I encountered an error while processing your question. "
            "Please check the server terminal for details."
        )