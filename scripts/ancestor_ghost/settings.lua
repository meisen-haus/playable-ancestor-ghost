local I = require('openmw.interfaces')
local config = require('scripts.ancestor_ghost.config')

local M = {}

function M.registerPage()
  I.Settings.registerPage({
    key = config.settingsPageKey,
    l10n = 'AncestorGhost',
    name = 'AncestorGhost',
    description = 'settingsPageDescription',
  })
end

function M.registerGroup()
  I.Settings.registerGroup({
    key = config.settingsGroupKey,
    page = config.settingsPageKey,
    l10n = 'AncestorGhost',
    name = 'modSettings',
    description = 'modSettingsDescription',
    permanentStorage = false,
    order = 0,
    settings = {
      {
        key = config.settingWraithKey,
        renderer = 'checkbox',
        name = 'wraithOfSulSenipul',
        description = 'wraithOfSulSenipulDescription',
        default = false,
      },
      {
        key = config.settingNormalWeaponsKey,
        renderer = 'select',
        name = 'normalWeaponsImmunity',
        description = 'normalWeaponsImmunityDescription',
        default = 100,
        argument = {
          l10n = 'AncestorGhost',
          items = { 100, 50, 0 },
        },
      },
    },
  })
end

return M
