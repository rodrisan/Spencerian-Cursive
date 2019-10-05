from fontTools.ttLib import TTFont
from pathlib import Path
import sys
import importlib
import numpy as np
import copy
import matplotlib.pyplot as plt
sys.path.append('/usr/local/lib/python3.7/site-packages')
# Import Fontforge
# Becasue pylint give me error due to importing, I import it programmitically
fontforge = importlib.import_module('fontforge')
# --------------------------------------------------------------------------------------------------
# The following method will apply the substituions on strings of the glyphs
def apply_substitution(l_l_g, substitutions):
    """
        l_l_g: It is list of list of glyphs

        substitutions: It is list of ['substituation_dictionaries','position to apply'],
        it is worth to mention that position to apply is posiition the list
        encomposing glyphs that the substitution will be apply on each glyph.  
    """
    #
    l_l_g=copy.deepcopy(l_l_g)
    # The follow loop will itereate over each substitution
    for substitution_dictionary,position in substitutions:
        # Retrive substitution dictionary !
                # Apply the substitution on the related position
        for base, replacement in substitution_dictionary.items():
            for glyph in l_l_g[position]:
                if base==glyph:
                    l_l_g[position][l_l_g[position].index(glyph)] =replacement

                    

        # for index, glyphs in enumerate(l_l_g):
        #     for glyph in glyphs:
        #         if glyph in substitution_dictionary:

        #             l_l_g[index][glyph] = substitution_dictionary[glyph]

    #return l_l_g.toList()
    return l_l_g


def generate_possible_string(l_l_g):
    # In order to gererate all possible strings I need a matrix with width of product of lenght of all record of
    #   l_l_g, and with height of lenght of l_l_g

    matrix_width = 1
    matrix_height = len(l_l_g)
    for glyphs in l_l_g:
        matrix_width = matrix_width*len(glyphs)

    possible_string_matrix =[[]*matrix_width]*matrix_height
    #  possible_string_matrix = np.empty((matrix_height,matrix_width),dtype='<U10')

    # Initialize above matrix
    # c_m_r is current multilypication result
    c_m_r=1
    for index, glyphs in enumerate(l_l_g):
        # the glyphs is a list of glyphs
        c_m_r=c_m_r*len(glyphs)
        # Temporary lists, it is worth to mention that because of confiusion between '1' and 'l', I think
        #   it is better to use 'one' as the follow:
        t_l_one=np.array([int(matrix_width/c_m_r)*[x] for x in glyphs]).tolist()
        t_l_2=[]
        for x in t_l_one:
            for y in x:
                t_l_2.append(y)
        if len(t_l_2)!=matrix_width:
            possible_string_matrix[index] = int(matrix_width/len(t_l_2))*t_l_2
        else:
            possible_string_matrix[index]=t_l_2

    # List of possible strins
    possible_strings = list()

    temporary_list=np.array(possible_string_matrix) 
    
    # Iterate over y
    for column in np.nditer(temporary_list, order='F', flags=['external_loop','refs_ok']):
        possible_strings.append(column)

    # Solving problem of ccmp lookup, because some elements in possible_strings list contains several glyphs
    #   I need to * the list of glyphs( or parts) that form a glyph, then connect it to *,
    #   for example, if I have a list like [x1,x2,x3,[x4,x5]], I will convert it to [x1,x2,x3,x4,x5]
    for index, p_s in enumerate(possible_strings):
        possible_string = list()
        for x in p_s:
            if type(x)==list:
                for glyph in x:
                    possible_string.append(glyph)
            else:
                possible_string.append(x)

        possible_strings[index] = possible_string


    return possible_strings


def generate_pairs(possible_sttrings):
    pairs = set()

    for p_s in possible_sttrings:
        pairs = pairs | {(p_s[x], p_s[x+1]) for x in range(len(p_s)-1)}

    return pairs

