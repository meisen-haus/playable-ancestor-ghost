#!/usr/bin/env node
/**
 * Builds ancestor_ghost.omwaddon containing:
 *   - 17× SPEL records  (12× ghostly nature immunity×levitate×disease, ghost curse, wraith kit)
 *   - 1×  BSGN record   (Bonebiter birthsign — wraith kit at character creation)
 *   - BODY records      (Dunmer placeholder + ag\ stubs; 1 head + 1 hair per gender)
 *   - 1×  RACE record   (Ancestor Ghost playable race)
 *
 * Run: node tools/build_esp.mjs
 */

import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, '..', 'ancestor_ghost.omwaddon');

// ---------------------------------------------------------------------------
// Effect IDs — ENAM stores OpenMW MagicEffect indices (sMagicEffectIds in
// loadmgef.cpp), NOT legacy editor effect numbers.
// ---------------------------------------------------------------------------
const FX = {
  LEVITATE              : 10, // Levitate (constant on Ghostly Nature)
  CHAMELEON             : 40, // Chameleon (OpenMW sMagicEffectIds index; 41 is Light)
  RESIST_NORMAL_WEAPONS : 98, // ResistNormalWeapons (vanilla resist fire_75 uses 90)
  RESIST_FROST          : 91, // ResistFrost (Ghostly Nature)
  RESIST_SHOCK          : 92, // ResistShock (Wraith)
  RESIST_COMMON_DISEASE : 94, // ResistCommonDisease
  RESIST_POISON         : 97, // ResistPoison
  DRAIN_ATTRIBUTE       : 17, // DrainAttribute
  DRAIN_FATIGUE         : 20, // DrainFatigue
  DAMAGE_HEALTH         : 23, // DamageHealth
  FORTIFY_MAX_MAGICKA   : 84, // FortifyMaximumMagicka (M/10 adds to INT multiplier; 20 → 3× INT)
  FORTIFY_ATTRIBUTE     : 79, // FortifyAttribute (Wraith: +25 Endurance)
  DAMAGE_ATTRIBUTE      : 22, // DamageAttribute (Bonebiter)
};
// Morrowind attribute indices (MWSE / OpenMW ESM::Attribute); see daedric_willpower (at 2), daedric_endurance (at 5).
const ATTR = {
  STRENGTH: 0,
  INTELLIGENCE: 1,
  WILLPOWER: 2,
  AGILITY: 3,
  SPEED: 4,
  ENDURANCE: 5,
  PERSONALITY: 6,
  LUCK: 7,
};

// Skin meshes from Morrowind.esm (Dark Elf BODY records). Clavicle (part 13) omitted.
const DUNMER_SKIN = {
  Neck     : { m: 'b\\B_N_Dark Elf_M_Neck.NIF',      f: 'b\\B_N_Dark Elf_F_Neck.nif' },
  Chest    : { m: 'b\\B_N_Dark Elf_M_Skins.NIF',     f: 'b\\B_N_Dark Elf_F_Skins.nif' },
  Groin    : { m: 'b\\B_N_Dark Elf_M_Groin.NIF',     f: 'b\\B_N_Dark Elf_F_Groin.nif' },
  Hand     : { m: 'b\\B_N_Dark Elf_M_Skins.NIF',     f: 'b\\B_N_Dark Elf_F_Skins.nif' },
  Wrist    : { m: 'b\\B_N_Dark Elf_M_Wrist.NIF',     f: 'b\\B_N_Dark Elf_F_Wrist.nif' },
  Forearm  : { m: 'b\\B_N_Dark Elf_M_Forearm.NIF',   f: 'b\\B_N_Dark Elf_F_Forearm.nif' },
  UpperArm : { m: 'b\\B_N_Dark Elf_M_Upper Arm.NIF', f: 'b\\B_N_Dark Elf_F_Upper Arm.nif' },
  Foot     : { m: 'b\\B_N_Dark Elf_M_Foot.NIF',      f: 'b\\B_N_Dark Elf_F_Foot.nif' },
  Ankle    : { m: 'b\\B_N_Dark Elf_M_Ankle.NIF',     f: 'b\\B_N_Dark Elf_F_Ankle.nif' },
  Knee     : { m: 'b\\B_N_Dark Elf_M_Knee.NIF',      f: 'b\\B_N_Dark Elf_F_Knee.nif' },
  UpperLeg : { m: 'b\\B_N_Dark Elf_M_Upper Leg.NIF', f: 'b\\B_N_Dark Elf_F_Upper Leg.nif' },
};

