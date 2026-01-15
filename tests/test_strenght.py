from index import PasswordStrengthAnalyzer

def test_calculate_password_strength_empty():
    psa = PasswordStrengthAnalyzer.__new__(PasswordStrengthAnalyzer)
    psa.common_passwords = set()

    score, strength = psa.calculate_password_strength("")
    assert score == 0