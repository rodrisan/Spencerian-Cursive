from pathlib import Path
import sys
import importlib
import cursive
import non_cursive_kerning
import lookups as l
sys.path.append('/usr/local/lib/python3.7/site-packages')
# ----------------------------------------
# Import Fontforge
# Becasue pylint give me error due to importing, I import it programmitically
fontforge = importlib.import_module('fontforge')
# ---------------------------------------------------------------------------------------------------------------------
# Fontforge file(.sdf file) path
sdf_file_path = '../sources/SpencerianCursive.sfd'

# creating fontforge object
fontforge_object = fontforge.open(sdf_file_path)

# Check whether '.temp' exists or not, if not, creating
if Path('.temp').exists() != True:
    Path('.temp').mkdir()

# Genereate a true type font
fontforge_object.generate('./.temp/font.ttf')

lookups=l.Lookups('./.temp/font.ttf')

cursive=cursive.Cursive(fontforge_object,lookups)
nck=non_cursive_kerning.NCK(fontforge_object,lookups)

cursive_to_kerning_result=cursive.cursive_to_kerning()
fontforge_object=cursive_to_kerning_result[0]
fontforge_object=nck.generate_nck(cursive_to_kerning_result[1])









