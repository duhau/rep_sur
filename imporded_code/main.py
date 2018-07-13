#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import filedialog, messagebox
import os.path
import re
from replace import *
from rep_sur_1 import *

# get current dir
file_dir=os.getcwd()    
# get origin MCNP files' dir
origin_filename = read_filename(file_dir,'打开原始文件')
# get MCCAD_files' dir
MCCAD_filename = read_filename(file_dir,'打开MCCAD新生成的文件')
# mark
origin_start_mark=['CELL Card','SURFACE Card','Material Card']
origin_end_mark=['End of CELL Card','End of SURFACE Card','End of Material Card']
MCCAD_start_mark=['Cells Card','Surfaces Card','Materials Card']
MCCAD_end_mark=['End of Cell','End of Surface','End of Convertion']
origin_part_content=''
MCCAD_part_content=''
new_MCCAD_surface=''
new_MCCAD_cell=''

if origin_filename and MCCAD_filename:
	#replacement of surface
	origin_surs = read_surfaces(origin_filename,origin_start_mark[1],origin_start_mark[2]) # use material mark as end of surface
	MCCAD_surs = read_surfaces(MCCAD_filename,MCCAD_start_mark[1],MCCAD_start_mark[2])
	MCCAD_cells = read_cells(MCCAD_filename,MCCAD_start_mark[0],MCCAD_start_mark[1])
	#Read and replace surfaces
	if origin_surs and MCCAD_surs:
		new_surface=replace_sur(MCCAD_surs,origin_surs)
		if new_surface:
			for sur in new_surface:
				new_MCCAD_surface = ''.join([new_MCCAD_surface, sur.out_str(), '\n'])
		else:
			print('Replace repeated surfaces Fail')
	else:
		print('Read surfaces Fail')
	#Read and replace cells
	if MCCAD_cells and new_surface:
		new_cell=replace_cell(MCCAD_cells,new_surface)
		if new_cell:
			for cell in new_cell:
				new_MCCAD_cell = ''.join([new_MCCAD_cell, cell.out_str(), '\n'])
		else:
			print('Replace cells Fail')
	else:
		print('Read cells Fail')
	# Pretreatment
	origin_pre_treatment=Pretreatment(origin_filename,origin_start_mark,origin_end_mark)
	MCCAD_pre_treatment=Pretreatment(MCCAD_filename,MCCAD_start_mark,MCCAD_end_mark)
	if origin_pre_treatment and MCCAD_pre_treatment:
		# get cell, surface and material part of file separately 
		origin_part_content=get_part_file(origin_pre_treatment, origin_start_mark, origin_end_mark)
		MCCAD_part_content=get_part_file(MCCAD_pre_treatment, MCCAD_start_mark, MCCAD_end_mark)		
		#save the file after pre_treatment
		#with open("origin_pre_treatment", 'w') as fou:
			#fou.write(origin_pre_treatment)
			#fou.close()
		#with open("MCCAD_pre_treatment", 'w') as fou:
			#fou.write(MCCAD_pre_treatment)
			#fou.close()
	else:
		print('Pre_treatment Fail')
else:
	print("Open File Fail")
	
#construct new file
if origin_part_content and MCCAD_part_content:
	new_cell_file=origin_part_content[0]+new_MCCAD_cell
	new_surf_file=origin_part_content[1]+MCCAD_part_content[1]
	new_material=MCCAD_part_content[2]+origin_part_content[2]
	new_file=new_cell_file+'\n'+new_surf_file+'\n'+new_material
	with open("new_file", 'w') as fou:
		fou.write(new_file)
		fou.close()