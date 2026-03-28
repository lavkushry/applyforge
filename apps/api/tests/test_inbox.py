from app.services.inbox import extract_otp, mask_token


def test_extract_otp_prefers_matching_sender_hint() -> None:
    result = extract_otp(
        [
            {"sender": "noreply@example.com", "subject": "Old code", "body": "Your code is 111111"},
            {"sender": "jobs@greenhouse.io", "subject": "Verification code", "body": "Use 482913 to continue"},
        ],
        sender_hint="greenhouse",
        subject_hint="verification",
    )

    assert result["status"] == "resolved"
    assert result["code"] == "482913"
    assert result["code_last4"] == "2913"
    assert result["confidence"] == "high"


def test_mask_token_obscures_middle_characters() -> None:
    assert mask_token("abcdefgh12345678").startswith("abcd")
    assert mask_token("abcdefgh12345678").endswith("5678")
