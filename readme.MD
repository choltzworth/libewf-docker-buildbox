# Build libewf debian packages
This Docker image builds libewf debian packages with Python bindings (pyewf) and includes the LEF tool.

## Features
- Builds libewf debian packages
- Installs Python bindings (pyewf) for libewf
- Sets up PYTHONPATH for Python module access
- Includes the LEF tool at `/opt/lef`

## Building the Image
To build the libewf debian packages do the following:
```bash
docker build . --no-cache --tag build-box
```

To build the libewf debian packages with a custom version do the following:
```bash
docker build --build-arg LIBEWF_VERSION=your_custom_version . --no-cache --tag build-box
```

## Running the Container
Once built, you can run the docker image with the following:
```bash
docker run --rm --name libewf_build_box --volume $(pwd)/debs:/tmp/debs -it build-box
```

The `--rm` flag automatically removes the container when you exit.

The image includes:
- libewf libraries and tools
- pyewf Python bindings
- LEF tool at `/opt/lef`

## Using the LEF Tool (unlef)
The image includes `unlef`, a command-line tool for extracting LEF files (L01, Lx01 format).

### Usage Examples (inside the container)
Once inside the container, you can use the unlef tool directly:

List contents of a LEF archive in JSON format:
```bash
python3 /opt/lef/unlef --list --suppress-apple-double-files /tmp/original.l01
```

Extract LEF archive to a directory:
```bash
python3 /opt/lef/unlef -d /output --suppress-apple-double-files /tmp/original.l01
```

Extract with sequential numbering mode:
```bash
python3 /opt/lef/unlef -d /output --numbering --suppress-apple-double-files /tmp/original.l01
```

View help and all available options:
```bash
python3 /opt/lef/unlef --help
```