from stack_oracle.compose import image_major, image_base_name


def test_image_major():
    assert image_major("mongo:7.0") == 7
    assert image_major("postgres:18-alpine") == 18
    assert image_major("mongo:7.0@sha256:abc") == 7


def test_image_base_name():
    assert image_base_name("docker.io/library/postgres:18") == "postgres"
