import chainlit as cl
from chainlit.input_widget import Select

def invoke(name: str):
    return name

@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            )
        ]
    ).send()
    value = settings["Model"]
    cl.user_session.set("model", value)

@cl.on_settings_update
async def on_su(settings):
    cl.user_session.set("model", settings["Model"])

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    model = cl.user_session.get("model")
    # Send a response back to the user
    await cl.Message(
        content=invoke(model),
    ).send()