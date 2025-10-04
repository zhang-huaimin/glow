# example:
#    docker build -f testing/Dockerfile -t glow-test:latest .
#    docker run --rm glow-test:latest
FROM glow:latest

LABEL org.opencontainers.image.description="Glow Test Image - for dev & CI testing"

WORKDIR /app/testing

CMD ["glow", "--conf", "glow", "testcases/dev/test_load_dev.py"]