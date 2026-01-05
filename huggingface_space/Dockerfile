FROM python:3.10-slim

WORKDIR /app

# Install only what we need with EXACT versions
RUN pip install --no-cache-dir \
    gradio==4.19.2 \
    huggingface_hub==0.20.3 \
    requests>=2.28.0

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
