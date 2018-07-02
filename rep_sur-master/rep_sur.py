#!/usr/bin python
# -*- coding: utf-8 -*-

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
               sur_list=[], imp_list=[1, 1]):
        # id is int
        self.id = cell_id
        self.mat_id = mat_id
        self.mat_density = mat_density
        self.sur_list = sur_list
        self.imp_list = imp_list
    
    def out_str(self):
        '''
        '''
        id_str = "{:<6}".format(str(self.id))
        mat_id_str = "{:<5}".format(self.mat_id)
        mat_density_str = ''.join([' ', self.mat_density])
        sur_str = ''.join([' (', ' '.join(self.sur_list), ') '])
        break_tag = False
        if len(id_str) + len(mat_id_str) + len(mat_density_str) + len(sur_str) > 79:
            break_tag = True
            sur_str = ''.join(['\n      ', sur_str])
        imp_str = ' imp:n={0} imp:p={1}'.format(self.imp_list[0], self.imp_list[1])
        if len(id_str) + len(mat_id_str) + len(mat_density_str) + len(sur_str) + len(imp_str)> 79:
            if break_tag:
                if len(sur_str) + len(imp_str)> 79:
                    imp_str = ''.join(['\n      ', imp_str])
                else:
                    pass
            else:
                imp_str = ''.join(['\n      ', imp_str])
        out_str = ''.join([id_str, mat_id_str, mat_density_str, sur_str, imp_str])
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
        # make para into length of 17  疑问
        for i in range(len(self.paras)):
            self.paras[i] = "{:<17}".format(self.paras[i])
        for para in self.paras:
            if len(out_str) + len(para) < 79 * (1 + line_breaker):
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
        return '*', int(para[1:])
    else:
        return '', int(para)


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

def read_surfaces(filename):
    '''
    read surfaces
    '''
    surfaces = []
    pre_lines = []
    with open(filename, 'r') as f:
        sur_start = False
        for line in f:
            line = line.rstrip()
            # read and treat
            if "SURFACE CARD START" in line:        
                sur_start = True
                continue
            if "c " in line or "C " in line:
                continue
            if "SURFACE CARD END" in line:
                sur = construct_surface(pre_lines)
                surfaces.append(sur)
                break
            if sur_start:
                # read surface
                sur_flag = is_surface(line)
                if sur_flag:
                    # lines in previous block represent a surface
                    if pre_lines:
                        sur = construct_surface(pre_lines)
                        surfaces.append(sur)
                    # store this line in the buffer
                    pre_lines = []
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

 
def compare_surface(new_sur, old_sur):
    '''
    compare two surfaces
    check the type and parameters
    '''
    if new_sur.type != old_sur.type:
        return new_sur
    elif len(new_sur.paras) != len(old_sur.paras):
        return new_sur
    #elif new_sur.reflect != old_sur.reflect:   #bug
        #return new_sur                          
    else:
        # compare the parameters
        for i in range(len(new_sur.paras)):
            if abs(abs(float(new_sur.paras[i])) - abs(float(old_sur.paras[i]))) > 1e-6:
                return new_sur
        # all the paras have the same absolute value, check the sign
        # are the all the same number?
        same_flag = True
        for i in range(len(new_sur.paras)):
            if abs(float(new_sur.paras[i])) > 1e-15:  # why -15?
                if new_sur.paras[i][0:-2] != old_sur.paras[i][0:len(new_sur.paras[i][0:-2])]: # why 0:-2?
                    same_flag = False
                    break
        
        if same_flag:
            # use old_sur parameters to replace new_sur parameters
            new_sur.paras = old_sur.paras
            new_sur.rep_relation = 'same'
            new_sur.rep_id = old_sur.id
            return new_sur
        # are they oppsite?
        oppsite_flag = True
        # Judge the sign
        for i in range(len(new_sur.paras)):
            if abs(float(new_sur.paras[i])) > 1e-15:
                if new_sur.paras[i][0] != '-' and old_sur.paras[i][0] != '-':
                    oppsite_flag = False
                    break
                elif new_sur.paras[i][0] == '-' and old_sur.paras[i][0] == '-':
                    oppsite_flag = False
                    break
        if oppsite_flag:
            # set new id, use old parameters
            new_sur.paras = change_paras_sign(old_sur.paras) 
            new_sur.rep_relation = 'oppsite'
            new_sur.rep_id = old_sur.id
            return new_sur
        # are they oppzero
        oppzero_flag = False
        # there must be a parameter equals to zero
        zero_flag = False
        for i in range(len(new_sur.paras)):
            if abs(float(new_sur.paras[i])) < 1e-15:
                zero_flag = True
        if zero_flag:
            # all the parameter not equal to zero must be the same
            for i in range(len(new_sur.paras)):
                if abs(float(new_sur.paras[i])) > 1e-15:
                    if new_sur.paras[i][0:-2] != old_sur.paras[i][0:len(new_sur.paras[i][0:-2])]:
                        oppzero_flag = False
                        break
            # chose non_zero position
            non_zero_pos=[pos for pos,suf_par in enumerate(new_sur.paras) if abs(float(suf_par))>1e-15]
            count=0
            if non_zero_pos:
                for i in range(len(non_zero_pos)):
                    if new_sur.paras[non_zero_pos[i]][0:-2] == old_sur.paras[non_zero_pos[i]][0:len(new_sur.paras[non_zero_pos[i]][0:-2])]:
                        count =count+1
                    else:
                        pass
                if count == len(non_zero_pos):
                    oppzero_flag = True                    
            #for i in range(len(new_sur.paras)):
                #if abs(float(new_sur.paras[i])) < 1e-15:
                    ##  one of the parameter equals to zero must have oppsize sign
                    #if new_sur.paras[i][0] == '-' and old_sur.paras[i][0] != '-':
                        #oppzero_flag = True
                        #break
                    #elif new_sur.paras[i][0] != '-' and old_sur.paras[i][0] == '-':
                        #oppzero_flag = True
                        #break
        if oppzero_flag:
            # use old_sur parameters to replace new_sur parameters
            new_sur.paras = change_oppzero_paras(new_sur.paras, old_sur.paras)
            new_sur.rep_relation = 'oppzero'
            new_sur.rep_id = old_sur.id
            return new_sur
        #print "check the parameters of the new surface: {0}, and the old surface: {1}".format(new_sur.id, old_sur.id)
        return new_sur
                
