import os
import random
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ---------------- Gemini Setup ----------------
USE_GEMINI = False
model = None

try:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        USE_GEMINI = True
except:
    USE_GEMINI = False


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, idea: str = Form(...)):

    # Generate a unique page ID
    page_id = random.randint(1000, 9999)

    # Hero/banner section
    hero_html = f"""
    <section class="hero" style="text-align:center; padding:40px; background:#4CAF50; color:white; border-radius:12px;">
        <h1>Welcome to the {idea.title()} Website</h1>
        <p>Explore our featured items below</p>
        <button style="padding:12px 20px; font-size:16px; background:#fff; color:#4CAF50; border:none; border-radius:8px; cursor:pointer;">
            Get Started
        </button>
    </section>
    """

    # Generate dynamic cards with images
    num_cards = random.randint(3, 6)
    cards_html = ""
    for i in range(1, num_cards + 1):
        card_id = f"{page_id}-{i}"
        image_url = f"https://picsum.photos/220/150?random={random.randint(1,1000)}"
        cards_html += f"""
        <div class="card" id="{card_id}">
            <img src="{image_url}" alt="{idea.title()} Item {i}">
            <h3>{idea.title()} Item {i}</h3>
            <p>Short description of item {i}</p>
            <button onclick="alert('Item ID: {card_id}')">View</button>
        </div>
        """

    # Combine hero and cards
    content = hero_html + f"""
    <section class="cards" style="display:flex; flex-wrap:wrap; gap:20px; justify-content:center; margin-top:30px;">
        {cards_html}
    </section>
    """

    # Attempt AI generation with Gemini if enabled
    if USE_GEMINI:
        try:
            prompt = f"""
            Generate a complete, modern, responsive second page for a {idea} website.
            Include:
            - header with logo and nav
            - hero/banner section
            - {num_cards} cards with image, title, description, button
            - footer
            Output only the inner HTML (<section>), no <html>/<body> tags
            """
            response = model.generate_content(prompt)
            ai_content = response.text
            # Replace {{cards}} placeholder if exists
            if "{{cards}}" in ai_content:
                ai_content = ai_content.replace("{{cards}}", cards_html)
            # Use AI content if generated
            if ai_content.strip():
                content = ai_content
        except Exception as e:
            print("Gemini Error:", e)

    # Render the result page
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "content": content,
            "page_id": page_id
        }
    )