from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
import time
import os
from dotenv import load_dotenv
from supabase import create_client

from analyzer.clone_repo import clone_repository
from analyzer.repo_info import repository_information
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from analyzer.repository_overview import get_repository_overview
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from analyzer.health_score import (
    calculate_health_score,
    classify_health,
)

from utils.validators import validate_github_url

from ai.summary_generator import generate_ai_summary

# ML
from ml.scripts.github_api import get_github_data
from ml.health_predictor import predict_health_details


# Flask application

app = Flask(__name__)

app.secret_key = "developer_intelligence"
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# Most recently completed analysis
# Fine for the current single-user/local prototype.

LAST_CONTEXT = None


# Context helper

def get_context_or_redirect():
    """Return the most recently completed analysis context."""

    return LAST_CONTEXT


# ML feature vector

def build_ml_features(
    github_data,
    statistics,
    overview,
    readme,
    dependencies,
    complexity,
    languages,
    tech,
):
    """
    Build the exact feature dictionary expected by the trained
    classification model.
    """

    complexity_value = complexity.get(
        "complexity",
        None,
    )

    functions_value = complexity.get(
        "functions",
        None,
    )

    return {

        
        # Repository statistics
        

        "total_files": statistics.get(
            "total_files",
            0,
        ),

        "total_folders": statistics.get(
            "total_folders",
            0,
        ),

        "lines": statistics.get(
            "lines",
            0,
        ),

        
        # Language-specific counts
        

        "python": statistics.get(
            "python",
            0,
        ),

        "html": statistics.get(
            "html",
            0,
        ),

        "css": statistics.get(
            "css",
            0,
        ),

        "javascript": statistics.get(
            "javascript",
            0,
        ),

        "java": statistics.get(
            "java",
            0,
        ),

        "cpp": statistics.get(
            "cpp",
            0,
        ),

        
        # Dependencies
        

        "dependency_count": len(
            dependencies
        ),

        
        # README
        

        "readme_score": readme.get(
            "score",
            0,
        ),

        
        # Complexity
        

        "functions": functions_value,

        "complexity": complexity_value,

        
        # Counts
        

        "language_count": len(
            languages
        ),

        "tech_stack_count": len(
            tech
        ),

        
        # Repository hygiene
        

        "has_readme": overview.get(
            "README",
            False,
        ),

        "has_license": overview.get(
            "License",
            False,
        ),

        "has_gitignore": overview.get(
            ".gitignore",
            False,
        ),

        
        # GitHub metadata
        

        "language": github_data.get(
            "language",
            "",
        ),

        "size": github_data.get(
            "size",
            0,
        ),

        "created_days": github_data.get(
            "created_days",
            0,
        ),

        "updated_days": github_data.get(
            "updated_days",
            0,
        ),

        
        # Metric-support indicators
        

        "complexity_supported": (
            complexity_value is not None
            and complexity_value != "Not Supported"
            and complexity_value != "-"
        ),

        "functions_supported": (
            functions_value is not None
            and functions_value != "Not Supported"
            and functions_value != "-"
        ),
    }

