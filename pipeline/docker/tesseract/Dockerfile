# Tesseract con il modello italiano, per il passo 3 della pipeline (OCR).
# Immagine locale: niente da installare sulla macchina oltre a Docker.
#
#   docker build -t elezio-tesseract pipeline/docker/tesseract
#   docker run --rm -v "<cartella>:/dati" elezio-tesseract /dati/p001.png stdout -l ita tsv
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-ita \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["tesseract"]
