# Deadlock Players

A Home Assistant integration that tracks Deadlock players. Each player you add becomes a device with a **Match result** event entity. It fires a `finished` event each time that player finishes a match, with the result (`win`/`loss`) and stats attached. It polls [deadlock-api.com](https://api.deadlock-api.com/docs) every 5 minutes.

## Install

### With HACS (recommended)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alahkaihclaude&repository=ha-deadlock&category=integration)

Click the button above, or do it by hand:

1. In Home Assistant, open **HACS**, then the ⋮ menu, then **Custom repositories**.
2. Add `https://github.com/alahkaihclaude/ha-deadlock` with type **Integration**.
3. Search HACS for **Deadlock Players**, download it, and restart Home Assistant.

### Manually

1. Copy `custom_components/deadlock` into your Home Assistant `config/custom_components/` folder. You should end up with `config/custom_components/deadlock/manifest.json`.
2. Restart Home Assistant.

## Add a player

1. Go to **Settings → Devices & services → Add integration** and pick **Deadlock Players**.
2. Enter a name, such as `Alice`, and the player's Steam ID. Any of these formats works:
   - a Steam32 ID: `388674065`
   - a SteamID64: `76561198348939793`
   - the `[U:1:388674065]` form

   You can find a Steam ID on sites like steamid.io, or in the player's profile URL.
3. Repeat for each player you want to track.

This creates the entity `event.alice_match_result`. It also creates sensors that show the most recent match on the device page and on dashboards: when it finished (shown as "x minutes ago"), result, kills, deaths, assists, net worth and duration in minutes (for example `sensor.alice_last_match_kills`). For automations, use the event entity below instead: a sensor doesn't change when two matches in a row have the same value.

## Use it in an automation

The entity always shows the most recent match's stats as attributes, even before its first event, so the automation editor can list them. Every new match fires the event and updates them: `event_type` (always `finished`), `result` (`win`/`loss`), `match_id`, `hero_id`, `player_kills`, `player_deaths`, `player_assists`, `net_worth` and `match_duration_min`.

```yaml
automation:
  - alias: "Alice won a Deadlock match"
    triggers:
      - trigger: state
        entity_id: event.alice_match_result
        not_from: [unavailable, unknown]  # skip the restore after a restart
    conditions:
      - condition: template
        value_template: "{{ trigger.to_state.attributes.result == 'win' }}"
    actions:
      - action: notify.notify
        data:
          message: >
            Alice won! {{ trigger.to_state.attributes.player_kills }}/{{
            trigger.to_state.attributes.player_deaths }}/{{
            trigger.to_state.attributes.player_assists }}
```

### Trigger on kills, deaths, assists and other stats

Use the same trigger and add a **Numeric state** condition on one of the attributes. In the automation editor, choose **Add condition → Entity → Numeric state**, pick the match result entity, and set **Attribute** to, for example, `player_deaths`. Each condition is checked once per match.

```yaml
automation:
  - alias: "Alice had a rough game"
    triggers:
      - trigger: state
        entity_id: event.alice_match_result
        not_from: [unavailable, unknown]
    conditions:
      - condition: numeric_state
        entity_id: event.alice_match_result
        attribute: player_deaths
        above: 9  # 10 or more deaths
    actions:
      - action: notify.notify
        data:
          message: "Alice died {{ trigger.to_state.attributes.player_deaths }} times 💀"
```

Available attributes: `result` (`win`/`loss`), `player_kills`, `player_deaths`, `player_assists`, `net_worth`, `match_duration_min` (minutes) and `hero_id` (a number, not the hero's name). Add several conditions to combine them, for example 10+ kills **and** a win.

## Releasing an update

Bump `"version"` in `custom_components/deadlock/manifest.json` and push to `main`. The Release workflow runs the tests and publishes a `v<version>` release. HACS then offers the update under **Settings → Updates**. Restart Home Assistant after updating.

## Known limits

- Matches that finish while Home Assistant is off never fire an event. After a restart, tracking starts from the newest match.
- New matches show up within about 5 minutes, plus however long the API takes to list them.
