import json
import os
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# 서비스 계정 키를 환경 변수에서 가져오기
service_account_info = json.loads(os.getenv('GDRIVE_SERVICE_ACCOUNT_KEY'))
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']
)

# Google Colab 노트북 실행 함수
def run_colab_notebook():
    colab_url = "https://colab.research.google.com/drive/1sn2oF99dbJvOFW3vFtVVXMGpiqsUSg9f"
    session = AuthorizedSession(credentials)
    response = session.post(
        "https://colab.research.google.com/notebook",
        json={"notebook": {"id": "1sn2oF99dbJvOFW3vFtVVXMGpiqsUSg9f"}}
    )
    if response.status_code == 200:
        print("Notebook executed successfully.")
    else:
        print(f"Failed to execute notebook. Status code: {response.status_code}")

if __name__ == "__main__":
    run_colab_notebook()
