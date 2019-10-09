import matplotlib.pyplot as plt
import constants as c
import numpy as np
import json
from pathlib import Path


class NCK:
    """
    NCK means non cursive kerning, for example between 'F' and 'a' if the design of 'F' be non cursive, in other words
    dosen't attachs to 'a'.
    """
    def __init__(self,fontforge_object,lookups):
        
        self.fontforge_object=fontforge_object
        self.lookups=lookups
    
    def generate_nck(self,all_pairs):
        # Check whether '.temp' and '.temp/png_glyphs' exists or not, if not, creating
        if Path('.temp/png_glyhs').exists() != True:
            Path('.temp/png_glyhs').mkdir()

        
        fontforge_object=self.fontforge_object
        lookups=self.lookups

        # It is worth to mention that here punctuations don't contain capitals that contain parts
        numbers_punctuations=[]
        capitals_initial,capitals_final=[],[]
        lowercases_initial,lowercases_final=[],[]


        numbers_punctuations=[fontforge_object[x].glyphname  for x in range(52)]
        numbers_punctuations.append('cent')
            
        for k,v in lookups.lookupType2s[0].SubTable[0].mapping.items():
            lowercases_initial.append(v[0])
            lowercases_final.append(v[-1])

        for k,v in lookups.lookupType2s[1].SubTable[0].mapping.items():
            lowercases_initial.append(v[0])
            lowercases_final.append(v[-1])

        for k,v in lookups.lookupType2s[2].SubTable[0].mapping.items():
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



        uniqe_initials=set()
        for x in initials:
            if (x in uniqe_initials)==False:
                uniqe_initials.add(x)

        uniqe_finals=set()
        for x in finals:
            if (x in uniqe_finals)==False:
                uniqe_finals.add(x)

        # Outlines Distance Dictionary
        o_d_dic=dict()

        # Exporting all 'PNG' images out of fontforge_object and generating outline distances

        if Path('o_d_dic.json').exists()!=True:
            with open('o_d_dic.json',mode='x') as f:

                

                for glyph in uniqe_initials|uniqe_finals:

                    if glyph[0:4]!='Guid' and (glyph in c.lowercase)!=True:
                        # Each element of row has three element, but the first of is my need
                        # I need to calculate distance from left and right of the outline of each glyph
                        # If some part of image don't includes the glyph I need set distance as the follow
                        image_path='./.temp/png_glyhs/'+glyph+'.PNG'
                        fontforge_object[glyph].export(image_path,c.em_size-1,1)
                        image_matraix=plt.imread(image_path)

                        left_distances=[100000]*c.em_size
                        right_distances=[100000]*c.em_size

                        # Each element of row has three element, but the first of is my need, indeed v[0]

                        if glyph in uniqe_finals and glyph in uniqe_initials:

                            for index,row in enumerate(image_matraix):
                                for k,v in enumerate(row[::-1]):
                                    if v[0] ==0:
                                        left_distances[index]=k+1
                                        break

                                for k,v in enumerate(row):
                                    if v[0] ==0:
                                        right_distances[index]=k+1
                                        break

                        elif glyph in uniqe_finals:

                            for index,row in enumerate(image_matraix):
                                for k,v in enumerate(row[::-1]):
                                    if v[0] ==0:
                                        left_distances[index]=k+1
                                        break
                            
                            right_distances=None

                        elif glyph in uniqe_initials:
                            for index,row in enumerate(image_matraix):

                                for k,v in enumerate(row):
                                    if v[0] ==0:
                                        right_distances[index]=k+1
                                        break

                            left_distances=None


                        o_d_dic[glyph]=[left_distances,right_distances]

                        json.dump(o_d_dic,f,sort_keys=True,indent=True)

                        print(glyph)
        




        def claculate_kerning(left_glyph,right_glyph):
            # matrix_height=c.em_size
            # left_matrix=np.array([[int(x[0]) for x in y] for y in plt.imread('./.temp/png_glyhs/'+left_glyph+'.PNG')])
            # right_matrix=np.array([[int(x[0]) for x in y] for y in plt.imread('./.temp/png_glyhs/'+right_glyph+'.PNG')])

            # left_distances=np.array([100000]*matrix_height)
            # right_distances=np.array([100000]*matrix_height)
            
            # for index in range(len(left_matrix)-1):

            #     for k,v in enumerate(left_matrix[index][::-1]):
            #         if v ==0:
            #             left_distances[index]=k+1
            #             break

            #     for k,v in enumerate(right_matrix[index]):
            #         if v ==0:
            #             right_distances[index]=k+1
            #             break
            # # ----------------------------------------------------------------------------------
            # # Section: Harmonizing Distances
            # # Harmonizing distance between two glyph, I mean minimum distance between the outline of two glyphs

            # # Destance between two glyphs
            # distance=150

        


            
            # # if left_glyph in capitals and right_glyph in capitals:
            # #     distance=300
            # if left_glyph == 'quotesingle' or left_glyph == 'quotedbl' or right_glyph == 'quotesingle' or right_glyph == 'quotedbl':
            #     distance = 80
            # # if left_glyph == 'glyph90' or right_glyph == 'glyph90':
            # #     distance=200
            # if left_glyph == 'period' or left_glyph=='glyph98' or left_glyph=='exclam' or right_glyph == 'period' or right_glyph=='glyph98' or right_glyph=='exclam':
            #     distance=60
            # if left_glyph == 'underscore' or left_glyph=='hyphen' or  right_glyph == 'underscore' or right_glyph=='hyphen':
            #     distance=70
            
            
            # # ----------------------------------------------------------------------------------
            # # Section: Virtual Outline
            # # For some glyph I need to assum a vertical line for some glyphs for example for left side of 7
            # if right_glyph == 'seven':
            #     right_distances= np.array([min(right_distances)]*matrix_height)
            # if right_glyph == 'six':
            #     right_distances= np.array([min(left_distances)]*matrix_height)
            

            # # ----------------------------------------------------------------------------------
            

            
        

            # sum_result=left_distances+right_distances
            # kerning_result=0
            # min_result=min(sum_result)
            # if min_result<100000:
            #     # It is worth to mention that height of the png imgages is equal the the number I have specified
            #     #   in 'ontforge_object[glyph].export('./.temp/png_glyhs/'+glyph+'.PNG',100,1)' plus one
            #     current_kerning=min_result*(c.em_size/101)
            #     kerning_result=(current_kerning-distance)*-1
        
            
            return  0

            

        k_m=np.zeros((len(uniqe_finals),len(uniqe_initials)))

        for final_k,final_v in enumerate(uniqe_finals) :
            for initial_k,initial_v in enumerate(uniqe_initials):
                if ((final_v,initial_v) in all_pairs) == False:
                    k_m[final_k][initial_k]=claculate_kerning(final_v,initial_v)

                

        fontforge_object.addKerningClass("'kern' *",
                            "'kern' *1", uniqe_finals, uniqe_initials,[x for x in k_m.flatten()])

        fontforge_object.save('../sources/temp.sfd')

        return fontforge_object

