-- Shared IDs (must match tools/build_esp.mjs).

return {
  RACE_ID = 'ancestor_ghost',

  settingsPageKey = 'AncestorGhost',
  settingsGroupKey = 'SettingsAncestorGhost',
  settingWraithKey = 'wraithOfSulSenipul',
  settingNormalWeaponsKey = 'normalWeaponsImmunity',
  settingUndeadFriendlyKey = 'undeadFriendly',
  settingDefaults = {
    wraithOfSulSenipul = false,
    normalWeaponsImmunity = 100,
    undeadFriendly = false,
  },

  -- One Ghostly Nature ability per immunity level (balance.lua swaps spells).
  GHOSTLY_NATURE_BY_IMMUNITY = {
    [100] = 'ag_ghostly_nature_100',
    [50] = 'ag_ghostly_nature_50',
    [0] = 'ag_ghostly_nature_0',
  },
  GHOSTLY_NATURE_VARIANTS = {
    'ag_ghostly_nature_100',
    'ag_ghostly_nature_50',
    'ag_ghostly_nature_0',
  },

  SPELL_WRAITH = 'ag_wraith_sul',
  LEGACY_WRAITH_ABILITIES = {
    'ag_wraith',
  },
  WRAITH_SPELLS = {
    'ag_wraith_grave_fatigue',
    'ag_wraith_grave_strength',
    'ag_wraith_bonebiter',
  },

  LEGACY_GHOSTLY_NATURE_SPELLS = {
    'ag_ghostly_nature',
    'ag_immunity_norm_100',
    'ag_immunity_norm_50',
  },
}
