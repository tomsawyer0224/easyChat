import click
import os
from utils import generate_Dockerfile, parse_config

@click.command()
def build():
    """
    build docker image
    """
    config = parse_config("./config.yaml")
    generate_Dockerfile(
        base_image = config["base_image"],
        models = config["models"]
    )
    cmd = f"docker build -t {config['image_name']} ."
    os.system(cmd)

    # script to run docker container
    os.makedirs("./scripts", exist_ok=True)
    with open("./scripts/start_chatbot.sh", "w") as rd_scr:
        rd_scr.write(
            f"docker run --name echat --rm -p 8080:8080 {config['image_name']}"
        )
    with open("./scripts/start_chatbot_background.sh", "w") as rdb_scr:
        rdb_scr.write(
            f"docker run --name echat --rm -d -p 8080:8080 {config['image_name']}"
        )
    # script to stop docker container
    with open("./scripts/stop_chatbot.sh", "w") as sdc_scr:
        sdc_scr.write("docker stop echat")

if __name__=="__main__":
    build()