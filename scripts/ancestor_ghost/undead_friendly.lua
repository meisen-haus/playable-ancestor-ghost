-- Optional tomb-undead pacify (USkele-style): zero Fight on undead creatures while enabled.

local types = require('openmw.types')
local world = require('openmw.world')
local self = require('openmw.self')
local config = require('scripts.ancestor_ghost.config')
local playerSettings = require('scripts.ancestor_ghost.player_settings')

local M = {}

local pacified = setmetatable({}, { __mode = 'k' })

local function isUndeadCreature(actor)
  if not types.Creature.objectIsInstance(actor) then return false end
  if types.Actor.isDead(actor) then return false end
  local rec = types.Creature.record(actor)
  return rec ~= nil and rec.type == types.Creature.TYPE.Undead
end

local function pacify(actor)
  local fight = types.Actor.stats(actor).ai.fight(actor)
  if pacified[actor] ~= nil then return end
  pacified[actor] = fight.modifier
  if fight.modified > 0 then
    fight.modifier = fight.modifier - fight.modified
  end
  actor:sendEvent('RemoveAIPackages', 'Combat')
end

function M.restoreAll()
  for actor, modifier in pairs(pacified) do
    pacified[actor] = nil
    if actor:isValid() and types.Actor.objectIsInstance(actor) then
      types.Actor.stats(actor).ai.fight(actor).modifier = modifier
    end
  end
end

function M.update()
  local rec = types.NPC.record(self)
  if not rec or rec.race ~= config.RACE_ID then
    M.restoreAll()
    return
  end

  local settings = playerSettings.readFromStorage()
  if not settings.undeadFriendly then
    M.restoreAll()
    return
  end

  for _, actor in ipairs(world.activeActors) do
    if isUndeadCreature(actor) then
      pacify(actor)
    end
  end
end

return M
