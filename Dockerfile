FROM jupyter/base-notebook:lab-3.0.11

LABEL maintainer="Fabian Brandt-Tumescheit <brandtfa@hu-berlin.de>"

# Install requirements
USER root
RUN mkdir /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y  --no-install-recommends cmake git build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# UID 1000 (jovyan) is the default user for jupyter-images. The default group for correct permission-level is GID 100 (users)
# Also see: https://jupyter.readthedocs.io/en/latest/community/content-community.html#what-is-a-jovyan
USER 1000
RUN pip install --upgrade pip 
RUN pip install setuptools cython powerlaw sklearn seaborn pandas tabulate matplotlib networkx ipycytoscape

# Configure Jupyter to enable ipycytoscape
RUN mkdir -p ${HOME}/.jupyter/lab
RUN mkdir -p ${HOME}/.jupyter/lab/user-settings
RUN mkdir -p ${HOME}/.jupyter/lab/user-settings/\@jupyterlab
RUN mkdir -p ${HOME}/.jupyter/lab/user-settings/@jupyterlab/docmanager-extension
COPY plugin.jupyterlab-settings ${HOME}/.jupyter/lab/user-settings/@jupyterlab/docmanager-extension
RUN conda install --verbose -c conda-forge --repodata-fn=repodata.json -y nodejs
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && jupyter labextension install jupyter-cytoscape
RUN jupyter lab build

# Create working environment
# This has to be done as root in order to avoid access denied errors.
USER root
RUN mkdir -p ${HOME}/.networkit
COPY . ${HOME}/.networkit/
RUN ln -s ${HOME}/.networkit/dataset ${HOME}/dataset && ln -s ${HOME}/.networkit/notebooks ${HOME}/notebooks && ln -s ${HOME}/.networkit/scripts ${HOME}/scripts
COPY Introduction.md ${HOME}
RUN rm -rf ${HOME}/work
RUN chown -R jovyan:users ${HOME}/*
RUN chown -R jovyan:users ${HOME}/.networkit
RUN chown -R jovyan:users ${HOME}/.networkit/*

# Build and install networkit from current branch
USER 1000
RUN cd ${HOME}/.networkit && python3 setup.py build_ext && pip install -e .