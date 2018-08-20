#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import filedialog, messagebox
import os.path
import re

'''
This code is writen by DuHua
The main function of the program is to used to deal with surface conflicts between MCNP input files that
generated with different decimal precision.
2018-6-24
'''

avail_types = ('p', 'px', 'py', 'pz',
               'so', 's', 'sx', 'sy', 'sz',
               'c/x', 'c/y', 'c/z', 'cx', 'cy', 'cz',
               'k/x', 'k/y', 'k/z', 'kx', 'ky', 'kz',
               'sq',
               'gq',
               'tx', 'ty', 'tz',
               'xyzp')

class Cell(object):
    '''
    '''
    def __init__(self, cell_id='0', mat_id='0', mat_density=' ',
               sur_list=[], imp_list=[1, 1],total_comment=[],part_comment=[]):
        # id is int
        self.id = cell_id
        self.mat_id = mat_id
        self.mat_density = mat_density
        self.sur_list = sur_list
        self.imp_list = imp_list
        self.total_comment=total_comment
        self.part_comment=part_comment
    
    def out_str(self):
        '''
        '''
        out_str = ''
        id_str = "{:<6}".format(str(self.id))
        mat_id_str = "{:<5}".format(self.mat_id)
        mat_density_str = ''.join([' ', self.mat_density])
        out_str = ''.join([out_str, id_str, mat_id_str,mat_density_str])
        line_breaker = 0
        for para in self.sur_list+self.imp_list:
            if len(out_str) + len(para) < 72 * (1 + line_breaker):
                out_str = ''.join([out_str, ' ', para])
            else:
                out_str = ''.join([out_str, '\n', '              ', para])
                line_breaker = line_breaker + 1
        if self.total_comment:
            out_str= self.total_comment + "\n" + out_str
        if self.part_comment:
            out_str= out_str + "\n" + self.part_comment
        return out_str
    
class Surface(object):
    '''
    class Surface
    '''

    def __init__(self, sur_id=None, sur_type=None, sur_paras=None, sur_reflect=None):
        self.id = sur_id
        self.type = sur_type
        # '' or '*'
        self.reflect = sur_reflect
        # paras are strings
        self.paras = sur_paras
        self.rep_id = None
        # rep_relation could be 'same', 'oppsite', 'oppzero'
        self.rep_relation = None

    def out_str(self):
        out_str = ''
        id_str = "{:<8}".format(self.reflect + str(self.id))
        type_str = "{:<5}".format(self.type)
        out_str = ''.join([out_str, id_str, type_str])
        line_breaker = 0
        # make para into length of 17  
        for i in range(len(self.paras)):
            self.paras[i] = "{:<17}".format(self.paras[i])
        for para in self.paras:
            if len(out_str) + len(para) < 72 * (1 + line_breaker):
                out_str = ''.join([out_str, ' ', para])
            else:
                out_str = ''.join([out_str, '\n', 
                                   '              ', para])
                line_breaker = line_breaker + 1
        return out_str
        
def get_reflect_id(para):
    '''
    return reflect flag and id
    '''
    reflect_flag = ''
    id = -1
    # if surface is reflective, reflect flag is '*', otherwise, the flag is ''
    if para[0] == '*':
        return '*', para[1:]
    else:
        return '', para

def construct_surface(paras=None):
    """
    construct surface using several lines
    """
    # paras check
    if not isinstance(paras, list):
        raise(ValueError, "paras must be a list")
    # combine these lines into one string
    sur_str = ''.join(paras)
    para_list = sur_str.split()
    reflect_flag, sur_id = get_reflect_id(para_list[0])
    sur_type = para_list[1].lower()
    sur_paras = []
    for i in range(2, len(para_list)):
        sur_paras.append(para_list[i])
    return Surface(sur_id=sur_id, sur_type=sur_type, sur_paras=sur_paras, sur_reflect=reflect_flag)
    
def is_surface(line):
    '''
    Judge whether a line is a surface start line
    '''
    paras = line.split()
    if len(paras) < 2:
        return False
    if paras[1].lower() in avail_types:
        return True
    else:
        return False

