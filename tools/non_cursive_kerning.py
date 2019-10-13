import matplotlib.pyplot as plt
import constants as c
import numpy as np
import sqlite3
import hashlib
import json
from pathlib import Path
from time import gmtime, strftime

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


        numbers_punctuations=[fontforge_object[x].glyphname  for x in range(1,52)]
        numbers_punctuations.append('cent')
        numbers_punctuations.append('pound')
            
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


        def get_glyph_dic(glyph):
            # Outlines Distance Dictionary
            glyph_dic=dict()
            glyph_dic['counters']={'counter'+str(k):v.spiros for k,v in enumerate(fontforge_object[glyph].layers['Fore'])}
            glyph_dic['reference']=[{'glyph':get_glyph_dic(x[0]) , 'transformation':x[1]} for x in fontforge_object[glyph].references]

            return glyph_dic
        
        
        # Exporting all 'PNG' images out of fontforge_object and generating outline distances
        sqlite_conncetion=sqlite3.connect('databases/distances.db')
        sqlite_cursor=sqlite_conncetion.cursor()
        sqlite_cursor.execute('CREATE TABLE IF NOT EXISTS distances (glyph text, left_distances text,right_distances text,right_side_bearing text,digest text)')
                
        finals_and_initals=uniqe_initials|uniqe_finals

        print('the numbers of glyphs that will be processed to finding their distances is: '+str(len(finals_and_initals)))
        for counter,glyph in enumerate(finals_and_initals):

            print('Curent Glyph: '+glyph)
            print('curent Index (or Counter): '+ str(counter))
            print('Start Time: '+strftime('%H:%M:%S',gmtime()))
            

            if glyph[0:4]!='Guid' and (glyph in c.lowercase)!=True:
                        
                
                digest=hashlib.sha384(bytes(json.dumps(get_glyph_dic(glyph)),encoding='UTF-8')).hexdigest()
                glyph_name=(glyph,)
                sqlite_cursor.execute('SELECT * FROM distances WHERE glyph=?',glyph_name)
                execute_result=sqlite_cursor.fetchone()
                

                if execute_result == None or execute_result[-1]!=digest:
            
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


                        
                    parameter_list=[glyph,json.dumps(left_distances),json.dumps(right_distances),fontforge_object[glyph].right_side_bearing,digest]

                    if execute_result == None:
                        
                        sqlite_cursor.execute('INSERT INTO distances VALUES(?,?,?,?,?)',parameter_list)
                    else:
                        parameter_list.append(glyph)
                        sqlite_cursor.execute('UPDATE distances SET(glyph,left_distances,right_distances,right_side_bearing,digest)=(?,?,?,?,?) WHERE glyph=?',parameter_list)
                    sqlite_conncetion.commit()
            
                else:

                    print('In Database Already Exist The Distances and They Are Update')
                        
            print('End Time: '+strftime('%H:%M:%S',gmtime()))   
            print('______________________________________')


        def claculate_kerning(left_glyph,right_glyph):
            matrix_height=c.em_size
            
            left_glyph_name=(left_glyph,)
            sqlite_cursor.execute('SELECT * FROM distances WHERE glyph=?',left_glyph_name)
            execute_result=sqlite_cursor.fetchone()
            left_distances=np.array(json.loads(execute_result[1]))

            right_glyph_name=(right_glyph,)
            sqlite_cursor.execute('SELECT * FROM distances WHERE glyph=?',right_glyph_name)
            execute_result=sqlite_cursor.fetchone()
            right_distances=np.array(json.loads(execute_result[2]))
            

            # ----------------------------------------------------------------------------------
            # Section: Harmonizing Distances
            # Harmonizing distance between two glyph, I mean minimum distance between the outline of two glyphs

            # Destance between two glyphs
            distance=700

        


            
            # if left_glyph in capitals and right_glyph in capitals:
            #     distance=300
            if left_glyph == 'quotesingle' or left_glyph == 'quotedbl' or right_glyph == 'quotesingle' or right_glyph == 'quotedbl':
                distance = 80
            # if left_glyph == 'glyph90' or right_glyph == 'glyph90':
            #     distance=200
            if left_glyph == 'period' or left_glyph=='glyph98' or left_glyph=='exclam' or right_glyph == 'period' or right_glyph=='glyph98' or right_glyph=='exclam':
                distance=60
            if left_glyph == 'underscore' or left_glyph=='hyphen' or  right_glyph == 'underscore' or right_glyph=='hyphen':
                distance=70
            
            
            # ----------------------------------------------------------------------------------
            # Section: Virtual Outline
            # For some glyph I need to assum a vertical line for some glyphs for example for left side of 7
            if right_glyph == 'seven':
                right_distances= np.array([min(right_distances)]*matrix_height)
            if right_glyph == 'six':
                right_distances= np.array([min(left_distances)]*matrix_height)
            

            # ----------------------------------------------------------------------------------
            

            
        

            sum_result=left_distances+right_distances
            kerning_result=0
            min_result=min(sum_result)
            if min_result<100000:
                # It is worth to mention that height of the png imgages is equal the the number I have specified
                #   in 'ontforge_object[glyph].export('./.temp/png_glyhs/'+glyph+'.PNG',100,1)' plus one
                current_kerning=min_result
                kerning_result=(current_kerning)*-1+distance
            
            return  kerning_result

            

        k_m=np.zeros((len(uniqe_finals),len(uniqe_initials)))

        for final_k,final_v in enumerate(uniqe_finals) :
            for initial_k,initial_v in enumerate(uniqe_initials):
                
                if ((final_v,initial_v) in all_pairs) == False:
                    k_m[final_k][initial_k]=claculate_kerning(final_v,initial_v)


        # I can't set 'Everything Else' field, so I set one row of '0' for the first row of 'k_m' matrix
        #   and one column of '0' for the first column of 'K_M' matrix, then I added 'uni0000' class for 
        #   'uniqe_finals_list' and 'uniqe_initials_list' lists, because I  figure out this method can simulate
        #   'Everything Else', for 'Everything Else' field I mean the field in the kerning by matrix editor windows in FontForge

        k_m=np.insert(k_m,0,0,axis=0)
        k_m=np.insert(k_m,0,0,axis=1)
        uniqe_finals_list=list(uniqe_finals)
        uniqe_initials_list=list(uniqe_initials)
        uniqe_finals_list.insert(0,'uni0000')
        uniqe_initials_list.insert(0,'uni0000')
         
        fontforge_object.addKerningClass("'kern' *",
                            "'kern' *1",uniqe_finals_list, uniqe_initials_list,k_m.flatten().tolist())

        fontforge_object.save('../sources/temp.sfd')

        sqlite_conncetion.close()

        return fontforge_object

