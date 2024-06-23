import docker
import docker.errors
import time
import os


def start_database_container():
    client = docker.from_env()

    container_name = "test-db"
    scripts_directory = os.path.abspath("./scripts")

    try:
        existing = client.containers.get(container_name)
        print("Test container exists")
        existing.stop()
        existing.remove()
        print("Test container stopped and removed")
    except docker.errors.NotFound:
        print("Test container does not exist")

    container_config = {
        "name": container_name,
        "image": "postgres:16.1-alpine3.19",
        "detach": True,
        "ports": {"5432": "5434"},
        "environment": {"POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": "postgres"},
        "volumes": [f"{scripts_directory}:/docker-entrypoint-initdb.d"],
        "network_mode": "fastpi_init_dev_network",
    }

    container = client.containers.run(**container_config)

    while not is_container_ready(container=container):
        time.sleep(2)

    if not wait_for_stable_status(container):
        raise RuntimeError("Container did not stabalize in the specified time")

    return container


def is_container_ready(container):
    container.reload()
    print(container.status)
    return container.status == "running"


def wait_for_stable_status(container, stable_duration=30, interval=1):
    start_time = time.time()
    stable_count = 0

    while time.time() - start_time < stable_duration:
        if is_container_ready(container=container):
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= stable_duration / interval:
            return True

        time.sleep(interval)

    return False
