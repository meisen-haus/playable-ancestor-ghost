-- PLAYER script: settings UI, tutorial message, balance on load / option changes.

local ui = require('openmw.ui')
local storage = require('openmw.storage')
local async = require('openmw.async')
local self = require('openmw.self')
local config = require('scripts.ancestor_ghost.config')
local settings = require('scripts.ancestor_ghost.settings')
local balance = require('scripts.ancestor_ghost.balance')
local playerSettings = require('scripts.ancestor_ghost.player_settings')

pcall(settings.registerPage)
pcall(settings.registerGroup)

local playerStore = storage.playerSection('AncestorGhost')
local modSettings = storage.playerSection(config.settingsGroupKey)
local STORE_TUTORIAL = 'ag_tutorial_shown'
local tutorialShown = false
local settingsSubscribed = false
local balanceSynced = false

local function applyBalance(notify)
  if not balance.applyToPlayer(self) then return false end
  balanceSynced = true
  if notify then
    local s = playerSettings.readFromStorage()
    if s.wraith then
      ui.showMessage('Wraith kit enabled (Grave Curse, Bonebiter, Wraith ability).')
    else
      ui.showMessage('Ancestor Ghost options applied.')
    end
  end
  return true
end

local function ensureSettingsSubscription()
  if settingsSubscribed then return end
  settingsSubscribed = true
  modSettings:subscribe(async:callback(function(_section, _key)
    applyBalance(true)
  end))
end

return {
  engineHandlers = {
    onLoad = function()
      tutorialShown = playerStore:get(STORE_TUTORIAL) or false
      playerSettings.ensureDefaults()
      ensureSettingsSubscription()
      applyBalance(false)
    end,

    onFrame = function()
      if balanceSynced then return end
      ensureSettingsSubscription()
      applyBalance(false)
    end,
  },

  eventHandlers = {
    AG_EquipBlocked = function(_data)
      if tutorialShown then return end
      tutorialShown = true
      playerStore:set(STORE_TUTORIAL, true)
      ui.showMessage('Ancestor Ghosts cannot wear clothing, weapons, or armour.')
    end,
  },
}
