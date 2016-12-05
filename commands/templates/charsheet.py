"""
Character sheet EvForm template.
"""

import re

FORMCHAR = "x"
TABLECHAR = "o"

FORM = """
-=-=-=-=-=-=-=-=-=-=-=-=-=-=|C[ |rCharacter Info |C]|n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-o
                                                                             ||
  |YName|n: xxxxxxxxxxxxxAxxxxxxxxxxxxxx     |YXP|n: xxCxx / xxxxDxxxx   |YLevel|n: xEx  ||
  |YArchetype|n: xxxxxxxxxxxBxxxxxxxxxxx                                         ||
                                       +-------------------------------------||
  ooooooooooooooooooooooooooooooooooo  | |YPrimary Traits  |CStrength|n    : xFxx  ||
  ooooooooooooooooo1ooooooooooooooooo  | ~~~~~~~~~~~~~~  |CPerception|n  : xGxx  ||
  ooooooooooooooooooooooooooooooooooo  |                 |CIntelligence|n: xHxx  ||
                                       |                 |CDexterity|n   : xIxx  ||
  |YRace|n:           xxxxxxxxxxxYxxxxxx   |                 |CCharisma|n    : xJxx  ||
  |YFocus|n:          xxxxxxxxxxxZxxxxxx   |                 |CVitality|n    : xKxx  ||
  |YDescription|n                          |                 |CMagic|n       : xLxx  ||
  ~~~~~~~~~~~                          ||-------------------------------------||
  ooooooooooooooooo2ooooooooooooooooo  | |YSave Rolls      |CFortitude|n   : xMxx  ||
  ooooooooooooooooooooooooooooooooooo  | ~~~~~~~~~~      |CReflex|n      : xNxx  ||
                                       |                 |CWill|n        : xOxx  ||
  |YEncumbrance|n                          ||-------------------------------------||
  ~~~~~~~~~~~                          | |YCombat Stats    |CMelee|n       : xPxx  ||
  |CCarry Weight|n:         xUxx / xxVxx   | ~~~~~~~~~~~~    |CRanged|n      : xQxx  ||
  |CEncumbrance Penalty|n:          xWxx   | |CPower Point     Unarmed|n     : xRxx  ||
  |CMovement Points|n:              xXxx   | |CBonus|n:  xTxx    |CDefense|n     : xSxx  ||
                                       +-------------------------------------+
"""

FORM = re.sub(r'\|$', r'', FORM, flags=re.M)
