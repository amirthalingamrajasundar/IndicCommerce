from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="test",
)

response = client.text_to_speech.convert(
    text="Hello, how are you?",
    target_language_code="hi-IN",
)

print(response)