def adding_preceding_and_leading_pairs(l_l_g,a_l_l_g,substitutions):
    if max((x[1] for x in substitutions)) == len(l_l_g)-1:
        precidding_glyphs=list()
        for glyph in l_l_g[-1]:
            # l_l_g.append([v[-2] for k,v in lookup.SubTable[0].mapping.items() for lookup in lookupType2s if v[-1]==glyph])
            
            
            for lookup in lookupType2s:
                for v in lookup.SubTable[0].mapping.values():
                    if v[0]==glyph:
                        if len([x for x in precidding_glyphs if x==v[1]])==0:
                            precidding_glyphs.append(v[1])
        if len(precidding_glyphs)>0:               
            a_l_l_g.append(precidding_glyphs)

    if min((x[1] for x in substitutions)) == 0:
        precidding_glyphs=list()
        for glyph in l_l_g[0]:
            
            
            
            for lookup in lookupType2s:
                for v in lookup.SubTable[0].mapping.values():
                    if v[-1]==glyph:
                        if len([x for x in precidding_glyphs if x==v[-2]])==0:
                            precidding_glyphs.append(v[-2])
        if len(precidding_glyphs)>0:
            a_l_l_g[:0]=[precidding_glyphs]
            
                        
    return a_l_l_g

#---------------------------------------------------------------------------------------------------
# Fontforge file(.sdf file) path
sdf_file_path = '../sources/SpencerianCursive.sfd'

# creating fontforge object
fontforge_object = fontforge.open(sdf_file_path)

# Check whether '.temp' and '.temp/png_glyphs' exists or not, if not, creating
if Path('.temp/png_glyhs').exists() != True:
    Path('.temp/png_glyhs').mkdir()


# Genereate a true type font
fontforge_object.generate('./.temp/font.ttf')

# Opening the target font in the '.temp' directory
type_face = TTFont('./.temp/font.ttf')

# Retrive GSUB lookups from the GSUB table
gsub_lookups = type_face['GSUB'].table.LookupList.Lookup

# Retrive LookupTypes, including LookupType 1, LookupType 2 and LookupType 6
lookupType1s, lookupType2s, lookupType6s = [], [], []

# Initial and final parts
initials=dict()
finals=dict()

# Initial and final parts group, for example initial part of 'b' when attach to a preciding glyp is member of 'b'
#   and initial part of 'h' when attach to a preciding glyph is member of 'b' ,
initial_groups={
    'a':['a','d','g','q'],
    'b':['b','f','h','k','l'],
    'c':['c'],
    'e':['e'],
    'i':['i','j','u','t','w'],
    'm':['m','n','v','x','y','z'],
    'o':['o'],
    'p':['p','r','s']
}
# final_groups={If I need it will add it in the future}

# Pairs
all_pairs=set()

for lookup in gsub_lookups:
    if lookup.LookupType == 1:
        lookupType1s.append(lookup)
    elif lookup.LookupType == 2:
        lookupType2s.append(lookup)
    elif lookup.LookupType == 6:
        lookupType6s.append(lookup)

# Finding possible pairs between two glyphs, for example between a and b, not between parts of a or b,
# so I need to iterate over LookupType6
for lookup in lookupType6s:

    # In this project each lookup has only one subtable, as I know it is limitation that we can't
    #   have more than one subtable, for more information vist: https://fontforge.github.io/lookups.html
    sub_table = lookup.SubTable[0]

    # For LookupType6 I have used only format 2 and 3
    if sub_table.Format == 2:
        # It is worth to mention that in Fontforge LookupType6 with Format2 has two ways to editing
        #   one way in simple way and another in complex way, but I have only use the simple way,
        #   in other word I have edited the Matche Classes list, so I need only use the InputClassDef
        #   nor the BacktrackClassDef and the LookAheadClssDef

        # The class list is like the Matche Classes list in FontForge *
        classes = [[]] * (max(sub_table.InputClassDef.classDefs.values())+1)

        # Generate Classes
        for k, v in sub_table.InputClassDef.classDefs.items():
            temp_list = classes[v][:]
            temp_list.append(k)
            classes[v] = temp_list

        # Apply Classes
        for index, chain_sub_class in enumerate(sub_table.ChainSubClassSet):
            #
            if chain_sub_class != None:
                l_l_g=list()
                
                l_l_g[len(l_l_g):]=[classes[x] for x in chain_sub_class.ChainSubClassRule[0].Backtrack]
                l_l_g.append(classes[index])
                l_l_g[len(l_l_g):]=[classes[x] for x in chain_sub_class.ChainSubClassRule[0].Input]
                l_l_g[len(l_l_g):]=[classes[x] for x in chain_sub_class.ChainSubClassRule[0].LookAhead]

                substitutions=[(gsub_lookups[s_l_r.LookupListIndex].SubTable[0].mapping ,s_l_r.SequenceIndex) 
                for s_l_r in chain_sub_class.ChainSubClassRule[0].SubstLookupRecord]

                

                a_l_l_g=apply_substitution(l_l_g,substitutions)
                a_l_l_g=adding_preceding_and_leading_pairs(l_l_g,a_l_l_g,substitutions)
                possible_strings=generate_possible_string(a_l_l_g)
                all_pairs=all_pairs| generate_pairs(possible_strings)

    elif sub_table.Format == 3:
        

        l_l_g=list()

        l_l_g[len(l_l_g):]=[x.glyphs for x in sub_table.BacktrackCoverage]
        l_l_g[len(l_l_g):]=[]
        l_l_g[len(l_l_g):]=[x.glyphs for x in sub_table.InputCoverage]
        l_l_g[len(l_l_g):]=[x.glyphs for x in sub_table.LookAheadCoverage]

        substitutions=[(gsub_lookups[s_l_r.LookupListIndex].SubTable[0].mapping ,s_l_r.SequenceIndex) 
        for s_l_r in sub_table.SubstLookupRecord]

    
        a_l_l_g=apply_substitution(l_l_g,substitutions)
        a_l_l_g=adding_preceding_and_leading_pairs(l_l_g,a_l_l_g,substitutions)
        possible_strings=generate_possible_string(a_l_l_g)
        all_pairs=all_pairs| generate_pairs(possible_strings)



