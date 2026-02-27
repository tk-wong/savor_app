docker build -t --no-cache image-gen-model .
docker run -it --rm -p 5020:5020 --gpus=all --runtime nvidia image-gen-model