import subprocess


def main():
    subprocess.run(
        ["docker-compose", "up", "--build", "-d"],
        check=True,
    )


if __name__ == "__main__":
    main()
