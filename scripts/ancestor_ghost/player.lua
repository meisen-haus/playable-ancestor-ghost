-- ancestor_ghost/player.lua
-- PLAYER script: one-time tutorial when a locked equipment slot is blocked.
-- Racial spells (Ghostly Nature, Ghost Curse) come from the RACE record in the ESP.

local ui      = require('openmw.ui')
local storage = require('openmw.storage')

local playerStore    = storage.playerSection('AncestorGhost')
local STORE_TUTORIAL = 'ag_tutorial_shown'
local tutorialShown  = false

return {
  engineHandlers = {
    onLoad = function()
      tutorialShown = playerStore:get(STORE_TUTORIAL) or false
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
