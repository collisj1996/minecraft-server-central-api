from msc.services.email_service import _build_email_template


def test_build_template():
    with open(
        f"msc/templates/awaitingconfirmation.html", "r", encoding="utf-8"
    ) as file:
        html_content = file.read()

    params = {
        "recipient_name": "TEST NAME",
        "server_name": "Test Server Name",
        "sponsor_slot": 8,
        "bid_amount": 5000,
    }

    html_content = _build_email_template(
        params=params,
        html=html_content,
    )

    assert (
        html_content
        == """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>MCSC - Auction Winner</title>
</head>
<body>
  <p>Hi TEST NAME,</p>
  <p>Congratulations on securing the number 8 sponsor slot for the server Test Server Name.</p>
  <p>Your winning bid amount was £5000</p>
  <p>If you are happy to continue, please respond to this email with "YES" within 12 hours.</p>
  <p>Once we have your confirmation please pay by the payment end time to secure your sponsored slot for the next month.</p>
  <p>If you would like to forfeit your slot to another server, please respond "NO" or "Forfeit", there is no penalty for this as long as you let us know!</p>
  <p>Thank you,</p>
  <p>Minecraft Server Central<p>
</body>
</html>
"""
    )