// Invisible leg stubs (Meshes/ag/); unisex paths for smoke-test / future ghost mesh work.
const AG_LEG = {
  Foot     : { m: 'ag\\ag_foot.nif',     f: 'ag\\ag_foot.nif' },
  Ankle    : { m: 'ag\\ag_ankle.nif',    f: 'ag\\ag_ankle.nif' },
  Knee     : { m: 'ag\\ag_knee.nif',     f: 'ag\\ag_knee.nif' },
  UpperLeg : { m: 'ag\\ag_upperleg.nif', f: 'ag\\ag_upperleg.nif' },
};

// Invisible arm stubs — full vanilla geometry with alpha=0 (see tools/build_invisible_stubs.py).
const AG_ARM = {
  Wrist    : { m: 'ag\\ag_wrist.nif',    f: 'ag\\ag_wrist.nif' },
  Forearm  : { m: 'ag\\ag_forearm.nif',  f: 'ag\\ag_forearm.nif' },
  UpperArm : { m: 'ag\\ag_upperarm.nif', f: 'ag\\ag_upperarm.nif' },
};

const AG_NECK = { m: 'ag\\ag_neck.nif', f: 'ag\\ag_neck.nif' };
const AG_GROIN = { m: 'ag\\ag_groin.nif', f: 'ag\\ag_groin.nif' };

// Ghost torso + hands (Chest/Hand slots share ag_chest.nif like vanilla Skins.nif).
const AG_CHEST = { m: 'ag\\ag_chest.nif', f: 'ag\\ag_chest.nif' };

const AG_SKIN = {
  ...DUNMER_SKIN,
  Neck: AG_NECK,
  Groin: AG_GROIN,
  Chest: AG_CHEST,
  Hand: AG_CHEST,
  ...AG_ARM,
  ...AG_LEG,
};

// Head: morpher ag_head.nif (Head-bone attach — NPC look-at / talk; chest stays rigid).
const HEAD_VARIANTS = {
  m: ['ag\\ag_head.nif'],
  f: ['ag\\ag_head.nif'],
};

const HAIR_VARIANTS = {
  m: ['ag\\ag_hair.nif'],
  f: ['ag\\ag_hair.nif'],
};

// OpenMW ESM::BodyPart::MeshPart indices (not armor biped slots).
const PART = {
  Head: 0, Hair: 1, Neck: 2, Chest: 3, Groin: 4, Hand: 5,
  Wrist: 6, Forearm: 7, UpperArm: 8, Foot: 9, Ankle: 10, Knee: 11, UpperLeg: 12,
};

const RACE_ID = 'ancestor_ghost';

// Body part type: 0=skin, 1=clothing, 2=armor
const BPTYPE = 0; // skin

// ---------------------------------------------------------------------------
// Binary helpers
// ---------------------------------------------------------------------------
function subrecord(type, data) {
  const payload = Buffer.isBuffer(data) ? data : Buffer.from(data, 'utf8');
  const header  = Buffer.alloc(8);
  header.write(type, 0, 4, 'ascii');
  header.writeInt32LE(payload.length, 4);
  return Buffer.concat([header, payload]);
}

function record(type, subrecords) {
  const body   = Buffer.concat(subrecords);
  const header = Buffer.alloc(16);
  header.write(type, 0, 4, 'ascii');
  header.writeInt32LE(body.length, 4);
  header.writeInt32LE(0, 8);
  header.writeInt32LE(0, 12);
  return Buffer.concat([header, body]);
}