#LANDING PAGE
@app.route("/")
def landing():
    return render_template("landing.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("user_id", "").strip().lower()
        password = request.form.get("password", "")

        print("Login attempt:", email)

        if not email or not password:
            return render_template(
                "login.html",
                error="Email and Password are required"
            )

        try:

            # --------------------------------
            # Login using Supabase Auth
            # --------------------------------

            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )

            user = response.user

            if user is None:
                return render_template(
                    "login.html",
                    error="Invalid Email or Password"
                )

            # --------------------------------
            # Check email verification
            # --------------------------------

            if not user.email_confirmed_at:

                return render_template(
                    "login.html",
                    error="Please verify your email before logging in."
                )

            # --------------------------------
            # Get profile information
            # --------------------------------

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, full_name, email
                FROM users
                WHERE auth_user_id = %s
                """,
                (user.id,)
            )

            profile = cursor.fetchone()

            cursor.close()
            conn.close()

            if profile is None:

                return render_template(
                    "login.html",
                    error="User profile not found."
                )

            # --------------------------------
            # Create Flask session
            # --------------------------------

            session["logged_in"] = True
            session["user_id"] = profile[0]
            session["user_name"] = profile[1]
            session["user_email"] = profile[2]
            session["login_method"] = "Email"

            print("Login successful:", profile[2])

            return redirect(url_for("home"))

        except Exception as e:

            print("Login error:", e)

            return render_template(
                "login.html",
                error="Invalid Email or Password"
            )

    return render_template("login.html")

# GOOGLE LOGIN
@app.route("/auth/google")
def google_login():

    response = supabase.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {
                "redirect_to": url_for(
                    "auth_callback",
                    _external=True
                 ),
                "query_params": {
                    "prompt": "select_account"
                }
            }
        }
    )

    return redirect(response.url)

# AUTH CALLBACK
@app.route("/auth/callback")
def auth_callback():

    # --------------------------------
    # GOOGLE OAUTH CALLBACK
    # --------------------------------

    code = request.args.get("code")

    if code:

        try:

            response = supabase.auth.exchange_code_for_session(
                {
                    "auth_code": code
                }
            )

            user = response.user

            session["logged_in"] = True
            session["user_id"] = user.id
            session["user_email"] = user.email

            session["user_name"] = (
                user.user_metadata.get("full_name")
                or user.user_metadata.get("name")
                or user.email
            )

            session["login_method"] = "Google"

            print("Google login successful:", user.email)

            return redirect(url_for("home"))

        except Exception as e:

            print("Google authentication error:", e)

            return redirect(url_for("login"))

    # --------------------------------
    # EMAIL VERIFICATION CALLBACK
    # --------------------------------

    return render_template("email_verified.html")

# REGISTER - UI ONLY FOR NOW
# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        print("REGISTER FORM SUBMITTED")

        # Get form data
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        print("Name:", full_name)
        print("Email:", email)

        # -----------------------------
        # Basic validation
        # -----------------------------

        if not full_name or not email or not password or not confirm_password:
            return render_template(
                "register.html",
                error="All fields are required"
            )

        # Check password match
        if password != confirm_password:
            print("Passwords do not match")

            return render_template(
                "register.html",
                error="Passwords do not match"
            )

        # -----------------------------
        # Check existing profile
        # -----------------------------

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                cursor.close()
                conn.close()

                return render_template(
                    "register.html",
                    error="Email already exists"
                )

            cursor.close()
            conn.close()

        except Exception as e:

            print("Database check error:", e)

            return render_template(
                "register.html",
                error="Registration failed. Please try again."
            )

        # -----------------------------
        # Create Supabase Auth user
        # -----------------------------

        try:

            print("Creating Supabase Auth user...")

            response = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": full_name
                        },
                        "email_redirect_to": url_for(
                            "auth_callback",
                            _external=True
                        )
                    }
                }
            )

            user = response.user

            if user is None:

                print("Supabase user creation failed")

                return render_template(
                    "register.html",
                    error="Unable to create account. Please try again."
                )

            print("Supabase Auth user created:", user.email)

            # -----------------------------
            # Save profile in users table
            # -----------------------------

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (full_name, email, auth_user_id)
                VALUES (%s, %s, %s)
                """,
                (
                    full_name,
                    email,
                    user.id
                )
            )

            conn.commit()

            cursor.close()
            conn.close()

            print("User profile saved successfully")

            # -----------------------------
            # Show verification message
            # -----------------------------

            return render_template(
                "login.html",
                message="Registration successful! Please check your email and verify your account before logging in."
            )

        except Exception as e:

            print("Registration error:", e)

            return render_template(
                "register.html",
                error="Registration failed. Please try again."
            )

    # GET request
    return render_template("register.html")


@app.route("/home")
def home():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    response = render_template("index.html")

    # Prevent browser from caching the authenticated dashboard
    response = app.make_response(response)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

@app.route("/profile")
def profile():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    name = session.get("user_name", "User")
    email = session.get("user_email", "")

    name_parts = name.split()

    if len(name_parts) >= 2:
        initials = name_parts[0][0] + name_parts[-1][0]
    else:
        initials = name[:2]

    response = app.make_response(
        render_template(
            "profile.html",
            name=name,
            email=email,
            initials=initials.upper(),
            login_method=session.get("login_method", "Email"),
            account_status="Active"
        )
    )

    # Prevent browser from caching authenticated profile
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response
# LOGOUT
@app.route("/logout")
def logout():

    try:
        # Sign out from Supabase Auth
        supabase.auth.sign_out()
    except Exception as e:
        print("Supabase logout error:", e)

    # Clear Flask session
    session.clear()

    print("User logged out")

    return redirect(url_for("login"))

@app.route("/profile/logout")
def profile_logout():

    session.clear()

    return redirect(url_for("landing"))

# ANALYZE REPOSITORY
@app.route(
    "/analyze",
    methods=["POST"],
)
def analyze():

    global LAST_CONTEXT

    start_time = time.time()

    repo_url = request.form.get(
        "repo_url",
        "",
    ).strip()

# Validate URL
    if not validate_github_url(
        repo_url
    ):

        return render_template(
            "index.html",
            error=(
                "Please enter a valid "
                "GitHub repository URL."
            ),
        )

# GitHub API
    github_data = get_github_data(
        repo_url
    )

    if github_data is None:

        return render_template(
            "index.html",
            error=(
                "Could not retrieve "
                "repository information "
                "from GitHub."
            ),
        )

    print(
        "✅ GitHub API Done"
    )

#Clone repository
    success, result = clone_repository(
        repo_url
    )

    if not success:

        return render_template(
            "index.html",
            error=result,
        )

    repo_path = result

    print(
        "✅ Clone Done"
    )

