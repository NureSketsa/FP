import google.generativeai as genai

genai.configure(api_key="AIzaSyDkfBkc7hJElusILz6moo5_GlclLtbPMjY")  # <- New key
model = genai.GenerativeModel("gemini-2.0-flash")
print(model.generate_content("Hello Gemini!").text)
