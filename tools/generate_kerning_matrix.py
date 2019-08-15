import fontforge
import numpy as np

final_forms = {'a': ['a', 'd', 'h', 'i', 'k', 'l', 'm', 'n', 'p', 'r', 't', 'u', 'x'],
               'c': ['c', 'e'],
               'b': ['b', 'v', 'w'],
               'o': ['o'],
               'g': ['g', 'j', 'Z', 'Y', 'J'],
               'f': ['f', 's'],
               'q': ['q'],
               'A': ['A', 'H'],
               'L': ['L', 'Q'],
               'K': ['K', 'R', 'X'],
               'M': ['M'],
               'D': ['D']}
initial_forms = {'a': ['a', 'd', 'g', 'q'],
                 'b': ['b', 'f', 'h', 'k', 'l'],
                 'c': ['c'],
                 'e': ['e'],
                 'i': ['i', 'j', 'u', 't', 'w'],
                 'm': ['m', 'n', 'v', 'x', 'y', 'z'],
                 'o': ['o'],
                 'p': ['p', 'r', 's']}
changable_inital_forms = {'a': False,
                          'b': True,
                          'c': False,
                          'e': True,
                          'i': False,
                          'm': False,
                          'o': False,
                          'p': True}


pairs = set()
pairs_2 = set()

my_type = fontforge.open('../sources/SpencerianCursive.sfd')
my_type.selection.all()


ccmp_lookups = dict()

for glyph in my_type:

    # ----------------------part1
    ccmp_lookup_lovercase = my_type[glyph].getPosSub("'ccmp' [Lowercase]")
    ccmp_lookup_uppercase = my_type[glyph].getPosSub("'ccmp' [Uppercase]")
    ccmp_lookup_s = my_type[glyph].getPosSub("'ccmp' [s] + *")

    ccmp_lookup = tuple()

    if len(ccmp_lookup_lovercase):
        ccmp_lookup = ccmp_lookup_lovercase
    elif len(ccmp_lookup_uppercase):
        ccmp_lookup = ccmp_lookup_uppercase
    elif len(ccmp_lookup_s):
        ccmp_lookup = ccmp_lookup_s

    if len(ccmp_lookup)>0:
        # becaue it like (((x,x),(x,x)),)
        ccmp_lookup_refined = ccmp_lookup[0][2:]

        pairs = pairs | {(ccmp_lookup_refined[x],
                          ccmp_lookup_refined[x+1])
                         for x in range(len(ccmp_lookup_refined)-1)}

        ccmp_lookups[glyph] = ccmp_lookup_refined
    # .......................part2

    # if len(glyph) > 1 and glyph.find('.') or glyph.find('_'):
    #     if len(glyph) == 3 and glyph.find('_') == 1:
    #         pairs_2 = pairs_2 | {(glyph, ccmp_lookups[x][len(ccmp_lookups[glyph])-1])
    #                              for x in initial_forms[glyph[2:3]]} | {(ccmp_lookups[glyph][len(ccmp_lookups[glyph])-1], glyph)
    #                                                                     for x in final_forms[glyph[0:1]]}

        # elif glyph_name.find('_')== len(glyph_name)-1:
        # ...
        # elif glyph_name.find('__')== len(glyph_name)-1:
        # ...
        # elif glyph_name.find('.')== len(glyph_name)-1:


# -----------------------------------------------------------------------------------------------------
# The follow codes are for finding final parts with their * and * parts
for glyph in my_type:

    left_part = set()
    right_part = set()

    # Check whether pattern is "letter name + '_'" or "letter name + '_' _ letter name".
    if (len(glyph) == 2 or len(glyph) == 3 or len(glyph) == 4 or  len(glyph) == 4) and (glyph.find('_', 1) == 1 and glyph.find('__') == -1) or glyph.find('..')==1:

        # common situation
        left_part = {(ccmp_lookups[x][-2], glyph) for x in final_forms[glyph[0]] }

        # pattern like 'a_'
        # if(len(glyph) == 2):
        #     # i don't do any thing here
        #     print('no')

        # pattern like 'a_c'
        if(len(glyph) == 3):
            if(changable_inital_forms[glyph[2]]):
                right_part = {(glyph, 'null1')} | {('null1', ccmp_lookups[x][1]) for x in initial_forms[glyph[2]]}
            else:
                right_part = {(glyph, ccmp_lookups[x][0]) for x in initial_forms[glyph[2]]}

        # pattern like 'a_bi'
        elif(len(glyph) == 4):
            if(changable_inital_forms[glyph[2]]):
                right_part = {(glyph, 'null1')} | {('null1', ccmp_lookups[x][1]) for x in initial_forms[glyph[2]]}
                print(right_part)

            else:
                right_part = {(glyph, ccmp_lookups[x][0]) for x in initial_forms[glyph[2]]}

            if(changable_inital_forms[glyph[3]]):
                right_part = {(glyph, 'null1')} | {('null1', ccmp_lookups[x][1]) for x in initial_forms[glyph[3]]} | right_part
            else:
                right_part = {(glyph, ccmp_lookups[x][0]) for x in initial_forms[glyph[3]]} | right_part
        
        # patter like a_c..
        elif(len(glyph) == 5):
            if(changable_inital_forms[glyph[2]]):
                right_part = {(glyph, 'null1')} | {('null1', ccmp_lookups[x][1]) for x in initial_forms[glyph[2]]}
            else:
                right_part = {(glyph, ccmp_lookups[x][0]) for x in initial_forms[glyph[2]]}

            
    pairs = pairs | left_part | right_part


row_set = {x[0] for x in pairs}
cloumn_set = {x[1] for x in pairs}

# Convertin above sets to list to in order to support for indexing
row = [x for x in row_set]
cloumn = [x for x in cloumn_set]


kerning_matrix = np.zeros((len(row), len(cloumn)))


for pair in pairs:
    left_part = pair[0]
    right_part = pair[1]

    # index will start from 1 if exist a value
    row_index = row.index(left_part)
    cloumn_index = cloumn.index(right_part)

    right_part_anchor_x = 0
    left_part_anchor_x = 0

    for anchor_class_name, anchor_type, anchor_x, anchor_y in my_type[left_part].anchorPoints:
        if anchor_type == 'exit':
            left_part_anchor_x = anchor_x

    for anchor_class_name, anchor_type, anchor_x, anchor_y in my_type[right_part].anchorPoints:
        if anchor_type == 'entry':
            right_part_anchor_x = anchor_x

    distance = ((my_type[left_part].width -
                 left_part_anchor_x)+right_part_anchor_x)*-1
    kerning_matrix[row_index][cloumn_index] = distance
    print(left_part+'+'+right_part+': '+str(distance))


distances = []
for x in kerning_matrix:
    for y in x:
        distances[len(distances):] = [y]
my_type.addKerningClass("'kern' Cursive Feature",
                       'test', row, cloumn, distances)

my_type.save('../sources/SpencerianCursive_WithKerneringMatrix.sfd')



    
