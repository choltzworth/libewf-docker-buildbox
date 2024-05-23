# Build libewf debian packages
To build the libewf debian packages do the following:
```
docker build . --no-cache --tag build-box
docker run --name libewf_build_box --volume $(pwd)/debs:/tmp/debs -it build-box
```

To build the libewf debian packages with a custom version do the following:
```
docker build --build-arg LIBEWF_VERSION=your_custom_value . --no-cache --tag build-box
```