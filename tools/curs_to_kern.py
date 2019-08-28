from fontTools.ttLib import TTFont
from pathlib import Path
import sys
import importlib
sys.path.append('/usr/local/lib/python3.7/site-packages')
# import fontforge
# Becasue pylint give me error due to importing, I import it programmitically
fontforge=importlib.import_module('fontforge')
# --------------------------------------------------------------------------------------------------

# fontforge file(.sdf file) path
SDF_File_Path='../sources/SpencerianCursive.sfd'

# creating fontforge object
FontforgeObject=fontforge.open(SDF_File_Path)

# Check whether '.temp' exists or not $
if Path('.temp').exists()!=True:
    Path('.temp').mkdir()

# Genereate a true type font
FontforgeObject.generate('./.temp/font.ttf')

# Opening target font in the '.temp' directory $
TypeFace=TTFont('./.temp/font.ttf')

# retrive GSUB lookups from the GSUB table
GSUB_Lookups=TypeFace['GSUB']

# retrive LookupType 3(Multiple Lookup Substitution Subtable)





print('end of my code')


# In order to know more about GSUB lookup types visit: https://docs.microsoft.com/en-us/typography/opentype/spec/gsub
# The Follow tree is a list of information base on above linked referernce that I need for above codes:
#   LookupType 1(Single Substitution Subtable)
#   LookupType 2(Multiple Substitution Subtable)
#   LookupType 6(Chaining Contextual Substitution Subtable)
#       Format1(Simple Glyph Contexts)
#       Format2(Class-Base Glyph Contexts)
#       Format3(Coverage-Base Glyph Contexts)