def read_cells(filename):
    '''
    return cells, a list of cells
    '''
    cells = []
    pre_lines = []
    with open(filename, 'r') as f:
        cell_start = False
        for line in f:
            line = line.rstrip()
            # read and treat
            if "CELL START" in line:
                cell_start = True
                continue
            if "c " in line or "C " in line:
                continue
            if "CELL END" in line:
                cell = construct_cell(pre_lines)
                cells.append(cell)
                break
            if cell_start:
                # read surface
                cell_flag = is_cell(line)
                if cell_flag:
                    # lines in previous block represent a surface
                    if pre_lines:
                        cell = construct_cell(pre_lines)
                        cells.append(cell)
                    # store this line in the buffer
                    pre_lines = []
                    pre_lines.append(line)
                else:
                    # this line is a data line, store in the buffer
                    pre_lines.append(line)
    return cells

def is_cell(line):
    '''
    '''
    if is_surface(line):
        return False
    if len(line) < 5:
        return False
    if line[0:5] == '     ':
        return False
    else:
        return True

def is_data(line):
    '''
    '''
    if len(line) < 5:
        return False
    if line[0:5] == '     ':
        return True
    else:
        return False


def construct_cell(paras=None):
    """
    construct cell using several lines
    """
    # paras check
    if not isinstance(paras, list):
        raise(ValueError, "paras must be a list")
    # combine these lines into one string
    cell_str = ''.join(paras)
    # for some case, there are '(' and ')', replace them with white space
    cell_str = cell_str.replace(')', ' ')
    cell_str = cell_str.replace('(', ' ')
    cell_str = cell_str.replace(':', ' ')
    cell_str = cell_str.replace('=', ' ')
    para_list = cell_str.split()
    cell_id = int(para_list[0])
    mat_id = para_list[1]
    if mat_id != '0':
        mat_density = para_list[2]
        sur_list = para_list[3:-6]
        imp_list = [para_list[-4], para_list[-1]]
    else:
        mat_density = ' '
        sur_list = para_list[2:-6]
        imp_list = [para_list[-4], para_list[-1]]
    return Cell(cell_id=cell_id, mat_id=mat_id, mat_density=mat_density, sur_list=sur_list, imp_list=imp_list)

def extract_cell_sur_info(cell_sur):
    '''
    '''
    if cell_sur[0] == '-':
        return '-', int(cell_sur[1:])
    else:
        return '', int(cell_sur)

def find_sur_via_id(sur_id, surfaces):
    '''
    '''
    for sur in surfaces:
        if sur.id == sur_id:
            return sur
    raise ValueError('sur_id: {0} not in surfaces list'.format(sur_id))

def find_cell_via_id(cell_id, cells):
    '''
    '''
    for cell in cells:
        if cell.id == cell_id:
            return cell
    raise ValueError('cell_id: {0} not in cells list'.format(cell_id))


if __name__ == "__main__":
    print("Start rep_sur")
    old_sur_file = "BLK_box"
    new_sur_file = "NEW"
    old_surs = read_surfaces(old_sur_file)
    new_surs = read_surfaces(new_sur_file)
    log_string = ''
    for new_sur in new_surs:
        for old_sur in old_surs:
            new_sur = compare_surface(new_sur, old_sur)
            if new_sur.rep_id:
                #print "surface:", new_sur.id, "is ", new_sur.rep_relation, "as ", old_sur.id
                log_string = ''.join([log_string, 'surface: ', str(new_sur.id), ' is ', new_sur.rep_relation, ' as ', str(new_sur.rep_id), '\n'])
                break
    # write surface replace relationship to log file
    flog = open('out.log', 'w')
    flog.write(log_string)
    flog.close()      # should close file
    #out_string = ''
    #for new_sur in new_surs:
    #    out_string = ''.join([out_string, new_sur.out_str()])
    
    # read cells
    cells = read_cells(new_sur_file)
    out_str = ''
    # read and rewrite new file
    with open(new_sur_file, 'r') as fin:
        for line in fin:
            line = line.rstrip()
            if 'CELL START' in line or 'CELL END' in line:
                # don't write this in output
                pass
            elif 'SURFACE CARD START' in line or 'SURFACE CARD END' in line:
                # don't write this in output
                pass
            elif len(line) < 6: # comment line or blank line
                out_str = ''.join([out_str, line, '\n'])
            elif 'C ' in line or 'c ' in line: # comment line
                out_str = ''.join([out_str, line, '\n'])
            elif is_cell(line):
                para_list = line.split()
                cell_id = int(para_list[0])
                cell = find_cell_via_id(cell_id, cells)
                out_str = ''.join([out_str, cell.out_str(), '\n'])
            elif is_surface(line):
                para_list = line.split()
                sur_id = int(para_list[0])
                sur = find_sur_via_id(sur_id, new_surs)
                out_str = ''.join([out_str, sur.out_str(), '\n'])
            elif is_data(line):
                # omit data
                pass
    # write
    with open("output", 'w') as fou:
        fou.write(out_str)
    # 
    print("Surface replace finished. Read out.log to see details.")



