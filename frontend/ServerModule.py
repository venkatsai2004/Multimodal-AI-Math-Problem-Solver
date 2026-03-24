import requests
import anvil.server

API_URL = "https://your-vercel-url.vercel.app"

@anvil.server.callable
def solve_text_api(problem):
    response = requests.post(
        f"{API_URL}/solve/text",
        json={"problem": problem}
    )
    return response.json()