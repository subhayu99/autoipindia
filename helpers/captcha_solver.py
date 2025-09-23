import os
import re
from pathlib import Path
from random import choices
from itertools import chain

from google import genai
from google.genai import types

from config import CAPTCHA_EXAMPLES


def read_image_bytes(file_path: str | Path):
    file_path = str(file_path)
    with open(file_path, "rb") as f:
        return f.read()

def generate_image_part(file_path: str | Path):
    file_path = str(file_path)
    
    # Can be image/jpeg or image/png
    mime_type = "image/png" if file_path.endswith(".png") else "image/jpeg"
    
    return types.Part.from_bytes(
        mime_type=mime_type,
        data=read_image_bytes(file_path),
    )

def generate_user_message(file_path: str | Path):
    return types.Content(
        role="user",
        parts=[
            generate_image_part(file_path),
            types.Part.from_text(text="""What is the code in the captcha-like image?"""),
        ],
    )

def get_examples(n: int = 3):
    selected = choices(CAPTCHA_EXAMPLES, k=n)
    message_pairs = [
        [
            generate_user_message(file_path),
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(
                        text=f"""The code in the captcha-like image appears to be **{code}**."""
                    ),
                ],
            ),
        ]
        for file_path, code in selected
    ]

    return list(chain(*message_pairs))

def parse_code(text: str) -> str | None:
    matches = re.findall(r'[A-Z0-9]{6}', text)
    if matches:
        return matches[-1]
    code = text.split("**")[1].strip()
    if code.isdigit():
        return code
    return None

def read_captcha(file_path: str | Path, examples: int = 3) -> str | None:
    file_path = str(file_path)
    
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        *get_examples(examples),
        generate_user_message(file_path),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
        temperature=0.2,
        response_mime_type="text/plain",
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print(response.text)
    return parse_code(response.text)

if __name__ == "__main__":
    print(read_captcha("captcha.png"))
