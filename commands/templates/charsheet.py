"""
Character sheet EvForm template.
"""

import re

FORMCHAR = "x"
TABLECHAR = "o"


FORM = """
-=-=-=-=-=-=-=-=-=-=-=-=-=-={C[ {rCharacter Info {C]{n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|
                                                                             |
  {YName{n: xxxxxxxxxxxxxAxxxxxxxxxxxxxx     {YXP{n: xxCxx / xxxxDxxxx   {YLevel{n: xEx  |
  {YArchetype{n: xxxxxxxxxxxBxxxxxxxxxxx                                         |
                                       +-------------------------------------|
  ooooooooooooooooooooooooooooooooooo  | {YPrimary Traits   {CStrength{n    : xFx  |
  ooooooooooooooooo1ooooooooooooooooo  | ~~~~~~~~~~~~~~   {CPerception{n  : xGx  |
  ooooooooooooooooooooooooooooooooooo  |                  {CIntelligence{n: xHx  |
                                       |                  {CDexterity{n   : xIx  |
  {YDescription{n                          |                  {CCharisma{n    : xJx  |
  ~~~~~~~~~~~                          |                  {CVitality{n    : xKx  |
  ooooooooooooooooo2ooooooooooooooooo  |                  {CMagic{n       : xLx  |
  ooooooooooooooooooooooooooooooooooo  |-------------------------------------|
                                       | {YSave Rolls       {CFortitude{n   : xMx  |
  {YEncumbrance{n                          | ~~~~~~~~~~       {CReflex{n      : xNx  |
  ~~~~~~~~~~~                          |                  {CWill{n        : xOx  |
  {CCarry Weight{n:          xUxx / xVxx   |-------------------------------------|
  {CEncumbrance Penalty{n:          xWxx   | {YCombat Stats     {CMelee{n       : xPx  |
  {CMovement Points{n:              xXxx   | ~~~~~~~~~~~~     {CRanged{n      : xQx  |
                                       | {CPower Point      Unarmed{n     : xRx  |
                                       | {CBonus{{n:   xTx     {CDefense{n     : xSx  |
                                       +-------------------------------------|
  {YSkills{n
 ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
 ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
 ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
 oooooooooooooooooooooooooooooooooooooo3oooooooooooooooooooooooooooooooooooooo
 ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
 ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
 ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
"""

FORM = re.sub(r'\|$', r'', FORM, flags=re.M)
