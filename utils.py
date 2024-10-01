import requests
import json
import time
import os
import datetime
import jwt
import boto3
from botocore.client import Config
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение значений из переменных окружения
FOLDER_ID = os.getenv('FOLDER_ID')
IAM_ENDPOINT = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
TTS_URL = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
STT_URL = 'https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize'
OPERATION_URL = 'https://operation.api.cloud.yandex.net/operations/'
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')

def get_iam_token_from_sa_key():
    try:
        with open('service_account_key.json') as infile:
            key_data = json.load(infile)
    except FileNotFoundError:
        print("    ⚠️  Файл service_account_key.json не найден.")
        return None
    except json.JSONDecodeError:
        print("    ⚠️  Ошибка при чтении service_account_key.json.")
        return None

    service_account_id = key_data['service_account_id']
    key_id = key_data['id']
    private_key = key_data['private_key']

    now = datetime.datetime.now(datetime.timezone.utc)

    payload = {
        'aud': IAM_ENDPOINT,
        'iss': service_account_id,
        'iat': int(now.timestamp()),
        'exp': int((now + datetime.timedelta(minutes=1)).timestamp()),
    }

    encoded_jwt = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id},
    )

    response = requests.post(IAM_ENDPOINT, json={'jwt': encoded_jwt})

    if response.status_code == 200:
        print("✅  Токен IAM успешно получен")
        return response.json()['iamToken']
    else:
        print(f"⚠️  Ошибка при получении IAM-токена: {response.text}")
        return None

def synthesize_text(iam_token, text, output_audio_file='output.ogg'):
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'marina',
        'emotion': 'friendly',
        'speed': '1.2',
        'folderId': FOLDER_ID,
    }

    response = requests.post(TTS_URL, headers=headers, data=data)

    if response.status_code == 200:
        with open(output_audio_file, 'wb') as f:
            f.write(response.content)
        print(f"✅  Аудио сохранено в {output_audio_file}")
        return output_audio_file
    else:
        print(f"⚠️  Ошибка при синтезе речи: {response.text}")
        return None

def upload_audio_to_object_storage(audio_file):
    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='ru-central1',
    )

    try:
        s3.upload_file(audio_file, BUCKET_NAME, audio_file)
        print("✅  Аудиофайл загружен в Object Storage.")
    except Exception as e:
        print(f"⚠️  Ошибка при загрузке аудиофайла: {e}")
        return None

    try:
        audio_uri = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': audio_file},
            ExpiresIn=3600,
        )
        print("✅  Получен URI аудиофайла.")
        return audio_uri
    except Exception as e:
        print(f"⚠️  Ошибка при генерации URI: {e}")
        return None

def recognize_speech_long_running(iam_token, audio_uri):
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json',
    }
    data = {
        "config": {
            "specification": {
                "languageCode": "ru-RU",
            }
        },
        "audio": {
            "uri": audio_uri
        }
    }

    response = requests.post(STT_URL, headers=headers, json=data)

    if response.status_code == 200:
        operation_id = response.json().get('id')
        print(f"📝 Операция запущена с ID: {operation_id}")
        return operation_id
    else:
        print(f"⚠️  Ошибка при распознавании речи: {response.text}")
        return None

def get_recognition_result(iam_token, operation_id):
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    while True:
        response = requests.get(f'{OPERATION_URL}{operation_id}', headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('done', False):
                if 'response' in result:
                    print("🎉 Распознавание успешно завершено.")
                    return result['response']['chunks']
                else:
                    print(f"⚠️ Распознавание завершилось с ошибкой: {result}")
                    return None
            else:
                print("⏳ Ожидание завершения операции...")
                time.sleep(5)
        else:
            print(f"⚠️  Ошибка при получении статуса операции: {response.text}")
            return None