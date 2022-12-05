FROM jupyter/base-notebook:lab-3.5.0

LABEL maintainer="Fabian Brandt-Tumescheit <brandtfa@hu-berlin.de>"

COPY data/nd2022-beginner.ipynb ${HOME}
COPY data/nd2022-advanced.ipynb ${HOME}
COPY data/karate ${HOME}/input
COPY data/les_mis ${HOME}/input
COPY data/jazz ${HOME}/input
COPY notebooks ${HOME}
RUN mv ${HOME}/notebooks ${HOME}/playground 

USER 1000
RUN pip install --upgrade pip
RUN pip install setuptools cython powerlaw scikit-learn seaborn pandas tabulate matplotlib networkx ipycytoscape
RUN pip install networkit==9.1.1
