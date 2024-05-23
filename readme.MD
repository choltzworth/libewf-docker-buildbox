# Build libewf debian packages
To build the libewf debian packages do the following:
```bash
docker build . --no-cache --tag build-box
```

To build the libewf debian packages with a custom version do the following:
```bash
docker build --build-arg LIBEWF_VERSION=your_custom_value . --no-cache --tag build-box
```

Once built, you can run the docker image with the following;
```bash
docker run --name libewf_build_box --volume $(pwd)/debs:/tmp/debs -it build-box
```