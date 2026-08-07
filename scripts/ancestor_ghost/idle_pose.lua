-- Soft float pose for Ancestor Ghost when not in weapon/spell stance (3rd person).
-- One IdleSpell blend on Torso + arms: holds the robe against walk spine bob and
-- keeps soft-ready arms. Uses IdleSpell (not Idle) so standing Idle on the legs
-- is not replaced. Skipped in first person so unready stays lower in FOV.
--
-- Important: magic-ready also uses the IdleSpell group. Only cancel when *we*
-- started the soft-float blend — never cancel the engine's spell-stance IdleSpell.

local anim = require('openmw.animation')
local camera = require('openmw.camera')
local types = require('openmw.types')
local self = require('openmw.self')
local I = require('openmw.interfaces')

local config = require('scripts.ancestor_ghost.config')

local GROUP = 'idlespell'
local ACCUM = 0
local INTERVAL = 0.35
local floatActive = false

local function isGhost()
  local ok, rec = pcall(types.Player.record, self)
  return ok and rec and rec.race == config.RACE_ID
end

local function isFirstPerson()
  local ok, mode = pcall(camera.getMode)
  if not ok then
    return false
  end
  return mode == camera.MODE.FirstPerson
end

local function wantSoftFloat()
  if not isGhost() then
    return false
  end
  if isFirstPerson() then
    return false
  end
  if not anim.hasAnimation(self) then
    return false
  end
  if not anim.hasGroup(self, GROUP) then
    return false
  end
  return types.Actor.getStance(self) == types.Actor.STANCE.Nothing
end

local function playFloat()
  I.AnimationController.playBlendedAnimation(GROUP, {
    loops = 9999,
    forceLoop = true,
    autoDisable = false,
    blendMask = (
      anim.BLEND_MASK.Torso
      + anim.BLEND_MASK.LeftArm
      + anim.BLEND_MASK.RightArm
    ),
    priority = {
      [anim.BONE_GROUP.Torso] = anim.PRIORITY.Weapon,
      [anim.BONE_GROUP.LeftArm] = anim.PRIORITY.Weapon,
      [anim.BONE_GROUP.RightArm] = anim.PRIORITY.Weapon,
    },
    startKey = 'start',
    stopKey = 'stop',
  })
  floatActive = true
end

local function stopFloat()
  if not floatActive then
    return
  end
  local stance = types.Actor.getStance(self)
  -- Spell stance owns IdleSpell — do not cancel or magic-ready restarts every poll.
  if stance ~= types.Actor.STANCE.Spell and anim.isPlaying(self, GROUP) then
    anim.cancel(self, GROUP)
  end
  floatActive = false
end

local function ensurePose()
  if wantSoftFloat() then
    if not floatActive or not anim.isPlaying(self, GROUP) then
      playFloat()
    end
  else
    stopFloat()
  end
end

local function onFrame(dt)
  ACCUM = ACCUM + (dt or 0)
  if ACCUM < INTERVAL then
    return
  end
  ACCUM = 0
  pcall(ensurePose)
end

return {
  onFrame = onFrame,
  ensurePose = ensurePose,
}