function zstring(str) { return Buffer.from(`${str}\0`, 'utf8'); }
function padId(id) {
  const buf = Buffer.alloc(32);
  buf.write(id, 0, 'ascii');
  return buf;
}

// ---------------------------------------------------------------------------
// TES3 header
// ---------------------------------------------------------------------------
function buildTes3Header(recordCount) {
  const hedr = Buffer.alloc(300);
  hedr.writeFloatLE(1.2, 0);
  hedr.writeInt32LE(1, 4);
  Buffer.from('Ancestor Ghost Race\0', 'ascii').copy(hedr, 8, 0, 32);
  Buffer.from(
    'Adds the Ancestor Ghost as a playable Dunmer-bodied race with ghostly resistances and Chameleon.\0',
    'ascii'
  ).copy(hedr, 40, 0, 256);
  hedr.writeInt32LE(recordCount, 296);

  const masterSize = Buffer.alloc(8);
  masterSize.writeBigInt64LE(0n, 0);

  return record('TES3', [
    subrecord('HEDR', hedr),
    subrecord('MAST', zstring('Morrowind.esm')),
    subrecord('DATA', masterSize),
  ]);
}

// ---------------------------------------------------------------------------
// SPEL helpers
// ---------------------------------------------------------------------------
function spdt(type, cost, flags) {
  const buf = Buffer.alloc(12);
  buf.writeInt32LE(type,  0);
  buf.writeInt32LE(cost,  4);
  buf.writeInt32LE(flags, 8);
  return buf;
}

function enam({ effectId, skillId = -1, attributeId = -1, range = 0, area = 0, duration, magMin, magMax }) {
  const buf = Buffer.alloc(24);
  buf.writeInt16LE(effectId,     0);
  buf.writeInt8(skillId,         2);
  buf.writeInt8(attributeId,     3);
  buf.writeInt32LE(range,        4);
  buf.writeInt32LE(area,         8);
  buf.writeInt32LE(duration,    12);
  buf.writeInt32LE(magMin,      16);
  buf.writeInt32LE(magMax,      20);
  return buf;
}

// ---------------------------------------------------------------------------
// SPEL: ag_ghostly_nature_{100,50,0}_{lev,ground}_{dis,nodis}  (balance.lua picks one)
// ---------------------------------------------------------------------------
function buildGhostlyNatureSpell(spellId, resistNormalWeapons, withLevitate, withDiseaseResist) {
  const enams = [
    subrecord('ENAM', enam({ effectId: FX.CHAMELEON,           duration: 0, magMin: 50,  magMax: 50  })),
    subrecord('ENAM', enam({ effectId: FX.RESIST_FROST,        duration: 0, magMin: 100, magMax: 100 })),
    subrecord('ENAM', enam({ effectId: FX.RESIST_POISON,       duration: 0, magMin: 100, magMax: 100 })),
    subrecord('ENAM', enam({ effectId: FX.FORTIFY_MAX_MAGICKA, duration: 0, magMin: 20,  magMax: 20  })),
  ];
  if (withDiseaseResist) {
    enams.push(
      subrecord('ENAM', enam({ effectId: FX.RESIST_COMMON_DISEASE, duration: 0, magMin: 100, magMax: 100 })),
    );
  }
  if (withLevitate) {
    enams.unshift(subrecord('ENAM', enam({
      effectId: FX.LEVITATE,
      duration: 0,
      magMin: 10,
      magMax: 10,
    })));
  }
  if (resistNormalWeapons > 0) {
    const insertAt = withLevitate ? 1 : 0;
    enams.splice(insertAt, 0, subrecord('ENAM', enam({
      effectId: FX.RESIST_NORMAL_WEAPONS,
      duration: 0,
      magMin: resistNormalWeapons,
      magMax: resistNormalWeapons,
    })));
  }
  return record('SPEL', [
    subrecord('NAME', zstring(spellId)),
    subrecord('FNAM', zstring('Ghostly Nature')),
    subrecord('SPDT', spdt(1, 0, 0x0000)),
    ...enams,
  ]);
}

