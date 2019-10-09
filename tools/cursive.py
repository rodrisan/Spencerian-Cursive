
import copy
import numpy as np
import constants as c

class Cursive:
    def __init__(self,fontforge_object,lookups):
        
        self.fontforge_object=fontforge_object
        self.lookups=lookups

    def apply_substitution(self,l_l_g, substitutions):
        """
            This method will apply the substituions on strings of the glyphs
            ---------------------------------------------------------------
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

    def generate_possible_string(self,l_l_g):
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

    def generate_pairs(self,possible_sttrings):
        pairs = set()

        for p_s in possible_sttrings:
            pairs = pairs | {(p_s[x], p_s[x+1]) for x in range(len(p_s)-1)}

        return pairs

    def adding_preceding_and_leading_pairs(self,l_l_g,a_l_l_g,substitutions):
        if max((x[1] for x in substitutions)) == len(l_l_g)-1:
            precidding_glyphs=list()
            for glyph in l_l_g[-1]:
                # l_l_g.append([v[-2] for k,v in lookup.SubTable[0].mapping.items() for lookup in lookupType2s if v[-1]==glyph])
                
                
                for lookup in self.lookups.lookupType2s:
                    for v in lookup.SubTable[0].mapping.values():
                        if v[0]==glyph:
                            if len([x for x in precidding_glyphs if x==v[1]])==0:
                                precidding_glyphs.append(v[1])
            if len(precidding_glyphs)>0:               
                a_l_l_g.append(precidding_glyphs)

        if min((x[1] for x in substitutions)) == 0:
            precidding_glyphs=list()
            for glyph in l_l_g[0]:
                
                
                
                for lookup in self.lookups.lookupType2s:
                    for v in lookup.SubTable[0].mapping.values():
                        if v[-1]==glyph:
                            if len([x for x in precidding_glyphs if x==v[-2]])==0:
                                precidding_glyphs.append(v[-2])
            if len(precidding_glyphs)>0:
                a_l_l_g[:0]=[precidding_glyphs]
                
                            
        return a_l_l_g

    def cursive_to_kerning(self):

        fontforge_object=self.fontforge_object
        lookups=self.lookups

        # Pairs
        all_pairs=set()

        # Finding possible pairs between two glyphs, for example between a and b, not between parts of a or b,
        # so I need to iterate over LookupType6
        for lookup in lookups.lookupType6s:

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

                        substitutions=[(lookups.gsub_lookups[s_l_r.LookupListIndex].SubTable[0].mapping ,s_l_r.SequenceIndex) 
                        for s_l_r in chain_sub_class.ChainSubClassRule[0].SubstLookupRecord]

                        

                        a_l_l_g=self.apply_substitution(l_l_g,substitutions)
                        a_l_l_g=self.adding_preceding_and_leading_pairs(l_l_g,a_l_l_g,substitutions)
                        possible_strings=self.generate_possible_string(a_l_l_g)
                        all_pairs=all_pairs| self.generate_pairs(possible_strings)

            elif sub_table.Format == 3:
                

                l_l_g=list()

                l_l_g[len(l_l_g):]=[x.glyphs for x in sub_table.BacktrackCoverage]
                l_l_g[len(l_l_g):]=[]
                l_l_g[len(l_l_g):]=[x.glyphs for x in sub_table.InputCoverage]
                l_l_g[len(l_l_g):]=[x.glyphs for x in sub_table.LookAheadCoverage]

                substitutions=[(lookups.gsub_lookups[s_l_r.LookupListIndex].SubTable[0].mapping ,s_l_r.SequenceIndex) 
                for s_l_r in sub_table.SubstLookupRecord]

            
                a_l_l_g=self.apply_substitution(l_l_g,substitutions)
                a_l_l_g=self.adding_preceding_and_leading_pairs(l_l_g,a_l_l_g,substitutions)
                possible_strings=self.generate_possible_string(a_l_l_g)
                all_pairs=all_pairs| self.generate_pairs(possible_strings)



        # Finding possible pairs between parts of a glyph, for example parts that form 'a', also finding initial and final parts
        for lookup in lookups.lookupType2s:
            all_pairs=all_pairs| self.generate_pairs([v for k,v in lookup.SubTable[0].mapping.items()])

        some_lowercases_finals=[]

        for k,v in lookups.lookupType2s[1].SubTable[0].mapping.items():
            some_lowercases_finals.append(v[-1])


        for k,v in lookups.lookupType2s[1].SubTable[0].mapping.items():
            right_part=v[0]
            right_base=k
            if k in c.initial_groups['i']:
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

        return [fontforge_object,all_pairs]