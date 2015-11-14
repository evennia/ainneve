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
  oooooooooooooooooooooooooooooooooo   | {YPrimary Traits   {CStrength{n    : xFx  |
  ooooooooooooooooo1oooooooooooooooo   | ~~~~~~~~~~~~~~   {CPerception{n  : xGx  |
  oooooooooooooooooooooooooooooooooo   |                  {CIntelligence{n: xHx  |
                                       |                  {CDexterity{n   : xIx  |
  {YDescription{n                          |                  {CCharisma{n    : xJx  |
  ~~~~~~~~~~~                          |                  {CVitality{n    : xKx  |
  ooooooooooooooooo2oooooooooooooooo   |                  {CMagic{n       : xLx  |
  oooooooooooooooooooooooooooooooooo   |-------------------------------------|
                                       | {YSave Rolls       {CFortitude{n   : xMx  |
  {YEncumbrance{n                          | ~~~~~~~~~~       {CReflex{n      : xNx  |
  ~~~~~~~~~~~                          |                  {CWill{n        : xOx  |
  {CCarry Weight{n:          xUxx / xVxx   |-------------------------------------|
  {CEncumbrance Penalty{n:          xWxx   | {YCombat Stats     {CMelee{n       : xPx  |
  {CMovement Points{n:              xXxx   | ~~~~~~~~~~~~     {CRanged{n      : xQx  |
                                       | {CPower Point      Unarmed{n     : xRx  |
                                       | {CBonus{{n:   xTx     {CDefense{n     : xSx  |
                                       +-------------------------------------|
"""

FORM = re.sub(r'\|$', r'', FORM, flags=re.M)