// ---------------------------------------------------------------------------
// SPEL: ag_ghost_curse  (active touch spell)
// ---------------------------------------------------------------------------
function buildGhostCurseSpell() {
  return record('SPEL', [
    subrecord('NAME', zstring('ag_ghost_curse')),
    subrecord('FNAM', zstring('Ghost Curse')),
    // flags 0: use cost field. flags 1 (F_Autocalc) recalculates ~40 like vanilla Ghost Curse.
    subrecord('SPDT', spdt(0, 9, 0x0000)),
    subrecord('ENAM', enam({ effectId: FX.DRAIN_ATTRIBUTE, attributeId: ATTR.ENDURANCE, range: 1, duration: 30, magMin: 5,  magMax: 5  })),
    subrecord('ENAM', enam({ effectId: FX.DRAIN_FATIGUE,                                range: 1, duration: 30, magMin: 10, magMax: 10 })),
    subrecord('ENAM', enam({ effectId: FX.DAMAGE_HEALTH,                                range: 1, duration: 0,  magMin: 1,  magMax: 10 })),
  ]);
}

// Tomb-wraith kit (granted via Bonebiter birthsign at character creation)
function buildWraithAbility() {
  return record('SPEL', [
    subrecord('NAME', zstring('ag_wraith_sul')),
    subrecord('FNAM', zstring('Wraith')),
    subrecord('SPDT', spdt(1, 0, 0x0000)),
    subrecord('ENAM', enam({ effectId: FX.FORTIFY_ATTRIBUTE, attributeId: ATTR.ENDURANCE, duration: 0, magMin: 25, magMax: 25 })),
    subrecord('ENAM', enam({ effectId: FX.RESIST_SHOCK,      duration: 0, magMin: 100, magMax: 100 })),
  ]);
}

function buildWraithGraveFatigue() {
  return record('SPEL', [
    subrecord('NAME', zstring('ag_wraith_grave_fatigue')),
    subrecord('FNAM', zstring('Grave Curse: Fatigue')),
    subrecord('SPDT', spdt(0, 0, 0x0001)),
    subrecord('ENAM', enam({ effectId: FX.DRAIN_FATIGUE, range: 2, duration: 10, magMin: 2, magMax: 4 })),
  ]);
}

function buildWraithGraveStrength() {
  return record('SPEL', [
    subrecord('NAME', zstring('ag_wraith_grave_strength')),
    subrecord('FNAM', zstring('Grave Curse: Strength')),
    subrecord('SPDT', spdt(0, 0, 0x0001)),
    subrecord('ENAM', enam({ effectId: FX.DRAIN_ATTRIBUTE, attributeId: ATTR.STRENGTH, range: 2, duration: 60, magMin: 2, magMax: 4 })),
  ]);
}

function buildWraithBonebiter() {
  return record('SPEL', [
    subrecord('NAME', zstring('ag_wraith_bonebiter')),
    subrecord('FNAM', zstring('Bonebiter')),
    subrecord('SPDT', spdt(0, 0, 0x0001)),
    subrecord('ENAM', enam({ effectId: FX.DAMAGE_ATTRIBUTE, attributeId: ATTR.AGILITY, range: 2, duration: 1, magMin: 20, magMax: 20 })),
  ]);
}

