FROM python:3.8-buster

RUN apt-get update
RUN apt-get install -y pandoc default-jre graphviz
RUN apt-get install -y texlive-latex-recommended \
                       texlive-latex-extra \
                       texlive-fonts-recommended \
                       latexmk

WORKDIR /app
ADD requirements.txt .

RUN pip install -r requirements.txt

CMD sphinx-autobuild --host 0.0.0.0 docs/source docs/build/html \
    --ignore /app/docs/source/apps/capability_table.md \
    --ignore /app/docs/source/apps/openAPI.json

# Build:
# docker build -f local_build.Dockerfile -t mp-docs .

# Run:
# docker run -it --rm -v $PWD:/app -p 8000:8000 mp-docs