def read_surfaces(filename,suf_start_mark,suf_end_mark):
    '''
    read surfaces
    '''       
    surfaces = []
    pre_lines = []
    if filename:
        # Open origin MCNP file
        with open(filename, 'r') as f:
            sur_start = False
            start_compile=re.compile(r'(.*)%s(.*)'% suf_start_mark,re.IGNORECASE)
            end_compile=re.compile(r'(.*)%s(.*)'% suf_end_mark,re.IGNORECASE)
            for line in f:
                start_compile_mark=start_compile.search(line)
                end_compile_mark=end_compile.search(line)
                line = line.rstrip()
                # read and treat
                if start_compile_mark:        
                    sur_start = True
                    continue
                if end_compile_mark:
                    sur = construct_surface(pre_lines)
                    surfaces.append(sur)
                    break                
                if line.startswith("c") or line.startswith("C"):
                    continue
                if sur_start:
                    # read surface
                    sur_flag = is_surface(line)
                    if sur_flag:
                        # lines in previous block represent a surface
                        if pre_lines:
                            sur = construct_surface(pre_lines)
                            surfaces.append(sur)
                            pre_lines = []
                        # store this line in the buffer
                        pre_lines.append(line)
                    else:
                        # this line is a data line, store in the buffer，continue line
                        pre_lines.append(line)
        return surfaces

def change_oppzero_paras(new_paras, old_paras):
    '''
    change the parameters for oppzero condition
    keep the zero untached
    change the data precision, using the old surfaces
    '''
    changed_paras = []
    for i in range(len(new_paras)):
        if abs(float(new_paras[i])) < 1e-15:          # why -15? should be abs
            changed_paras.append(new_paras[i])
        else:
            changed_paras.append(old_paras[i])
    return changed_paras

def change_paras_sign(paras):
    '''
    change the sign of parameters
    '''
    new_paras = []
    for para in paras:
        if para[0] == '-':
            new_paras.append(para[1:])
        else:
            new_paras.append(para)
    return new_paras

def xiaoshudian(str):
    return len(str.split('.')[1])
    
        
def compare_surface(new_sur, old_sur):
    '''
    compare two surfaces
    check the type and parameters
    '''
    if new_sur.type != old_sur.type:
        return new_sur
    elif len(new_sur.paras) != len(old_sur.paras):
        return new_sur
    else:
        # compare the parameters
        same_count=0
        oppsite_count=0
        non_zero_count=0
        for i in range(len(new_sur.paras)):
            if abs(abs(float(new_sur.paras[i])) - abs(float(old_sur.paras[i]))) > 1e-6:
                return new_sur
            elif abs(float(new_sur.paras[i])) > 1e-15:
                non_zero_count+=1
                # are the all the same number
                num_point=xiaoshudian(new_sur.paras[i])
                if abs(float(new_sur.paras[i])-float(old_sur.paras[i])) < pow(10,-num_point):
                    
                #if new_sur.paras[i][0:-2] == old_sur.paras[i][0:len(new_sur.paras[i][0:-2])]:
                    same_count+=1
                # all the paras have the same absolute value, check the sign, are they oppsite?
                elif (new_sur.paras[i][0] != '-' and old_sur.paras[i][0] == '-') or  \
                   ((new_sur.paras[i][0] == '-' and old_sur.paras[i][0] != '-')):
                    oppsite_count+=1
                
        if same_count==non_zero_count:
            # use old_sur parameters to replace new_sur parameters
            new_sur.paras = old_sur.paras
            new_sur.rep_relation = 'same'
            new_sur.rep_id = old_sur.id
            return new_sur            
        if oppsite_count==non_zero_count:
            # set new id, use old parameters
            new_sur.paras = change_paras_sign(old_sur.paras) 
            new_sur.rep_relation = 'oppsite'
            new_sur.rep_id = old_sur.id
            return new_sur
        return new_sur

def find_sur_via_id(sur_id, surfaces):
    '''
    '''
    for sur in surfaces:
        if sur.id == sur_id:
            return sur
    raise ValueError('sur_id: {0} not in surfaces list'.format(sur_id))