// ---------------------------------------------------------------------------
// BODY records — one per slot per gender
//
// BODY subrecord layout (BYDT): 4 bytes
//   byte 0: part index
//   byte 1: unknown (0)
//   byte 2: flags  (0x01 = female, 0x00 = male)
//   byte 3: part type (0=skin)
// ---------------------------------------------------------------------------
function buildBodyRecord(id, partIndex, isFemale, mesh) {
  const bydt = Buffer.alloc(4);
  bydt.writeUInt8(partIndex,       0);
  bydt.writeUInt8(0,               1);
  bydt.writeUInt8(isFemale ? 1 : 0, 2);
  bydt.writeUInt8(BPTYPE,          3);

  return record('BODY', [
    subrecord('NAME', zstring(id)),
    subrecord('MODL', zstring(mesh)),
  // FNAM on BODY records stores the race ID (not a display name).
    subrecord('FNAM', zstring(RACE_ID)),
    subrecord('BYDT', bydt),
  ]);
}

function buildVariantBodyRecords(partIndex, genderKey, idPrefix, meshes) {
  const records = [];
  const isFemale = genderKey === 'f';
  meshes.forEach((mesh, i) => {
    const num = String(i + 1).padStart(2, '0');
    records.push(buildBodyRecord(`${idPrefix}_${genderKey}_${num}`, partIndex, isFemale, mesh));
  });
  return records;
}

// Build all BODY records: Dunmer skin (ag\ leg stubs) + head/hair variants for char gen.
function buildAllBodyRecords() {
  const records = [];

  for (const [name, idx] of Object.entries(PART)) {
    if (name === 'Head' || name === 'Hair') continue;
    const skin = AG_SKIN[name];
    records.push(buildBodyRecord(`ag_${name.toLowerCase()}_m`, idx, false, skin.m));
    records.push(buildBodyRecord(`ag_${name.toLowerCase()}_f`, idx, true, skin.f));
  }

  records.push(...buildVariantBodyRecords(PART.Head, 'm', 'ag_head', HEAD_VARIANTS.m));
  records.push(...buildVariantBodyRecords(PART.Head, 'f', 'ag_head', HEAD_VARIANTS.f));
  records.push(...buildVariantBodyRecords(PART.Hair, 'm', 'ag_hair', HAIR_VARIANTS.m));
  records.push(...buildVariantBodyRecords(PART.Hair, 'f', 'ag_hair', HAIR_VARIANTS.f));

  return records;
}

// ---------------------------------------------------------------------------
// RACE record
//
// RADT layout (140 bytes):
//   Skill bonuses : 7 × (int32 skillId + int32 bonus) = 56 bytes  [0..55]
//   Attributes    : 16 × int32 interleaved by attribute (OpenMW    [56..119]
//                   ESM::Race::RADTstruct::mAttributeValues):
//                   Str♂, Str♀, Int♂, Int♀, Wil♂, Wil♀, Agi♂, Agi♀,
//                   Spd♂, Spd♀, End♂, End♀, Per♂, Per♀, Lck♂, Lck♀
//   Height male/female float: 8 bytes                             [120..127]
//   Weight male/female float: 8 bytes                             [128..135]
//   Flags int32: 4 bytes                                          [136..139]
//     0x01=Playable, 0x02=Beast Race
//
// Valid RACE subrecords (OpenMW esm3/loadrace.cpp): NAME, FNAM, RADT,
// NPCS, DESC. Body parts are separate BODY records whose FNAM subrecord
// holds the race ID; OpenMW scans BODY records by race + BYDT part/gender.
// ---------------------------------------------------------------------------
const RACE_ATTRS = [30, 50, 50, 50, 50, 20, 20, 40];
const RACE_SKILLS = [
  [10, 15], [14, 10], [11, 10], [13, 10], // Destruction, Mysticism, Alteration, Conjuration
  [-1, 0], [-1, 0], [-1, 0],
];

