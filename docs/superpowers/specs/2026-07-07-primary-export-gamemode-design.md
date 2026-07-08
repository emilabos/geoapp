# Primary Export Game Mode — Design Spec
**Date:** 2026-07-07

## Summary

Add a "Primary Export" game mode that follows the existing `religion` / `capitals` / `currency` / `languages` pattern exactly. The country is shown on a map with a flag overlay ("both" question style) and the player identifies the country's main export. All answer modes work (4 options, 2 options, type). Levels are locked to `.both` question style; practice mode lets the user pick.

---

## Data Layer

**New file: `ExportData.swift`**  
Mirrors `ReligionData.swift`. Contains a `let exportByCountryName: [String: String]` dictionary keyed by lowercased country name (e.g. `"canada": "Crude Petroleum"`). Values come from `country_main_exports.json` (152 entries, 69 unique export values), hand-transcribed as a Swift literal — no runtime JSON parsing.

**`Country` struct (in `CountriesGameViewModel.swift`)**  
Add `mainExport: String` field. In `Country._parse()`, look it up via `exportByCountryName[r.names.common.lowercased()] ?? ""`, the same way `primaryReligion` is looked up via `religionByAlpha2[iso2]`.

---

## Game Attribute

**`GameAttribute` enum (in `GameShared.swift`)**  
Add `.exports` case:
- `value(for:)` → `country.mainExport`
- `promptPrefix` → `"What is the main export of"`

Autocomplete deduplication by export value is already handled generically in `AttributeGameViewModel.typingAutocomplete` (deduplicates on attribute value).

---

## Game Mode

**`GameMode` enum (in `GameModeSheet.swift`)**  
Add `.exports = "Primary Export"`. `usesMap` falls through to `default: return true`.

**`HomeView.swift`**
- `homeDisplayName`: `"Primary Export"`
- `homeSubtitle`: `"Main economic export of each country"`
- `homeIcon`: `"shippingbox.fill"`
- `launchGameView`: `.exports` case → `AttributeGameView(attribute: .exports, answerMode: .fourOptions, questionStyle: .both, difficulty: .easy, config: cfg)`

**`GameModeSheet.swift`**
- `icon` switch: `"shippingbox.fill"`
- `ctaButton` switch: `.exports` → `activeAttributeGame = .exports`
- `questionStyleSection` conditional: add `.exports`

**`GameModeSettingsView.swift`**
- `supportsQuestionStyle` check: add `.exports`
- Default `selectedQuestionStyle` to `.both` when `mode == .exports` (via custom `init`)
- `startGame()`: `.exports` → `activeAttributeGame = .exports`
- In the `.fullScreenCover(item: $activeAttributeGame)` handler: when `config.isLevelsMode`, pass `questionStyle: .both` unconditionally for `.exports`; otherwise use `selectedQuestionStyle`

**`LevelDataService.swift`**  
`.exports` → `"exports"`

---

## Levels Data (`levels.json`)

Add key `"exports"` with 50 levels of 20 iso2 codes each. Level ordering matches the familiarity progression used by the `religion` mode: easy levels (1–15) use highly recognisable countries (G20 + major economies), medium levels (16–35) broaden to mid-tier countries, hard levels (36–50) include smaller/less-known nations.

---

## Consistency Checklist

| Concern | Handled by |
|---|---|
| Distinct options | `AttributeGameViewModel.buildOptions` deduplicates by attribute value |
| Autocomplete | `AttributeGameViewModel.typingAutocomplete` deduplicates by attribute value |
| Adaptive learning | `adaptiveModeId` = `"exports"` (from `attribute.rawValue`) |
| Levels progression | `LevelDataService` + `levels.json` `"exports"` key |
| Question style picker | Shown for `.exports` in both `GameModeSheet` and `GameModeSettingsView` |
| Levels locked to `.both` | `questionStyle: .both` hard-coded in levels branch of `startGame()` |
| Jump-back | `HomeView.launchGameView` `.exports` case with `.both` |
| Profile/XP | No change needed — `AttributeGameView` already records XP generically via `gameMode.levelsKey` |
