import subprocess

def main():
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.yml", "-f", "docker-compose.local.yml", "up", "--build", "-d"],
        check=True,
    )

if __name__ == "__main__":
    main()
