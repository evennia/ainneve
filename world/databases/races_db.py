from world.races.race import Race

#Create the race database
race_db = {}

# --------------------------------
# Initalise all Ainneve races here
# --------------------------------
race_db['dwarf'] = Race()
race_db['elf'] = Race()
race_db['human'] = Race()

# -----------------------
# Dwarf Race Settings
# -----------------------
DWARF_FOCI = ['brawn',
              'resilience',
              'alertness',]

DWARF_FEATS = ['heat vision',
               'poison resistance',
               'dark vision',
               'improved climb',
               'fear resistance',]

DWARF_BONUSES = {'will' : 1}

race_db['dwarf'].name = "Dwarf"
race_db['dwarf'].size = "small"
race_db['dwarf'].foci = DWARF_FOCI
race_db['dwarf'].feats = DWARF_FEATS
race_db['dwarf'].bonuses = DWARF_BONUSES
race_db['dwarf'].detriments = {}

# -----------------------
# Elf Race Settings
# -----------------------
ELF_FOCI = ['agility',
            'spirit',
            'alertness',]

ELF_FEATS = ['magic resistance',
             'heat vision',
             'improved listen',
             'sprint',
             'illusion resistance',]

ELF_BONUSES = {}

race_db['elf'].name = "Elf"
race_db['elf'].size = "medium"
race_db['elf'].foci = ELF_FOCI
race_db['elf'].feats = ELF_FEATS
race_db['elf'].bonuses = ELF_BONUSES
race_db['elf'].detriments = {}

# -----------------------
# Human Race Settings
# -----------------------
HUMAN_FOCI = ['agility',
              'cunning',
              'prestige',]

HUMAN_FEATS = ['sprint',
               'improved jump',
               'improved climb',
               'improved swim',
               'fear resistance',]

HUMAN_BONUSES = {'will' : 1,
                 'languages' : 3}

race_db['human'].name = "Human"
race_db['human'].size = "medium"
race_db['human'].foci = HUMAN_FOCI
race_db['human'].feats = HUMAN_FEATS
race_db['human'].bonuses = HUMAN_BONUSES
race_db['human'].detriments = []
