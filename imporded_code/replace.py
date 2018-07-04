#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import filedialog, messagebox
import os.path
import re
from rep_sur_1 import *

'''
This code is writen by DuHua
The main function of the program is to  
2018-6-28
'''
def get_part_file(pre_treatment_file, start_mark, end_mark):   
    # pre_treatment_file is MCADfiles
    # start_mark is start mark in origin MCCAD files
    # end_mark is end mark in origin MCCAD files
    if pre_treatment_file:
        file_content=[]
        for i in range(len(start_mark)):
            start_compile=re.compile(r'(.*)%s(.*)'% start_mark[i])  
            start_compile_mark=start_compile.search(pre_treatment_file)
            end_compile=re.compile(r'(.*)%s(.*)'% end_mark[i])
            end_compile_mark=end_compile.search(pre_treatment_file)
            if start_compile_mark and end_compile_mark:
                start_pos=pre_treatment_file.find(start_compile_mark.group(0))
                end_pos=pre_treatment_file.find(end_compile_mark.group(0))    
                #print(origin_start_pos,start_pos,end_pos)
                if start_pos != -1 and end_pos!=-1 :
                    pat_content=pre_treatment_file[start_pos:end_pos]
                    #print(pre_treatment_file[start_pos:end_pos])
                    file_content.append(pat_content)              
                else:
                    print('get_part_file fail match')  
            else:
                print('get_part_file fail match') 
        return file_content

def Pretreatment(filename,start_mark,end_mark):
    if filename:
        with open(filename, 'r') as fp:
            content=fp.read()
            # Modify MCCAD files to be recongnized
            cell_end_compile=re.compile(r'(.*)%s(.*)' % start_mark[1])
            cell_serch_mark=cell_end_compile.search(content)
            surf_end_compile=re.compile(r'(.*)%s(.*)' % start_mark[2])
            surf_serch_mark=surf_end_compile.search(content)
                
            if surf_serch_mark and cell_serch_mark:
                cell_end_pos=content.find(cell_serch_mark.group(0)) 
                surf_end_pos=content.find(surf_serch_mark.group(0)) 
                content=content[:cell_end_pos-1] + 'c --------  %s --------'% end_mark[0] + \
                    '\n' + content[cell_end_pos-1:surf_end_pos-1]+ \
                    'c --------  %s --------'% end_mark[1] + '\n'+ content[surf_end_pos-1:]+ \
                    '\n' + 'c --------  %s --------'% end_mark[2] 
            else:
                print("Pretreatment fail match")
            fp.close() 
                
            return content

if __name__ == '__main__':
    
    MCCAD_start_mark=['Cells Card','Surfaces Card','Materials Card']
    MCCAD_end_mark=['End of Cell','End of Surface','End of Convertion'] 
    
    # get current dir
    file_dir=os.getcwd()    
    # get MCCAD_files' dir
    MCCAD_filename = read_filename(file_dir,'Open MCCAD file')
    if  MCCAD_filename:
        # Pretreatment MCCAD_file   
        MCCAD_pre_treatment=Pretreatment(MCCAD_filename,MCCAD_start_mark,MCCAD_end_mark)
        content=get_part_file(MCCAD_pre_treatment, MCCAD_start_mark, MCCAD_end_mark)
    
        with open('1','w') as origin_fp:
            origin_fp.write(content[0])
            origin_fp.close () 
            
    else:
        messagebox.showerror('Error','OPen File Fail')        
    