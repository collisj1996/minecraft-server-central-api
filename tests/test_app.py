from fastapi.testclient import TestClient

# def test_auth(session, test_client: TestClient):
#     response = test_client.get(
#         "/servers",
#         headers={
#             "Authorization": "eyJraWQiOiJFT1ZGRHpGVStSM1ZKSXZtOGZ1RDhabUs1eGxpTzFWVnhTalB6dkVIcXMwPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJkMjQ1NDRlNC1iMGExLTcwMDctZjhjZi05ZWZiNGViMzVkOGEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtd2VzdC0xLmFtYXpvbmF3cy5jb21cL2V1LXdlc3QtMV80dFVwZlZZcUUiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiJpdDBlY3Ruc2Q0NGNyMXBocmlmaW8yaDVrIiwib3JpZ2luX2p0aSI6ImY2NjU2NzQxLWJjYTgtNGNkMi1hNDkwLTk1MmQ2ODQwYTY3MCIsImV2ZW50X2lkIjoiNTMxMGI0NDYtMDlhMS00MGE0LWI2OGYtNjNhZTdjNDUyMmI0IiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJwaG9uZSBvcGVuaWQgZW1haWwiLCJhdXRoX3RpbWUiOjE2OTUyMjM3NDEsImV4cCI6MTY5NTIyNzM0MSwiaWF0IjoxNjk1MjIzNzQxLCJqdGkiOiJiZmQxM2M1Ni0yZTllLTQ5NjItYjc4NC02NGNhMmRmODc2OTMiLCJ1c2VybmFtZSI6ImNvbGRvZyJ9.oFd4lRumh7WHDZn4LmEB0CpCXit0c8fMyqZGgN6G7mdgTSwAuTVso4mSf5soWV9UyHewjn7E8MLGrPhpC_b5G3xDYvcKT4_hpNAP7N0MOqZQjsL4y71jsFE_kPNeftAm6HuubYHT12d8gStrLdNGkZR0RFb14SHiIdYx8HSYVvPjx3vFRDXgXaFdZuETCDAQIPylXkmaIXnSnc9e35HrE5XDQCWxVSBPBlgqiW4fAT6EDaceoKC8puJEZmRcGAHubb0wSVVP7ASAATGm6_gWdJIUC20w1596z1SXxnU5VXj7m_G7XoU-rzmbiFZVkMzOGVOIovm9dw-W38RnaI8fsw",
#         },
#     )

#     assert response.status_code == 200

#     print(1)
