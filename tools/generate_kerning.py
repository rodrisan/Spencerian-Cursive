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
#---------------------------------------------------------------------------------------------------
# Fontforge file(.sdf file) path
sdf_file_path = './.temp/temp.sfd'

# creating fontforge object
fontforge_object = fontforge.open(sdf_file_path)

# Check whether '.temp' '.temp/png_glyhs' exists or not
if Path('.temp').exists() != True:
    Path('.temp').mkdir()
if Path('.temp/png_glyhs').exists() != True:
    Path('.temp/png_glyhs').mkdir()

# Genereate a true type font
fontforge_object.generate('./.temp/font.ttf')

# Opening the target font in the '.temp' directory
type_face = TTFont('./.temp/font.ttf')

# Retrive GSUB lookups from the GSUB table
gsub_lookups = type_face['GSUB'].table.LookupList.Lookup

# Retrive LookupTypes 2
lookupType2s= []


for lookup in gsub_lookups:
    if lookup.LookupType == 2:
        lookupType2s.append(lookup)



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
    distance_constance=400
    if left_glyph in capitals_final and right_glyph in capitals_final:
        distance_constance=500

    sum_result=left_distances+right_distances
    kerning_result=0
    min_result=min(sum_result)
    if min_result<100000:
        kerning_result=distance_constance-min_result*fontforge_object[left_glyph].width/len(left_matrix[0])

    
    return  kerning_result

    

k_m=np.zeros((len(uniqe_finals),len(uniqe_initials)))

for final_k,final_v in enumerate(uniqe_finals) :
    for initial_k,initial_v in enumerate(uniqe_initials):
        k_m[final_k][initial_k]=claculate_kerning(final_v,initial_v)

fontforge_object.addKerningClass("'kern' *",
                       "'kern' *1", uniqe_finals, uniqe_initials,[x for x in k_m.flat])



fontforge_object.save('../sources/temp.sfd')
