from uuid import UUID


def get_auth_header(user_id: UUID):
    return {"msc-user-id": str(user_id)}


def get_response_body(response):
    return response.json()
