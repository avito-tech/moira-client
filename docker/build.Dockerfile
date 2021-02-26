FROM python:3.7

WORKDIR /build
COPY . /build

ARG PYPI_LOGIN
ARG PYPI_PASSWORD

RUN pip3 install --upgrade pip
RUN pip install twine
RUN python setup.py sdist --dist-dir dist --verbose

# replace https://pypi.cc/pypi/ with your company's pypi url
RUN twine upload dist/* --repository-url https://pypi.cc/pypi/ --username $PYPI_LOGIN --password $PYPI_PASSWORD

ENTRYPOINT ["bash"]
