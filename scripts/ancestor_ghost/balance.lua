-- Applies in-game settings to Ancestor Ghost players (ghostly nature variant + wraith kit).

local types = require('openmw.types')
local config = require('scripts.ancestor_ghost.config')
local playerSettings = require('scripts.ancestor_ghost.player_settings')

local function isAncestorGhost(player)
  local rec = types.NPC.record(player)
  return rec and rec.race == config.RACE_ID
end

local function stripLegacySpells(player)
  local spells = types.Actor.spells(player)
  for _, spellId in ipairs(config.LEGACY_GHOSTLY_NATURE_SPELLS) do
    if spells[spellId] then
      spells:remove(spellId)
    end
  end
  for _, spellId in ipairs(config.LEGACY_WRAITH_ABILITIES) do
    if spells[spellId] then
      spells:remove(spellId)
    end
  end
end

local function applyGhostlyNature(player, immunityMag)
  local spells = types.Actor.spells(player)
  local target = config.GHOSTLY_NATURE_BY_IMMUNITY[immunityMag]
    or config.GHOSTLY_NATURE_BY_IMMUNITY[100]
  for _, spellId in ipairs(config.GHOSTLY_NATURE_VARIANTS) do
    if spellId ~= target and spells[spellId] then
      spells:remove(spellId)
    end
  end
  if not spells[target] then
    spells:add(target)
  end
end

local function enableWraith(player)
  local spells = types.Actor.spells(player)
  if spells[config.SPELL_WRAITH] then
    spells:remove(config.SPELL_WRAITH)
  end
  spells:add(config.SPELL_WRAITH)
  for _, spellId in ipairs(config.WRAITH_SPELLS) do
    if not spells[spellId] then
      spells:add(spellId)
    end
  end
end

local function disableWraith(player)
  local spells = types.Actor.spells(player)
  for _, spellId in ipairs(config.WRAITH_SPELLS) do
    if spells[spellId] then
      spells:remove(spellId)
    end
  end
  if spells[config.SPELL_WRAITH] then
    spells:remove(config.SPELL_WRAITH)
  end
end

local function applyToPlayer(player, settings)
  if not isAncestorGhost(player) then return false end
  stripLegacySpells(player)
  settings = settings or playerSettings.readFromStorage()
  applyGhostlyNature(player, settings.normalWeaponsImmunity)
  if settings.wraith then
    enableWraith(player)
  else
    disableWraith(player)
  end
  return true
end

return {
  applyToPlayer = applyToPlayer,
}
