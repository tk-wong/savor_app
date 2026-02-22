import logging
import os

import flask
import  io
from image_generation_model import ImageGenerationModel
from dotenv import load_dotenv



def main(img_gen_model: ImageGenerationModel):
    app = flask.Flask(__name__)

    @app.route("/create_image", methods=["POST"])
    def hello():
        image_prompt = flask.request.json.get("prompt", "")
        if not image_prompt:
            return flask.jsonify({"error": "Prompt is required"}), 400
        image = img_gen_model.generate_image(image_prompt)
        byte_io = io.BytesIO()
        image.save(byte_io, format="PNG")
        byte_io.seek(0)
        return flask.send_file(byte_io, mimetype="image/png")

    app.run(host="0.0.0.0", port=5020)


if __name__ == "__main__":
    load_dotenv()
    image_generation_model = ImageGenerationModel(hf_token=os.getenv("HF_TOKEN"))
    main(image_generation_model)
    # logging.info("Shutting down server and unloading model...")
    # image_generation_model.unload_model()
