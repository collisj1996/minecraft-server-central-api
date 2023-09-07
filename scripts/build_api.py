import subprocess


def main():
    subprocess.run(
        ["poetry", "export", "--output", "msc/requirements.txt", "--without-hashes"],
        check=True,
    )


if __name__ == "__main__":
    main()
