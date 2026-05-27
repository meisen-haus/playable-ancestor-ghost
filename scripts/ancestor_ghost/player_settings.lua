-- Read mod settings from playerSection (player script only).
local storage = require('openmw.storage')
local config = require('scripts.ancestor_ghost.config')

local M = {}

local function snapImmunity(value)
  local fallback = config.settingDefaults.normalWeaponsImmunity
  local v = tonumber(value) or fallback
  if v <= 0 then return 0 end
  if v <= 50 then return 50 end
  return 100
end

local function readLevitate(section)
  local v = section:get(config.settingLevitateKey)
  if v == nil then
    return config.settingDefaults.ghostlyLevitate
  end
  return v == true
end

function M.readFromStorage()
  local section = storage.playerSection(config.settingsGroupKey)
  return {
    wraith = section:get(config.settingWraithKey) == true,
    normalWeaponsImmunity = snapImmunity(section:get(config.settingNormalWeaponsKey)),
    levitate = readLevitate(section),
  }
end

return M
