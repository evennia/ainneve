"""
Character sheet EvForm template.
"""

import re

FORMCHAR = "x"
TABLECHAR = "o"

FORM = """
-=-=-=-=-=-=-=-=-=-=-=-=-=-=|C[ |rCharacter Info |C]|n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|
                                                                             |
  |YName|n: xxxxxxxxxxxxxAxxxxxxxxxxxxxx     |YXP|n: xxCxx / xxxxDxxxx   |YLevel|n: xEx  |
  |YArchetype|n: xxxxxxxxxxxBxxxxxxxxxxx                                         |
                                       +-------------------------------------|
  ooooooooooooooooooooooooooooooooooo  | |YPrimary Traits   |CStrength|n    : xFx  |
  ooooooooooooooooo1ooooooooooooooooo  | ~~~~~~~~~~~~~~   |CPerception|n  : xGx  |
  ooooooooooooooooooooooooooooooooooo  |                  |CIntelligence|n: xHx  |
                                       |                  |CDexterity|n   : xIx  |
  |YRace|n:           xxxxxxxxxxxYxxxxxx   |                  |CCharisma|n    : xJx  |
  |YFocus|n:          xxxxxxxxxxxZxxxxxx   |                  |CVitality|n    : xKx  |
  |YDescription|n                          |                  |CMagic|n       : xLx  |
  ~~~~~~~~~~~                          ||-------------------------------------|
  ooooooooooooooooo2ooooooooooooooooo  | |YSave Rolls       |CFortitude|n   : xMx  |
  ooooooooooooooooooooooooooooooooooo  | ~~~~~~~~~~       |CReflex|n      : xNx  |
                                       |                  |CWill|n        : xOx  |
  |YEncumbrance|n                          ||-------------------------------------|
  ~~~~~~~~~~~                          | |YCombat Stats     |CMelee|n       : xPx  |
  |CCarry Weight|n:          xUxx / xVxx   | ~~~~~~~~~~~~     |CRanged|n      : xQx  |
  |CEncumbrance Penalty|n:          xWxx   | |CPower Point      Unarmed|n     : xRx  |
  |CMovement Points|n:              xXxx   | |CBonus|n:   xTx     |CDefense|n     : xSx  |
                                       +-------------------------------------|
"""

FORM = re.sub(r'\|$', r'', FORM, flags=re.M)
