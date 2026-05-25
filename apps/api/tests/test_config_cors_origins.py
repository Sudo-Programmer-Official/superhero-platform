from app.config import Settings


def test_cors_origins_list_parses_csv() -> None:
    s = Settings(cors_origins="http://localhost:5173, https://app.example.com/")
    assert s.cors_origins_list == ["http://localhost:5173", "https://app.example.com"]


def test_cors_origins_list_parses_json_array() -> None:
    s = Settings(cors_origins='["https://superhero-platform-web.onrender.com/", "http://localhost:5173"]')
    assert s.cors_origins_list == ["https://superhero-platform-web.onrender.com", "http://localhost:5173"]


def test_cors_origins_list_parses_wrapped_values() -> None:
    s = Settings(cors_origins='"https://app.example.com"')
    assert s.cors_origins_list == ["https://app.example.com"]
