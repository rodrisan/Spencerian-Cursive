from fontTools.ttLib import TTFont
from pathlib import Path
import sys
import importlib
import numpy as np
sys.path.append('/usr/local/lib/python3.7/site-packages')
# Import Fontforge
# Becasue pylint give me error due to importing, I import it programmitically
fontforge = importlib.import_module('fontforge')
# --------------------------------------------------------------------------------------------------

# Fontforge file(.sdf file) path
sdf_file_path = '../sources/SpencerianCursive.sfd'

# creating fontforge object
fontforge_object = fontforge.open(sdf_file_path)

# Check whether '.temp' exists or not
if Path('.temp').exists() != True:
    Path('.temp').mkdir()

# Genereate a true type font
fontforgeObject.generate('./.temp/font.ttf')

# Opening the target font in the '.temp' directory
type_face = TTFont('./.temp/font.ttf')

# Retrive GSUB lookups from the GSUB table
gsub_lookups = type_face['GSUB'].table.LookupList.Lookup

# Retrive LookupTypes, including LookupType 1, LookupType 2 and LookupType 6
lookupType1s, lookupType2s, lookupType6s = [], [], []

for lookup in gsub_lookups:
    if lookup.LookupType == 1:
        lookupType1s.append(Lookup)
    elif lookup.LookupType == 2:
        lookupType2s.append(Lookup)
    elif lookup.LookupType == 6:
        lookupType6s.append(Lookup)

# Finding possible pairs between two glyphs for example between a and b, not between parts of a or b,
# so I need to iterate over LookupType6
for lookup in lookupType6s:

    # In this project each lookup has only one subtable, as I know it is limitation that we can't
    #   have more than one subtable, for more information vist: https://fontforge.github.io/lookups.html
    sub_table = Lookup.SubTable[0]

    # For LookupType6 I have used only format 2 and 3
    if sub_table.Format == 2:
        # It is worth to mention that in Fontforge LookupType6 with Format2 has two ways to editing
        #   one way in simple way and another in complex way, but I have only use the simple way,
        #   in other word I have edited the Matche Classes list, so I need only use the InputClassDef
        #   nor the BacktrackClassDef and the LookAheadClssDef

        # The class list is like the Matche Classes list in FontForge *
        classes = [[]] * max(sub_table.InputClassDef.classDefs.values())

        # Generate Classes
        for v, k in sub_table.InputClassDef.classDefs.items():
            temp_list = Classes[k-1][:]
            temp_list.append(v)
            classes[k-1] = temp_list

        # Apply Classes
        for chain_sub_class in sub_table.ChainSubClassSet:
            #
            if chain_sub_class != None:
                #
                for subst_lookup_record in chain_sub_class.ChainSubClassRule[0].SubstLookupRecord:
                    print('ok')
                    # Index of current ChainSubClass in SubTable.ChainSubClassSet, currenct index is index of
                    #   the class mines one that I need appy substituation of it
                    ChainSubClassIndex = ""
                    #

    elif SubTable.Format == 3:
        print('format3')


# The following method will apply the substituions on strings of the glyphs
def apply_substitution(l_l_g, substitutions):
    """
        l_l_g: It is list of list of glyphs, it is worth to mention that l_l_g
        must be a numpy matrix.

        substitutions: It is list of ['substituation_index','position to apply'],
        it is worth to mention that position to apply is posiition the list
        encomposing glyphs that the substitution will be apply on each glyph.  
    """

    # The follow loop will itereate over each substitution
    for substitution in substitutions:
        # Retrive substitution dictionary !
        substitution_dictionary = substitution
        # Apply the substitution on the related position
        for index, glyphs in enumerate(l_l_g):
            for glyph in glyphs:
                if glyph in substitution_dictionary:

                    l_l_g[index][glyph] = substitution_dictionary[glyph]

    return l_l_g


def generate_possible_string(l_l_g):
    # In order to gererate all possible strings I need a matrix with width of product of lenght of all record of
    #   l_l_g, and with height of lenght of l_l_g

    matrix_width = 1
    matrix_height = len(l_l_g)
    for glyphs in l_l_g:
        matrix_width = matrix_width*len(glyphs)

    possible_string_matrix = np.zeros((matrix_width, matrix_height))

    # Initialize above matrix
    for index, glyphs in enumerate(l_l_g):
        # the glyphs is a list of glyphs
        possible_string_matrix[index] = matrix_width/len(glyphs)*glyphs

    # List of possible strins
    possible_strings = list()

    # Iterate over y
    for column in np.nditer(possible_string_matrix, order='F', flags=['external_loop']):
        possible_strings.append(column)

    # Solving problem of ccmp lookup, because some elements in possible_strings list contains several glyphs
    #   I need to * the list of glyphs( or parts) that form a glyph, then connect it to *,
    #   for example, if I have a list like [x1,x2,x3,[x4,x5]], I will convert it to [x1,x2,x3,x4,x5]
    for index, p_s in enumerate(possible_strings):
        possible_string = np.array(p_s)
        possible_strings[index] = [x for x in possible_string.flat]

    return possible_strings


def generate_pairs(possible_sttrings):
    pairs = set()

    for p_s in possible_sttrings:
        pairs = pairs | {(p_s[x], p_s[x+1]) for x in range(len(p_s)-1)}

    return pairs



# In order to know more about GSUB lookup types visit: https://docs.microsoft.com/en-us/typography/opentype/spec/gsub
# The Follow tree is a list of information base on above linked referernce that I need for above codes:
#   LookupType 1(Single Substitution Subtable)
#   LookupType 2(Multiple Substitution Subtable)
#   LookupType 6(Chaining Contextual Substitution Subtable)
#       Format1(Simple Glyph Contexts)
#       Format2(Class-Base Glyph Contexts)
#       Format3(Coverage-Base Glyph Contexts)
