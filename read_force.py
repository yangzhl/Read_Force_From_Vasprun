# -*- coding: utf-8 -*-

DEBUG = False
import os
import time

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
__author__ = 'Jin Cao'
__copyright__ = "Copyright 2017, Quantum Functional Materials Design and Application Laboratory"
__version__ = "0.2"
__maintainer__ = "Jin Cao"
__email__ = "jincao2013@outlook.com"
__date__ = "Feb 28, 2017"
	
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
    '''
        force_matrix_full = {}
    '''
    try:
        tree = ET.parse(file_name)
    except:
        if DEBUG == True: print('vasprun.xml need repair')
        file_name = repair_vasprun_xml(input_file_name='vasprun.xml',
                                       output_file_name='vasprun_repaired.xml',
                                       )
        tree = ET.parse(file_name)

    calculation_xml = tree.findall('calculation')
    
    force_matrix_full = {}
    for i in range(len(calculation_xml)):
        force_xml = calculation_xml[i].findall('varray')[0]
        force_matrix = []
        for force_v in force_xml.findall('v'):
            force_matrix.append(force_v.text.strip().split())
    
        force_matrix = [ [float(j) for j in i] for i in force_matrix ]
        force_matrix_full[str(i+1)] = force_matrix

    return force_matrix_full
    
def force_detail(force_matrix_full):
    force_detail = {}
    for i in range(len(force_matrix_full)):
        force_detail[str(i+1)] = {}
        force_matrix = force_matrix_full[str(i+1)]
        force_detail[str(i+1)]['max_force'] = max_force(force_matrix)
    return force_detail

def main():
    summary = []
    try:
        os.remove("force.out")
    except FileNotFoundError:
        if DEBUG == True: print ("No such file or directory: 'force.out'")
        
    with open("force.out","w") as output:
        output.writelines('read force program running at ')
        output.writelines(time.asctime( time.localtime(time.time()) ))
        output.writelines("\n \n")
        
    for dir_name in os.listdir():
        if os.path.isdir(dir_name) == True:
            os.chdir(dir_name)
            if os.path.exists('vasprun.xml') == False:
                print ('# vasprun not in '+str(dir_name))
                os.chdir('..')
                continue
            else:
                force_matrix_full = read_force_matrix('vasprun.xml')
                os.chdir('..')
                
            force_detail_dir = force_detail(force_matrix_full)
            # summary
            last_max_force = force_detail_dir[str(len(force_detail_dir)-1)]['max_force']
            max_iter_num = len(force_detail_dir)
            
            min_force_of_all = force_detail_dir['1']['max_force']
            iter_num_of_min_force_of_all = 1
            for key in force_detail_dir:
                if float(force_detail_dir[key]['max_force']) < float(min_force_of_all):
                    min_force_of_all = float(force_detail_dir[key]['max_force'])
                    iter_num_of_min_force_of_all = key
                    
            summary.append({'work_dir':dir_name,
                            'last_max_force':last_max_force,
                            'max_iter_num':max_iter_num,
                            'min_force_of_all':min_force_of_all,
                            'iter_num_of_min_force_of_all':iter_num_of_min_force_of_all,
                            })
            # write detail
            with open("force.out","a") as output:
                output.writelines("************************  work_dir: ")
                output.writelines(dir_name)
                output.writelines("  ************************")
                output.writelines("\n")
                output.writelines("------------------------\n")
                output.writelines("iter_num \tmax_force \n")
                output.writelines("------------------------\n")
                for i in range(len(force_detail_dir)):
                    output.writelines(str(i)); output.writelines("\t\t\t")
                    output.writelines(str(force_detail_dir[str(i+1)]['max_force']))
                    output.writelines("\n")
                output.writelines("------------------------\n\n")

            
    # write summary
    with open("force.out","a") as output:
        output.writelines("************************  Summary  ************************")
        output.writelines("\n")
        output.writelines("----------------------------------------------------------\n")
        output.writelines("Work_dir \t\t\t\t"+"last_max_force \t"+"max_force_of_all \t"+"\n")
        output.writelines("----------------------------------------------------------\n")
        for item in summary:
            output.writelines(item["work_dir"]);output.writelines("\t")
            output.writelines(str(item["last_max_force"]))
            output.writelines('('+str(item["max_iter_num"])+')')
            output.writelines("\t")
            
            output.writelines(str(item["min_force_of_all"]))
            output.writelines('('+str(item["iter_num_of_min_force_of_all"])+')')
            output.writelines("\t")
            
            output.writelines("\n")
        output.writelines("----------------------------------------------------------\n\n")
'''
  main
'''
main()