function buildRaceRecord() {
  const radt = Buffer.alloc(140);
  let o = 0;
  for (const [skillId, bonus] of RACE_SKILLS) {
    radt.writeInt32LE(skillId, o); o += 4;
    radt.writeInt32LE(bonus,   o); o += 4;
  }
  for (const v of RACE_ATTRS) {
    radt.writeInt32LE(v, o); o += 4; // male
    radt.writeInt32LE(v, o); o += 4; // female (same targets for both)
  }
  radt.writeFloatLE(1.0, o); o += 4;
  radt.writeFloatLE(1.0, o); o += 4;
  radt.writeFloatLE(1.0, o); o += 4;
  radt.writeFloatLE(1.0, o); o += 4;
  radt.writeInt32LE(0x01, o); // Playable only (not Beast — beast skeleton breaks Dunmer head preview)

  const subs = [
    subrecord('NAME', zstring('ancestor_ghost')),
    subrecord('FNAM', zstring('Ancestor Ghost')),
    subrecord('RADT', radt),
    // Default racial ability at chargen; balance.lua swaps variant from mod settings.
    subrecord('NPCS', padId('ag_ghost_curse')),
    subrecord('NPCS', padId('ag_ghostly_nature_100_ground_dis')),
    subrecord('DESC', zstring(
      'The Ancestor Ghost is an undead spirit of the Dunmer, bound to the mortal plane. ' +
      'Spectral and untouchable by mundane weapons, they cannot wield physical arms or don ' +
      'armour, relying instead on ancient magic and incorporeal resilience. Their touch drains ' +
      'the living, and frost and poison pass through them like wind through smoke.'
    )),
  ];

  return record('RACE', subs);
}

// ---------------------------------------------------------------------------
// BSGN: Bonebiter (Wraith of Sul-Senipul — pick at character creation)
// ---------------------------------------------------------------------------
function buildBonebiterBirthsign() {
  return record('BSGN', [
    subrecord('NAME', zstring('ag_sign_bonebiter')),
    subrecord('FNAM', zstring('Bonebiter')),
    subrecord('TNAM', zstring('Birthsigns\\Tx_birth_bonebiter.tga')),
    subrecord('DESC', zstring(
      'Born under the wraith-star of Sul-Senipul, you are a tomb-bound hunger that gnaws at bone and sinew. ' +
      'The grave grants you endurance beyond the dust, immunity to shock, and curses to drain the living.'
    )),
    subrecord('NPCS', padId('ag_wraith_sul')),
    subrecord('NPCS', padId('ag_wraith_grave_fatigue')),
    subrecord('NPCS', padId('ag_wraith_grave_strength')),
    subrecord('NPCS', padId('ag_wraith_bonebiter')),
  ]);
}

// ---------------------------------------------------------------------------
// Assemble plugin
// ---------------------------------------------------------------------------
const bodyRecords  = buildAllBodyRecords();            // 22 skin + 2 head + 2 hair = 26 BODY
const GHOSTLY_IMMUNITY = [100, 50, 0];
const SPELL_RECORDS = [
  ...GHOSTLY_IMMUNITY.flatMap((mag) => [
    buildGhostlyNatureSpell(`ag_ghostly_nature_${mag}_lev_dis`, mag, true, true),
    buildGhostlyNatureSpell(`ag_ghostly_nature_${mag}_lev_nodis`, mag, true, false),
    buildGhostlyNatureSpell(`ag_ghostly_nature_${mag}_ground_dis`, mag, false, true),
    buildGhostlyNatureSpell(`ag_ghostly_nature_${mag}_ground_nodis`, mag, false, false),
  ]),
  buildGhostCurseSpell(),
  buildWraithAbility(),
  buildWraithGraveFatigue(),
  buildWraithGraveStrength(),
  buildWraithBonebiter(),
];
const CONTENT_RECORDS = SPELL_RECORDS.length + bodyRecords.length + 2;

const allRecords = [
  buildTes3Header(CONTENT_RECORDS),
  ...SPELL_RECORDS,
  ...bodyRecords,
  buildRaceRecord(),
  buildBonebiterBirthsign(),
];

