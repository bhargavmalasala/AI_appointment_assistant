
import requests
import getpass

API_KEY = getpass.getpass("Enter your ElevenLabs API key: ")

url = "https://api.elevenlabs.io/v1/voices"

headers = {
    "xi-api-key": API_KEY
}

response = requests.get(url, headers=headers)

print("\nStatus Code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("\nAPI key is working!")
    print("\nAvailable voices:")

    for voice in data.get("voices", []):
        print(f"Name: {voice['name']} | Voice ID: {voice['voice_id']}")

else:
    print("\nAPI request failed:")
    print(response.text)