# Finding possible pairs between parts of a glyph, for example parts that form 'a', also finding initial and final parts
for lookup in lookupType2s:
    all_pairs=all_pairs| generate_pairs([v for k,v in lookup.SubTable[0].mapping.items()])

some_lowercases_finals=[]

for k,v in lookupType2s[1].SubTable[0].mapping.items():
    some_lowercases_finals.append(v[-1])


for k,v in lookupType2s[1].SubTable[0].mapping.items():
    right_part=v[0]
    right_base=k
    if k in initial_groups['i']:
        for left_part in some_lowercases_finals:
                all_pairs.add((left_part,right_part))



row_set = {x[0] for x in all_pairs}
cloumn_set = {x[1] for x in all_pairs}

# Convertin above sets to list to in order to support for indexing
row = [x for x in row_set]
cloumn = [x for x in cloumn_set]


kerning_matrix = np.zeros((len(row), len(cloumn)))


for pair in all_pairs:
    left_part = pair[0]
    right_part = pair[1]

    # index will start from 1 if exist a value
    row_index = row.index(left_part)
    cloumn_index = cloumn.index(right_part)

    right_part_anchor_x = 0
    left_part_anchor_x = 0

    for anchor_class_name, anchor_type, anchor_x, anchor_y in fontforge_object[left_part].anchorPoints:
        if anchor_type == 'exit':
            left_part_anchor_x = anchor_x

    for anchor_class_name, anchor_type, anchor_x, anchor_y in fontforge_object[right_part].anchorPoints:
        if anchor_type == 'entry':
            right_part_anchor_x = anchor_x

    distance = ((fontforge_object[left_part].width -
                 left_part_anchor_x)+right_part_anchor_x)*-1
    kerning_matrix[row_index][cloumn_index] = distance




distances = []
for x in kerning_matrix:
    for y in x:
        distances[len(distances):] = [y]
fontforge_object.addKerningClass("'kern' Cursive Feature",
                       "'kern' Cursive Feature", row, cloumn, distances)

# Remove the unnecessary lookup and its associate anchor points
fontforge_object.removeLookup("'curs' [a,d,g,o,q]",1)
fontforge_object.removeLookup("'curs' *",1)
#   It is worth to mention that the following lookup doesn't has anchor points
fontforge_object.removeLookup("'kern' `applying 'curs' features`")

# # Save fontforge object in the '.temp' folder
# fontforge_object.save('./.temp/temp.sfd')

# ----------------------------------------------------------------------------------------------
# Section: Side Bearings
# Changing the side bearing of glyphs
#   glyph98 is comma

for glyph in fontforge_object:

    side_bering = 0

    if glyph == 'quotesingle' or glyph == 'quotedbl':
        side_bering = 80
    elif glyph == 'glyph90':
        side_bering=900
    elif glyph == 'period' or glyph=='glyph98' or glyph=='exclam':
        side_bering=60
    elif glyph == 'underscore' or glyph=='hyphen':
        side_bering=70
    else:
        side_bering=100

    fontforge_object[glyph].left_side_bearing=side_bering
    fontforge_object[glyph].right_side_bearing=side_bering

