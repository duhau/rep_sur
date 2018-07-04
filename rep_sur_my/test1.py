#!/usr/bin/python
# -*- coding: UTF-8 -*-
#class Test():
    #def __init__(self, math, chinese, chemsity,english):
        #self.math=math
        #self.chinese=chinese
        #self.chemsity=chemsity
        #self.english=english
        
#def compare(teata,testb):

    #if teata.math < testb.math:
        #teata.math=  testb.math
        #return teata
    #else:
        #return teata 
        
#Li=[Test(60,69,72,65),Test(82,92,70,45)]
#Wang=[Test(70,89,90,70),Test(77,85,84,89)]

#for a in Li:
    #for b in Wang:
        #a=compare(a,b)   #return the last compare 
        
#print(Li[0].math)
        
        
    
##查找a中不为0的元素
#a=[12,0.1,0,15,0,0.1,2]
#b=[i for i,v in enumerate(a) if v<1e-15]
#for j in range(len(b)):
    #print(a[b[j]])


#from tkinter import filedialog, messagebox
#import os.path
#import re
#file_dir=os.getcwd()

## get origin MCNP files' dir
#origin_filename = filedialog.askopenfilename(initialdir=file_dir, filetypes = (("Origin MCNP files", "*")                                                        

                                                         #,("All files", "*.*") )) 
#a=[]
#with open(origin_filename, 'r') as fin:
    #for line in fin:
        #line = line.strip()
        #a.append(line)
    #fin.close()
#sur_str = ''.join(a)
#print(sur_str)

#writefile=file_dir+'9999.txt'            
#with open(writefile, 'w') as fin:
    #fin.write(sur_str)
    #fin.close()

import re
pattern = re.compile(r'(\d{1,5}\s+)(\d{1,5}\s+)(-?\d{1,}(\.\d{1,})?([E,e]-\d*)?)')
line="38    20  8.56E-3( 266 -9 -21 267 -15 16) : ( 267 -4 266 -184 216 185) : (267 -16 -9 266 -4 -185 5) : ( 267 266 10 -16 -5) : ( -27 267-209 266 -33 34) : ( 267 -34 -27 -16 266 -21 22) : ( 266 -34 26728 -22) IMP:N=1.000000  IMP:P=1.000000"
x=pattern.search(line)
end_pos=x.span()[1]
suf=line[end_pos:]
b=suf.split()
y=float(x.group(3))
y1="{:<6.5e}".format(y)

pattern=re.compile(r'IMP:')
line="38    20  8.56E-3( 266 -9 -21 267 -15 16) : ( 267 -4 266 -184 216 185) : (267 -16 -9 266 -4 -185 5) : ( 267 266 10 -16 -5) : ( -27 267-209 266 -33 34) : ( 267 -34 -27 -16 266 -21 22) : ( 266 -34 26728 -22) IMP:N=1.000000  IMP:P=1.000000"
x=pattern.search(line)
line[x.span()[0]:]

pattern = re.compile(r'(\d{1,5}\s+)(0\s+)')
line="38    0  ( 266 -9 -21 267 -15 16) : ( 267 -4 266 -184 216 185) : (267 -16 -9 266 -4 -185 5) : ( 267 266 10 -16 -5) : ( -27 267-209 266 -33 34) : ( 267 -34 -27 -16 266 -21 22) : ( 266 -34 26728 -22) IMP:N=1.000000  IMP:P=1.000000"
x=pattern.search(line)
end_pos=x.span()[1]
y=float(x.group(2))