def read_filename(file_dir,str):
    # get OLD MCNP files' dir
    filename = filedialog.askopenfilename(title=str,initialdir=file_dir, filetypes = (("OLD MCNP files", "*") \
                                                                            ,("All files", "*.*") ))  
    return filename

def replace_sur(new_surs,old_surs):
    # replacement of surface
    print("Start rep_sur")
    log_string = ''
    for new_sur in new_surs:
        for old_sur in old_surs:
            new_sur = compare_surface(new_sur, old_sur)  #replacement complent in compare function
        if new_sur.rep_id:
            #print "surface:", new_sur.id, "is ", new_sur.rep_relation, "as ", old_sur.id
            log_string = ''.join([log_string, 'surface: ', str(new_sur.id), ' is ', \
                                  new_sur.rep_relation, ' as ', str(new_sur.rep_id), '\n'])
            
    # write surface replace relationship to log file
    flog = open('out.log', 'w')
    flog.write(log_string)
    flog.close()      # should close file    
    print("Surface replace finished. Read out.log to see details.")
    return new_surs

def replace_cell(MCCAD_cells,new_surface):
    for new_suf in new_surface:
        if new_suf.rep_relation == 'same':
            for new_cell in MCCAD_cells:
                for k, suf in enumerate(new_cell.sur_list):
                    if new_suf.id in suf :
                        pos=suf.index(new_suf.id)
                        suf_list=list(suf)
                        id_list=list(new_suf.id)
                        for i in id_list:
                            suf_list.remove(i)
                        suf_list.insert(pos,new_suf.rep_id)
                        suf=''.join(suf_list)
                        new_cell.sur_list[k]=suf
                    else:
                        new_cell.sur_list[k]=suf
                    
        elif new_suf.rep_relation == 'oppsite':
            for new_cell in MCCAD_cells:
                for k, suf in enumerate(new_cell.sur_list):
                    if new_suf.id in suf :
                        pos=suf.index(new_suf.id)
                        if pos==0:   
                            suf_list=list(suf)
                            id_list=list(new_suf.id)
                            for i in id_list:
                                suf_list.remove(i)
                            suf_list.insert(pos,new_suf.rep_id)
                            suf='-' + ''.join(suf_list)
                            new_cell.sur_list[k]=suf
                        elif pos >0 :
                            if suf[pos-1]=='-':
                                suf_list=list(suf)
                                id_list=list(new_suf.id)
                                for i in id_list:
                                    suf_list.remove(i)
                                suf_list.remove('-')
                                suf_list.insert(pos,new_suf.rep_id)
                                suf=''.join(suf_list) 
                                new_cell.sur_list[k]=suf
                            else:
                                suf_list=list(suf)
                                id_list=list(new_suf.id)
                                for i in id_list:
                                    suf_list.remove(i)
                                suf_list.insert(pos,'-')
                                suf_list.insert(pos+1,new_suf.rep_id)
                                suf=''.join(suf_list)
                                new_cell.sur_list[k]=suf
                    else:
                        new_cell.sur_list[k]=suf 
    return MCCAD_cells
        
     
def read_cells(filename,cell_start_mark,cell_end_mark):
    '''
    return cells, a list of cells
    '''
    cells = []
    pre_lines = []
    part_comment=[]
    total_comment=[]
    with open(filename, 'r') as f:
        cell_start = False
        comment_start=False
        total_comment_start=False
        start_compile=re.compile(r'(.*)%s(.*)'% cell_start_mark,re.IGNORECASE)
        end_compile=re.compile(r'(.*)%s(.*)'% cell_end_mark,re.IGNORECASE)
        for line in f:
            start_compile_mark=start_compile.search(line)
            end_compile_mark=end_compile.search(line)
            line = line.rstrip()
            # read and treat
            if start_compile_mark:
                cell_start = True
                total_comment_start=True
                continue

            if end_compile_mark:
                cell = construct_cell(total_comment,part_comment,pre_lines)
                cells.append(cell)
                break            
            if line.startswith("c")  or line.startswith("C"):
                if total_comment_start:
                    total_comment.append(line)
                if comment_start:
                    part_comment.append(line)
                continue
            
            if cell_start:
                # read cell
                cell_flag = is_cell(line)
                if cell_flag:
                    comment_start = True
                    total_comment_start=False
                    # lines in previous block represent a surface
                    if pre_lines:
                        cell = construct_cell(total_comment,part_comment,pre_lines)
                        cells.append(cell)
                        # store this line in the buffer
                        total_comment = []
                        pre_lines = []
                        part_comment=[]
                    pre_lines.append(line)
                else:
                    # this line is a data line, store in the buffer
                    pre_lines.append(line)
        f.close()
    return cells

