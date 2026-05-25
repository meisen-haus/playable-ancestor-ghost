-- Read mod settings from playerSection (player script only).
local storage = require('openmw.storage')
local config = require('scripts.ancestor_ghost.config')

local M = {}

local function snapImmunity(value)
  local v = tonumber(value) or 100
  if v <= 0 then return 0 end
  if v <= 50 then return 50 end
  return 100
end

function M.readFromStorage()
  local section = storage.playerSection(config.settingsGroupKey)
  return {
    wraith = section:get(config.settingWraithKey) == true,
    normalWeaponsImmunity = snapImmunity(section:get(config.settingNormalWeaponsKey)),
  }
end

return M
