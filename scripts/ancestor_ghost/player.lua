-- PLAYER script: settings UI, tutorial message, balance on load / option changes.

local ui = require('openmw.ui')
local storage = require('openmw.storage')
local async = require('openmw.async')
local self = require('openmw.self')
local config = require('scripts.ancestor_ghost.config')
local settings = require('scripts.ancestor_ghost.settings')
local balance = require('scripts.ancestor_ghost.balance')
local playerSettings = require('scripts.ancestor_ghost.player_settings')
local undeadFriendly = require('scripts.ancestor_ghost.undead_friendly')

pcall(settings.registerPage)
pcall(settings.registerGroup)

local playerStore = storage.playerSection('AncestorGhost')
local STORE_TUTORIAL = 'ag_tutorial_shown'
local tutorialShown = false
local settingsSubscribed = false
local balanceSynced = false
local undeadCheckTimer = 0
local UNDEAD_CHECK_INTERVAL = 0.25

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
  local modSettings = storage.playerSection(config.settingsGroupKey)
  modSettings:subscribe(async:callback(function(_section, _key)
    applyBalance(true)
    undeadFriendly.update()
  end))
end

local function trySyncBalance(notify)
  ensureSettingsSubscription()
  applyBalance(notify)
end

return {
  engineHandlers = {
    -- New saves call onInit (not onLoad). onActive fires when the player is in the world.
    onInit = function()
      trySyncBalance(false)
      undeadFriendly.update()
    end,

    onLoad = function()
      tutorialShown = playerStore:get(STORE_TUTORIAL) or false
      trySyncBalance(false)
      undeadFriendly.update()
    end,

    onActive = function()
      balanceSynced = false
      trySyncBalance(false)
      undeadFriendly.update()
    end,

    onFrame = function(dt)
      if not balanceSynced then
        trySyncBalance(false)
      end
      undeadCheckTimer = undeadCheckTimer + dt
      if undeadCheckTimer >= UNDEAD_CHECK_INTERVAL then
        undeadCheckTimer = 0
        undeadFriendly.update()
      end
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
