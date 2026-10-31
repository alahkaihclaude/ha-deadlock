import sys
sys.path.insert(0, "custom_components/deadlock")
from matches import new_matches, to_account_id, won

assert to_account_id("388674065") == 388674065
assert to_account_id("[U:1:388674065]") == 388674065
assert to_account_id("76561198348939793") == 388674065
assert to_account_id("gabe") is None

ms = [{"match_id": 3}, {"match_id": 1}, {"match_id": 2}]
assert [m["match_id"] for m in new_matches(ms, 1)] == [2, 3]
assert new_matches(ms, 3) == []

assert won({"match_result": 0, "player_team": 0})
assert not won({"match_result": 1, "player_team": 0})
print("ok")
