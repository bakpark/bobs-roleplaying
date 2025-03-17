from io import BytesIO

from gtts import gTTS
from util import logger


# TTS 변환 함수 (예시로 gTTS 사용 또는 외부 TTS API 호출 자리)
def synthesize_text_to_speech(text: str, lang: str = "en") -> bytes:
    """
    주어진 텍스트를 음성으로 변환하고, 음성 데이터를 bytes로 반환합니다.
    실제 TTS 엔진 또는 외부 API 호출로 대체할 수 있습니다.
    """
    if not text:
        return b""  # 빈 텍스트에 대해서는 빈 응답
    # 예시: gTTS를 사용하여 MP3 오디오 데이터 생성
    if gTTS:
        tts = gTTS(text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        audio_data = fp.getvalue()
        return audio_data
    else:
        logger.error(">gtts import error")
        # gTTS 사용 불가한 경우: 실제 TTS 엔진/API 호출로 대체
        return b""
