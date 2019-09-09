from framework.session import *

session = Session()
session.verify = False
staging_auth_url = "https://api.testing.aws.rewardgateway.net/auth/access_token"


target = session.target(staging_auth_url)


def test_access_token():
    payload = "----------------------------578395087689527433693242\r\nContent-Disposition: form-data; name=\"client_id" \
              "\"\r\n\r\nrarebreed\r\n----------------------------578395087689527433693242\r\nContent-Disposition: form-data;" \
              " name=\"grant_type\"\r\n\r\npassword\r\n----------------------------578395087689527433693242\r\nContent-Disposition:" \
              " form-data; name=\"username\"\r\n\r\n1\r\n----------------------------578395087689527433693242\r\nContent-Disposition:" \
              " form-data; name=\"password\"\r\n\r\n!1Password1!\r\n----------------------------578395087689527433693242\r\nContent-Disposition:" \
              " form-data; name=\"scope\"\r\n\r\nuser.read user.write programme.create programme.read programme.write member retailers.read" \
              "\r\n----------------------------578395087689527433693242--"
    headers = {
        'Accept': "application/vnd.rewardgateway+json;version=2.0",
        'Content-Type': "multipart/form-data; boundary=--------------------------578395087689527433693242",
    }

    response = target.post('/', headers=headers, data=payload)

    response.assert_ok()
    response.assert_jsonpath('$.expires_in', 3600)
    assert len(response.extract_jsonpath('$.access_token')) > 100
