# -*- coding: utf-8 -*-

DEBUG = False
import os
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
__author__ = 'Jin Cao'
__copyright__ = "Copyright 2017, Quantum Functional Materials Design and Application Laboratory"
__version__ = "0.1"
__maintainer__ = "Jin Cao"
__email__ = "jincao2013@outlook.com"
__date__ = "Feb 1, 2017"
	
def repair_vasprun_xml(input_file_name='vasprun.xml',
                       output_file_name='vasprun_repaired.xml',
                       ):
    if os.path.exists(output_file_name):
        os.remove(output_file_name)
    # open file
    fo = open(input_file_name,'r')
    gr = open(output_file_name,'a')
    # 
    temp_line = None
    stop = False
    while (temp_line != '' ):
        temp_line = fo.readline()
        if '<calculation>' in temp_line:
            if DEBUG == True: print('find a <calculation> tag') 
            cal_seek = fo.tell()
            temp_line = fo.readline()
            while '</calculation>' not in temp_line:
                if (temp_line == '' ):
                    gr.write('</modeling>')
                    stop = True
                    break
                else:
                    temp_line = fo.readline()
            if '</calculation>' in temp_line:
                if DEBUG == True: print('find a </calculation> tag') 
                fo.seek(cal_seek)
                gr.write(' <calculation>\n')
                continue
        else:
            gr.write(temp_line)
        if stop == True: break
    # close file
    gr.close()
    fo.close()
    return output_file_name
    
def max_force(force_matrix):
    max_force_of_one_atom = []
    for i in force_matrix:
        f1 = abs(max(i))
        f2 = abs(min(i))
        max_force_of_one_atom.append(max([f1,f2]))
    return max(max_force_of_one_atom)
    
def read_force_matrix(file_name):
    try:
        tree = ET.parse(file_name)
    except:
        if DEBUG == True: print('vasprun.xml need repair')
        file_name = repair_vasprun_xml(input_file_name='vasprun.xml',
                                       output_file_name='vasprun_repaired.xml',
                                       )
        tree = ET.parse(file_name)
    '''
    if temp_varray == None:
        if DEBUG == True: print('vasprun.xml need repair')
        file_name = repair_vasprun_xml(input_file_name='vasprun.xml',
                                       output_file_name='vasprun_repaired.xml',
                                       )
        varray = tree.findall('calculation')[-1].findall('varray')
    else:
        varray = temp_varray
    '''
    varray = tree.findall('calculation')[-1].findall('varray')
    for i in varray:
        if i.attrib['name'] == 'forces':
            force_xml = i
    
    atom_num = len(force_xml.findall('v'))
    force_matrix = []
    for i in force_xml.findall('v'):
        force_matrix.append(i.text.strip().split())

    for i in range(len(force_matrix)):
        for j in range(len(force_matrix[i])):
            force_matrix[i][j] = float(force_matrix[i][j])
            
    if DEBUG == True: print(force_matrix)
    # print ('atom_num:',atom_num)
    return {'atom_num':atom_num,
            'force_matrix':force_matrix,
            }
    
def main():
    print ('>   Scrip of Read Max Force   <')
    print ('+---------------------------------------+')
    print ('| dir_name \t\t','max_force\t|')
    print ('|---------------------------------------|')
    log = []
    listdir = os.listdir()
    for dir_name in listdir:
        if os.path.isdir(dir_name) == True:
            pwd = os.getcwd()
            os.chdir(dir_name)
            if os.path.exists('vasprun.xml') == False:
                temp_log = '# vasprun not in '+str(dir_name)
                log.append(temp_log)
                os.chdir(pwd)
                continue

            force_matrix = read_force_matrix('vasprun.xml')
            print('| ',dir_name,' \t\t',max_force(force_matrix['force_matrix']), '\t|')
            
            os.chdir(pwd)
    print ('+---------------------------------------+')
    for i in log:
        print (i)
    print('Done!')
    
'''
  main
'''
main()