const plugin = Buffer.concat(allRecords);
writeFileSync(OUT, plugin);

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------
const text = plugin.toString('binary');
const required = [
  ['ag_ghostly_nature_100_ground_dis', 'Ghostly Nature 100% grounded + disease ID'],
  ['ag_ghostly_nature_50_lev_nodis', 'Ghostly Nature 50% + levitate, no disease ID'],
  ['ag_ghostly_nature_0_ground_nodis', 'Ghostly Nature 0% grounded, no disease ID'],
  ['ag_ghost_curse',             'Ghost Curse spell ID'],
  ['ag_wraith_sul',              'Wraith ability ID'],
  ['ag_wraith_grave_fatigue',    'Wraith Grave Curse Fatigue ID'],
  ['ag_wraith_bonebiter',        'Bonebiter spell ID'],
  ['ag_sign_bonebiter',          'Bonebiter birthsign ID'],
  ['ancestor_ghost',             'Race record ID'],
  ['Ancestor Ghost',             'Race display name'],
  ['ag_head_m_01',               'Male head body part ID'],
  ['ag_head_f_01',               'Female head body part ID'],
  ['ag_hair_m_01',               'Male hair body part ID'],
  ['ag_hair_f_01',               'Female hair body part ID'],
  ['ag\\ag_head.nif',            'Ghost head mesh (morpher, Head-bone attach)'],
  ['ag\\ag_neck.nif',             'Invisible neck stub mesh path'],
  ['ag\\ag_groin.nif',            'Invisible groin stub mesh path'],
  ['ag\\ag_chest.nif',            'Ghost chest/hand mesh path'],
  ['ag\\ag_wrist.nif',            'Invisible arm stub mesh path'],
  ['ag\\ag_foot.nif',            'Invisible leg stub mesh path'],
  ['ag\\ag_hair.nif',            'Invisible hair stub mesh path'],
  ['Ancestor Ghost is an undead','Race description'],
];

let ok = true;
for (const [needle, label] of required) {
  if (!text.includes(needle)) {
    console.error(`validation FAILED: missing ${label} ("${needle}")`);
    ok = false;
  }
}

// Sanity-check Wraith ability ENAM (catches wrong attribute / effect indices).
for (let i = 0; i < plugin.length - 16; i++) {
  if (plugin.slice(i, i + 4).toString('ascii') !== 'SPEL') continue;
  const size = plugin.readInt32LE(i + 4);
  const body = plugin.slice(i + 16, i + 16 + size);
  let o = 0;
  let id = '';
  const enams = [];
  while (o < body.length - 8) {
    const st = body.slice(o, o + 4).toString('ascii');
    const ss = body.readInt32LE(o + 4);
    const d = body.slice(o + 8, o + 8 + ss);
    o += 8 + ss;
    if (st === 'NAME') id = d.toString('binary').replace(/\0.*/, '');
    if (st === 'ENAM' && d.length >= 24) {
      enams.push({ e: d.readInt16LE(0), at: d.readInt8(3), mag: d.readInt32LE(16) });
    }
  }
  if (id !== 'ag_wraith_sul') continue;
  const fortify = enams.find((c) => c.e === FX.FORTIFY_ATTRIBUTE);
  if (!fortify || fortify.at !== ATTR.ENDURANCE || fortify.mag !== 25) {
    console.error('validation FAILED: ag_wraith_sul fortify endurance ENAM', enams);
    ok = false;
  }
  const shock = enams.find((c) => c.e === FX.RESIST_SHOCK);
  if (!shock || shock.mag !== 100) {
    console.error('validation FAILED: ag_wraith_sul resist shock ENAM', enams);
    ok = false;
  }
  break;
}

