import subprocess

def main():

    # First, get the login password from AWS ECR
    get_login_command = ["aws", "ecr", "get-login-password", "--region", "eu-west-1"]
    result = subprocess.run(get_login_command, text=True, check=True, capture_output=True)

    # Check for any errors in the subprocess.run call
    if result.returncode != 0:
        print("Error:", result.stderr)
        exit(1)

    # Extract and strip the password from stdout
    password = result.stdout.strip()

    # Then, use the obtained password to log in to Docker
    docker_login_command = ["docker", "login", "--username", "AWS", "--password-stdin", "670349167663.dkr.ecr.eu-west-1.amazonaws.com"]
    subprocess.run(docker_login_command, input=password, text=True, check=True)


    subprocess.run(
        ["docker-compose", "build", "msc-app"],
        check=True,
    )
    subprocess.run(
        ["docker", "tag", "msc-web-app:latest", "670349167663.dkr.ecr.eu-west-1.amazonaws.com/msc-web-app:latest"],
        check=True,
    )
    subprocess.run(
        ["docker", "push", "670349167663.dkr.ecr.eu-west-1.amazonaws.com/msc-web-app:latest"],
        check=True,
    )


if __name__ == "__main__":
    main()
