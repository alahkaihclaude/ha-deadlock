"""Pure helpers, no Home Assistant imports, so they can be tested on their own."""

STEAM64_OFFSET = 76561197960265728


def to_account_id(text: str) -> int | None:
    """Accept a Steam32 ID, a SteamID64 or [U:1:123]; return the Steam32 ID."""
    digits = text.strip().removeprefix("[U:1:").removesuffix("]")
    if not digits.isdigit():
        return None
    n = int(digits)
    return n - STEAM64_OFFSET if n > STEAM64_OFFSET else n


def won(match: dict) -> bool:
    # shortcut: assumes match_result is the winning team's number; check one real response and fix here if wins/losses come out swapped
    return match["match_result"] == match["player_team"]


def new_matches(matches: list[dict], last_id: int) -> list[dict]:
    """Matches newer than last_id, oldest first, so events fire in play order."""
    return sorted((m for m in matches if m["match_id"] > last_id), key=lambda m: m["match_id"])
