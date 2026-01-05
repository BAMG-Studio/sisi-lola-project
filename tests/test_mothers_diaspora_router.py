from modal_deployments.mothers_diaspora_router import route_incoming_message


def test_route_text_general():
    decision = route_incoming_message(
        from_number="whatsapp:+10000000000",
        to_number="whatsapp:+14155238886",
        body="Hello Sisi Lola",
        num_media=0,
        media_url_0=None,
        media_content_type_0=None,
    )
    assert decision.kind == "text"
    assert decision.intent == "general"
    assert decision.language in {"en", "unknown"}


def test_route_text_pidgin_language_guess():
    decision = route_incoming_message(
        from_number="whatsapp:+10000000000",
        to_number="whatsapp:+14155238886",
        body="Wetin dey happen?",
        num_media=0,
        media_url_0=None,
        media_content_type_0=None,
    )
    assert decision.kind == "text"
    assert decision.language == "pcm"


def test_route_text_pidgin_language_guess_misspelling():
    decision = route_incoming_message(
        from_number="whatsapp:+10000000000",
        to_number="whatsapp:+14155238886",
        body="weting dey happen for naija?",
        num_media=0,
        media_url_0=None,
        media_content_type_0=None,
    )
    assert decision.kind == "text"
    assert decision.language == "pcm"


def test_route_text_legal_intent():
    decision = route_incoming_message(
        from_number="whatsapp:+10000000000",
        to_number="whatsapp:+14155238886",
        body="How do I renew my work permit (EAD) with USCIS?",
        num_media=0,
        media_url_0=None,
        media_content_type_0=None,
    )
    assert decision.kind == "text"
    assert decision.intent == "legal_query"


def test_route_voice_media():
    decision = route_incoming_message(
        from_number="whatsapp:+10000000000",
        to_number="whatsapp:+14155238886",
        body="",
        num_media=1,
        media_url_0="https://example.com/audio.ogg",
        media_content_type_0="audio/ogg",
    )
    assert decision.kind == "voice"


def test_route_text_voice_reply_request_intent():
    decision = route_incoming_message(
        from_number="whatsapp:+10000000000",
        to_number="whatsapp:+14155238886",
        body="you fit talk?",
        num_media=0,
        media_url_0=None,
        media_content_type_0=None,
    )
    assert decision.kind == "text"
    assert decision.intent == "voice_reply_request"
