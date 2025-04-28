from pathlib import Path

def test_eleven_tool():
    from media_crew.tools.eleven_tts import ElevenTTSTool
    mp3 = ElevenTTSTool()._run("Teste rápido!", voice_id="EXAVITQu4vr4xnSDxMaL")
    assert mp3.endswith(".mp3") and Path(mp3).exists()