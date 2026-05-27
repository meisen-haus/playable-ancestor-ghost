-- Shared IDs (must match tools/build_esp.mjs).

local M = {
  RACE_ID = 'ancestor_ghost',

  settingsPageKey = 'AncestorGhost',
  settingsGroupKey = 'SettingsAncestorGhost',
  settingWraithKey = 'wraithOfSulSenipul',
  settingNormalWeaponsKey = 'normalWeaponsImmunity',
  settingLevitateKey = 'ghostlyLevitate',
  settingDefaults = {
    wraithOfSulSenipul = false,
    normalWeaponsImmunity = 100,
    ghostlyLevitate = true,
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
    'ag_ghostly_nature_100',
    'ag_ghostly_nature_50',
    'ag_ghostly_nature_0',
  },
}

-- Six Ghostly Nature abilities: immunity (100/50/0) × levitate on/off.
M.GHOSTLY_NATURE_VARIANTS = {
  'ag_ghostly_nature_100_lev',
  'ag_ghostly_nature_100_ground',
  'ag_ghostly_nature_50_lev',
  'ag_ghostly_nature_50_ground',
  'ag_ghostly_nature_0_lev',
  'ag_ghostly_nature_0_ground',
}

function M.ghostlyNatureSpellId(immunityMag, levitate)
  local mag = immunityMag
  if mag ~= 0 and mag ~= 50 then
    mag = 100
  end
  local suffix = levitate and '_lev' or '_ground'
  return ('ag_ghostly_nature_%d%s'):format(mag, suffix)
end

return M