def is_cell(line):
    '''
    '''
    pattern = re.compile(r'\d{1,5}\s+\d{1,5}')
    mark=pattern.search(line)
    if line[0:5] == '     ':
        return False
    if mark:
        return True
    else:
        return False
    #if is_surface(line):
        #return False
    #if len(line) < 5:
        #return False
    #if line[0:5] == '     ':
        #return False
    #else:
        #return True

def construct_cell(total_comment=[],part_comment=[],paras=None):
    """
    construct cell using several lines
    """
    # paras check
    # if not isinstance(total_comment, list):
    #     raise (ValueError, "total_comment must be a list")
    # if not isinstance(part_comment, list):
    #     raise (ValueError, "part_comment must be a list")
    if not isinstance(paras, list):
        raise(ValueError, "paras must be a list")
    # combine these lines into one string
    if total_comment:
        total_comment='\n'.join(total_comment)
    if part_comment:
        part_comment='\n'.join(part_comment)
    cell_str = ''.join(paras)
    para_list = cell_str.split()
    cell_id = int(para_list[0])
    mat_id = para_list[1]
    
    if mat_id != '0':
        pattern = re.compile(r'(\d{1,5}\s+)(\d{1,5}\s+)(-?\d{1,}(\.\d{1,})?([E,e]-?\d+)?)')
        cell_serch_mark=pattern.search(cell_str)
        suf_start_pos=cell_serch_mark.span()[1]
        
        pattern_imp=re.compile(r'IMP:',re.IGNORECASE)
        cell_serch_mark_imp=pattern_imp.search(cell_str)
        suf_end_pos=cell_serch_mark_imp.span()[0]
        
        mat_density = "{:<9.9f}".format(float(cell_serch_mark.group(3)))
        sur_list = cell_str[suf_start_pos:suf_end_pos].split()
        imp_list = cell_str[suf_end_pos:].split()
    else:
        mat_density = ' '
        pattern = re.compile(r'(\d{1,5}\s+)(0\s+)')
        cell_serch_mark=pattern.search(cell_str)
        suf_start_pos=cell_serch_mark.span()[1]
        
        pattern_imp=re.compile(r'IMP:',re.IGNORECASE)
        cell_serch_mark_imp=pattern_imp.search(cell_str)
        suf_end_pos=cell_serch_mark_imp.span()[0]
        
        sur_list = cell_str[suf_start_pos:suf_end_pos].split()
        imp_list = cell_str[suf_end_pos:].split()        
    return Cell(cell_id=cell_id, mat_id=mat_id, mat_density=mat_density, sur_list=sur_list, imp_list=imp_list,
                total_comment=total_comment,part_comment=part_comment)


if __name__ == '__main__':
    origin_start_mark=['CELL Card','SURFACE Card','Material Card']
    origin_end_mark=['End of CELL Card','End of SURFACE Card','End of Material Card']
    MCCAD_start_mark=['Cells Card','Surfaces Card','Materials Card']
    MCCAD_end_mark=['End of Cell','End of Surface','End of Convertion']
    
    file_dir=os.getcwd() 
    # get origin MCNP files' dir
    NEW_filename = read_filename(file_dir,'Open MCCAD file')
    # get MCCAD_files' dir
    OLD_filename = read_filename(file_dir,'Open origin file')    
    old_surs = read_surfaces(NEW_filename,origin_start_mark[1],origin_start_mark[2])
    new_surs = read_surfaces(OLD_filename,MCCAD_start_mark[1],MCCAD_start_mark[2])    
    new_surface=replace_sur(new_surs,old_surs)
    
    # write new surface file  
    with open("output", 'w') as fou:
        fou.write(new_surface)
        fou.close()
    
    

