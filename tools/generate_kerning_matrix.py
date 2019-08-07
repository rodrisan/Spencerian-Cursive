import fontforge
import numpy as np

final_forms = {'a': ['a', 'd', 'h', 'i', 'k', 'l', 'm', 'n', 'p', 'r', 't', 'u', 'x'],
               'c': ['c', 'e'],
               'b': ['b', 'v', 'w']}
pairs = set()

my_type = fontforge.open('../sources/SpencerianCursive.sfd')
my_type.selection.all()

for glyph in my_type:

    ccmp_lookup_lovercase = my_type[glyph].getPosSub("'ccmp' [Lowercase]")
    ccmp_lookup_uppercase = my_type[glyph].getPosSub("'ccmp' [Uppercase]")
    ccmp_lookup_s = my_type[glyph].getPosSub("'ccmp' [s] + *")

    ccmp_lookup = tuple()

    if len(ccmp_lookup_lovercase):
            ccmp_lookup = ccmp_lookup_lovercase
    elif len(ccmp_lookup_uppercase):
            ccmp_lookup = ccmp_lookup_uppercase
    elif len(ccmp_lookup_s):
            ccmp_lookup=ccmp_lookup_s

    if len(ccmp_lookup):
        # becaue it like (((x,x),(x,x)),)
        ccmp_lookup_refined=ccmp_lookup[0][2:]
        pairs=pairs | {(ccmp_lookup_refined[x], ccmp_lookup_refined[x+1])
                         for x in range(len(ccmp_lookup_refined)-1)}

row_set={x[0] for x in pairs}
cloumn_set={x[1] for x in pairs}

#Convertin above sets to list to in order to support for indexing
row=[x for x in row_set]
cloumn=[x for x in cloumn_set]


kerning_matrix=np.zeros((len(row),len(cloumn)))


for pair in pairs:
        left_part=pair[0]
        right_part=pair[1]
        
        #index will start from 1 if exist a value
        row_index=row.index(left_part)
        cloumn_index=cloumn.index(right_part)
        

        right_part_anchor_x=0
        left_part_anchor_x=0
        
        for anchor_class_name,anchor_type,anchor_x,anchor_y in my_type[left_part].anchorPoints:
                if anchor_type == 'exit':
                        left_part_anchor_x=anchor_x

        for anchor_class_name,anchor_type,anchor_x,anchor_y in my_type[right_part].anchorPoints:
                if anchor_type == 'entry':
                        right_part_anchor_x=anchor_x

        distance=((my_type[left_part].width-left_part_anchor_x)+right_part_anchor_x)*-1
        kerning_matrix[row_index][cloumn_index]=distance


distances=[]
for x in kerning_matrix:
        for y in x:
                distances[len(distances):]=[y]
my_type.addKerningClass("'kern' cursive feature",'test',row,cloumn,distances)

#print(distances)

my_type.save('../sources/SpencerianCursive_WithKerneringMatrix.sfd')