# ----------------------------------------------------------------------------------------------

# It is worth to mention that here punctuations don't contain capitals that contain parts
numbers_punctuations=[]
capitals_initial,capitals_final=[],[]
lowercases_initial,lowercases_final=[],[]


numbers_punctuations=[fontforge_object[x].glyphname  for x in range(52)]
numbers_punctuations.append('cent')
    
for k,v in lookupType2s[0].SubTable[0].mapping.items():
    lowercases_initial.append(v[0])
    lowercases_final.append(v[-1])

for k,v in lookupType2s[1].SubTable[0].mapping.items():
    lowercases_initial.append(v[0])
    lowercases_final.append(v[-1])

for k,v in lookupType2s[2].SubTable[0].mapping.items():
    capitals_initial.append(v[0])
    capitals_final.append(v[-1])

    if k in numbers_punctuations:
        numbers_punctuations.remove(k)


initials=[]
initials.extend(numbers_punctuations)
initials.extend(capitals_initial)
initials.extend(lowercases_initial)

finals=[]
finals.extend(numbers_punctuations)
finals.extend(capitals_final)
finals.extend(lowercases_final)



uniqe_initials=[]
for x in initials:
    if (x in uniqe_initials)==False:
        uniqe_initials.append(x)

uniqe_finals=[]
for x in finals:
    if (x in uniqe_finals)==False:
        uniqe_finals.append(x)

# Exporting all 'PNG' images out of fontforge_object
for glyph in fontforge_object:
    fontforge_object[glyph].export('./.temp/png_glyhs/'+glyph+'.PNG',100,1)
 


def claculate_kerning(left_glyph,right_glyph):
    left_matrix=np.array([[int(x[0]) for x in y] for y in plt.imread('./.temp/png_glyhs/'+left_glyph+'.PNG')])
    right_matrix=np.array([[int(x[0]) for x in y] for y in plt.imread('./.temp/png_glyhs/'+right_glyph+'.PNG')])

    left_distances=np.array([100000]*len(left_matrix))
    right_distances=np.array([100000]*len(right_matrix))
    
    for index in range(len(left_matrix)-1):

        for k,v in enumerate(left_matrix[index][::-1]):
            if v ==0:
                left_distances[index]=k+1
                break

        for k,v in enumerate(right_matrix[index]):
            if v ==0:
                right_distances[index]=k+1
                break
    # ----------------------------------------------------------------------------------
    # Section: Harmonizing Distances
    # Harmonizing distance between two glyph, I mean minimum distance between the outline of two glyphs

    # Destance between two glyphs
    distance=400
    # Glyphs without distance between each other, I can find this list from Section with name "Side Bearings"
    g_w_d=['quotesingle','quotedbl','glyph90','period','glyph98','exclam','underscore','hyphen']
    
    

    if left_part in g_w_d or right_part in g_w_d:
        distance=0
    elif left_glyph in capitals_final and right_glyph in capitals_final:
        distance=500
    # ----------------------------------------------------------------------------------

    
   

    sum_result=left_distances+right_distances
    kerning_result=0
    min_result=min(sum_result)
    if min_result<100000:
        kerning_result=distance-min_result*fontforge_object[left_glyph].width/len(left_matrix[0])

    
    return  kerning_result

    

k_m=np.zeros((len(uniqe_finals),len(uniqe_initials)))

for final_k,final_v in enumerate(uniqe_finals) :
    for initial_k,initial_v in enumerate(uniqe_initials):
        if ((final_v,initial_v) in all_pairs) == False:
            k_m[final_k][initial_k]=claculate_kerning(final_v,initial_v)

        

fontforge_object.addKerningClass("'kern' *",
                       "'kern' *1", uniqe_finals, uniqe_initials,[x for x in k_m.flat])



fontforge_object.save('../sources/temp.sfd')

# In order to know more about GSUB lookup types visit: https://docs.microsoft.com/en-us/typography/opentype/spec/gsub
# The Follow tree is a list of information base on above linked referernce that I need for above codes:
#   LookupType 1(Single Substitution Subtable)
#   LookupType 2(Multiple Substitution Subtable)
#   LookupType 6(Chaining Contextual Substitution Subtable)
#       Format1(Simple Glyph Contexts)
#       Format2(Class-Base Glyph Contexts)
#       Format3(Coverage-Base Glyph Contexts)