#Repository analyzers
    repo_info = repository_information(
        repo_path
    )

    overview = get_repository_overview(
        repo_path
    )

    languages = detect_languages(
        repo_path
    )

    tech = detect_tech_stack(
        repo_path
    )

    dependencies = analyze_dependencies(
        repo_path
    )

    statistics = repository_statistics(
        repo_path
    )

    complexity = analyze_complexity(
        repo_path
    )

    readme = analyze_readme(
        repo_path
    )

    print(
        "✅ Repository analysis complete"
    )

    # AI summary

    ai_summary = generate_ai_summary(
        overview,
        languages,
        tech,
        statistics,
        readme,
        complexity,
        dependencies,
    )

    # Build ML feature vector

    ml_features = build_ml_features(
        github_data=github_data,
        statistics=statistics,
        overview=overview,
        readme=readme,
        dependencies=dependencies,
        complexity=complexity,
        languages=languages,
        tech=tech,
    )

    print(
        "✅ ML feature vector created"
    )

    # ML classification

    try:

        health_prediction = (
            predict_health_details(
                ml_features
            )
        )

        print(
            "✅ ML Health Prediction:",
            health_prediction,
        )

    except Exception as exc:

        print(
            "❌ ML prediction failed:",
            exc,
        )

        return render_template(
            "index.html",
            error=(
                "Repository analysis completed, "
                "but ML health prediction failed."
            ),
        )

    # AUTHORITATIVE BASELINE HEALTH SCORE
    #
    # This is calculated from the CURRENT health_score.py implementation.
    # It is separate from the ML classification result.

    baseline_features = {

        "readme_score": readme.get(
            "score",
            0,
        ),

        "has_readme": overview.get(
            "README",
            False,
        ),

        "has_license": overview.get(
            "License",
            False,
        ),

        "has_gitignore": overview.get(
            ".gitignore",
            False,
        ),

        "complexity": complexity.get(
            "complexity",
            None,
        ),

        "dependency_count": len(
            dependencies
        ),

        "updated_days": github_data.get(
            "updated_days",
            0,
        ),

        "total_files": statistics.get(
            "total_files",
            0,
        ),

        "total_folders": statistics.get(
            "total_folders",
            0,
        ),

        "lines": statistics.get(
            "lines",
            0,
        ),

        "functions": complexity.get(
            "functions",
            None,
        ),
    }

    baseline_health_score = (
        calculate_health_score(
            baseline_features
        )
    )

    baseline_health_grade = (
        classify_health(
            baseline_health_score
        )
    )

    print(
        "✅ Baseline Health Score:",
        baseline_health_score,
    )

    print(
        "✅ Baseline Health Grade:",
        baseline_health_grade,
    )

    # Store the authoritative baseline score in the summary.
    #
    # This replaces the old simplified score generated by summary_generator.

    ai_summary["health_score"] = (
        baseline_health_score
    )

    ai_summary["baseline_health_grade"] = (
        baseline_health_grade
    )

    # Store ML grade separately.

    ai_summary["health_grade"] = (
        health_prediction["grade"]
    )

    # Save context

    end_time = time.time()

    print(
        f"Analysis completed in "
        f"{end_time - start_time:.2f} seconds"
    )

    LAST_CONTEXT = {

        "repo": repo_info,

        "github_data": github_data,

        "overview": overview,

        "languages": languages,

        "tech": tech,

        "readme": readme,

        "dependencies": dependencies,

        "statistics": statistics,

        "complexity": complexity,

        "ai_summary": ai_summary,

        "repo_path": repo_path,

        # ML data

        "ml_features": ml_features,

        "health_prediction": health_prediction,

        # Explicit baseline data

        "baseline_health_score": (
            baseline_health_score
        ),

        "baseline_health_grade": (
            baseline_health_grade
        ),
    }

    # Redirect to dashboard

    return redirect(
        url_for("dashboard")
    )


# DASHBOARD

@app.route(
    "/dashboard"
)
def dashboard():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "dashboard.html",
        **context,
    )


# SUMMARY

@app.route(
    "/summary"
)
def summary():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "summary.html",
        **context,
    )


# HEALTH

@app.route(
    "/health"
)
def health():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "health.html",
        **context,
    )


# ARCHITECTURE

@app.route(
    "/architecture"
)
def architecture():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "architecture.html",
        **context,
    )


# SECURITY

@app.route(
    "/security"
)
def security():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "security.html",
        **context,
    )


# TECH STACK

@app.route(
    "/tech"
)
def tech():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "tech.html",
        **context,
    )


# AI CHAT

@app.route(
    "/chat"
)
def chat():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "chat.html",
        **context,
    )


# RUN APPLICATION

if __name__ == "__main__":

    app.run(
        debug=True,use_reloader = False
    )