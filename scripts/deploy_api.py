import subprocess


def main():
    # First, get the login password from AWS ECR
    get_login_command = ["aws", "ecr", "get-login-password", "--region", "eu-west-1"]
    result = subprocess.run(
        get_login_command, text=True, check=True, capture_output=True
    )

    # Check for any errors in the subprocess.run call
    if result.returncode != 0:
        print("Error:", result.stderr)
        exit(1)

    # Extract and strip the password from stdout
    password = result.stdout.strip()

    # Then, use the obtained password to log in to Docker
    docker_login_command = [
        "docker",
        "login",
        "--username",
        "AWS",
        "--password-stdin",
        "670349167663.dkr.ecr.eu-west-1.amazonaws.com",
    ]
    subprocess.run(docker_login_command, input=password, text=True, check=True)

    subprocess.run(
        ["docker-compose", "build", "msc-web-app"],
        check=True,
    )
    subprocess.run(
        [
            "docker",
            "tag",
            "msc-web-app:latest",
            "670349167663.dkr.ecr.eu-west-1.amazonaws.com/msc-web-app:latest",
        ],
        check=True,
    )
    subprocess.run(
        [
            "docker",
            "push",
            "670349167663.dkr.ecr.eu-west-1.amazonaws.com/msc-web-app:latest",
        ],
        check=True,
    )

    # SSH into the EC2 instance and perform commands
    ssh_command = [
        "ssh",
        "-i",
        "~/.ssh/msc-web-server.pem",
        "ec2-user@ec2-54-154-80-210.eu-west-1.compute.amazonaws.com",
    ]

    try:
        # Execute SSH commands using stdin, stdout, and stderr
        ssh_process = subprocess.Popen(
            ssh_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Run a series of commands within the SSH session
        commands_to_run = [
            "cd minecraft-server-central",
            "sudo aws ecr get-login-password --region eu-west-1 | sudo docker login --username AWS --password-stdin 670349167663.dkr.ecr.eu-west-1.amazonaws.com",
            "sudo docker-compose up --build --pull -d",
        ]

        for command in commands_to_run:
            ssh_process.stdin.write(command.encode() + b"\n")
            ssh_process.stdin.flush()

        # Close stdin and wait for the SSH session to finish
        ssh_process.stdin.close()
        ssh_process.wait()

        # Capture and print SSH session output
        ssh_stdout, ssh_stderr = ssh_process.communicate()
        print("SSH STDOUT:", ssh_stdout.decode())
        print("SSH STDERR:", ssh_stderr.decode())

    except Exception as e:
        print("Error:", str(e))
    finally:
        # Ensure proper cleanup
        if ssh_process:
            ssh_process.stdin.close()
            ssh_process.stdout.close()
            ssh_process.stderr.close()
            ssh_process.kill()


if __name__ == "__main__":
    main()

#     subprocess.run(
#         ["ssh", "-i", "'~/.ssh/msc-web-server.pem'", "ec2-user@ec2-54-154-80-210.eu-west-1.compute.amazonaws.com"],
#         check=True,
#     )
#     subprocess.run(
#         ["cd", "minecraft-server-central"],
#         check=True,
#     )
#     subprocess.run(
#         ["sudo", "docker-compose", "up", "--build", "--pull", "-d"],
#         check=True,
#     )

# if __name__ == "__main__":
#     main()