for (let i = 0; i < plugin.length - 16; i++) {
  if (plugin.slice(i, i + 4).toString('ascii') !== 'SPEL') continue;
  const size = plugin.readInt32LE(i + 4);
  const body = plugin.slice(i + 16, i + 16 + size);
  let o = 0;
  let spellId = '';
  while (o < body.length - 8) {
    const st = body.slice(o, o + 4).toString('ascii');
    const ss = body.readInt32LE(o + 4);
    const d = body.slice(o + 8, o + 8 + ss);
    o += 8 + ss;
    if (st === 'NAME') spellId = d.toString('binary').replace(/\0.*/, '');
    if (st === 'SPDT' && spellId === 'ag_ghost_curse' && d.length >= 12) {
      const cost = d.readInt32LE(4);
      const flags = d.readUInt32LE(8);
      if (cost !== 9 || flags !== 0) {
        console.error(`validation FAILED: ag_ghost_curse SPDT cost=${cost} flags=0x${flags.toString(16)}`);
        ok = false;
      }
    }
  }
}

for (const [id, resist, withLevitate, withDiseaseResist] of [
  ['ag_ghostly_nature_100_lev_dis', 100, true, true],
  ['ag_ghostly_nature_100_lev_nodis', 100, true, false],
  ['ag_ghostly_nature_100_ground_dis', 100, false, true],
  ['ag_ghostly_nature_100_ground_nodis', 100, false, false],
  ['ag_ghostly_nature_50_lev_dis', 50, true, true],
  ['ag_ghostly_nature_50_lev_nodis', 50, true, false],
  ['ag_ghostly_nature_50_ground_dis', 50, false, true],
  ['ag_ghostly_nature_50_ground_nodis', 50, false, false],
  ['ag_ghostly_nature_0_lev_dis', 0, true, true],
  ['ag_ghostly_nature_0_lev_nodis', 0, true, false],
  ['ag_ghostly_nature_0_ground_dis', 0, false, true],
  ['ag_ghostly_nature_0_ground_nodis', 0, false, false],
]) {
  for (let i = 0; i < plugin.length - 16; i++) {
    if (plugin.slice(i, i + 4).toString('ascii') !== 'SPEL') continue;
    const size = plugin.readInt32LE(i + 4);
    const body = plugin.slice(i + 16, i + 16 + size);
    let o = 0;
    let spellId = '';
    const enams = [];
    while (o < body.length - 8) {
      const st = body.slice(o, o + 4).toString('ascii');
      const ss = body.readInt32LE(o + 4);
      const d = body.slice(o + 8, o + 8 + ss);
      o += 8 + ss;
      if (st === 'NAME') spellId = d.toString('binary').replace(/\0.*/, '');
      if (st === 'ENAM' && d.length >= 24) {
        enams.push({ e: d.readInt16LE(0), mag: d.readInt32LE(16) });
      }
    }
    if (spellId !== id) continue;
    const lev = enams.find((c) => c.e === FX.LEVITATE);
    if (withLevitate) {
      if (!lev || lev.mag !== 10) {
        console.error(`validation FAILED: ${id} missing levitate ENAM`, enams);
        ok = false;
      }
    } else if (lev) {
      console.error(`validation FAILED: ${id} should omit levitate ENAM`, enams);
      ok = false;
    }
    const rnw = enams.find((c) => c.e === FX.RESIST_NORMAL_WEAPONS);
    if (resist === 0) {
      if (rnw) {
        console.error(`validation FAILED: ${id} should omit resist normal weapons`, enams);
        ok = false;
      }
    } else if (!rnw || rnw.mag !== resist) {
      console.error(`validation FAILED: ${id} resist normal weapons ENAM`, enams);
      ok = false;
    }
    const commonDis = enams.find((c) => c.e === FX.RESIST_COMMON_DISEASE);
    if (withDiseaseResist) {
      if (!commonDis || commonDis.mag !== 100) {
        console.error(`validation FAILED: ${id} missing common disease resist ENAM`, enams);
        ok = false;
      }
    } else if (commonDis) {
      console.error(`validation FAILED: ${id} should omit common disease resist ENAM`, enams);
      ok = false;
    }
    break;
  }
}

if (ok) {
  console.log(`Wrote ${OUT} (${plugin.length} bytes, ${CONTENT_RECORDS} content records)`);
} else {
  process.exit(1);
}
