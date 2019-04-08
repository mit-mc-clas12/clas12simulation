from __future__ import print_function
from utils import utils, file_struct
import sqlite3, os, shutil, argparse

#This allows a user to specifiy which batch to use to generate files using a specific BatchID
argparser = argparse.ArgumentParser()
argparser.add_argument('-b','--batchID', default='none', help = 'Enter the ID# of the batch you want to submit (e.g. -b 23)')
args = argparser.parse_args()

#This uses the argument passed from command line, if no args, grab most recent DB entry
def grab_batchID(DBname,args):
  if args.batchID != 'none':
    BatchID = args.batchID
  else:
    strn = "SELECT BatchID FROM Batches;"
    Batches = utils.sql3_grab(DBname,strn)
    BatchID = max(Batches)[0]
  return BatchID

#Grabs all GCards from a corresponding Batch
def grab_gcards(DBname,BatchID):
  strn = "SELECT GcardID, gcard_text FROM GCards WHERE BatchID = {};".format(BatchID)
  gcards = utils.sql3_grab(DBname,strn)
  return gcards

#This function writes a file from a file object (see file_struct file). This is currently not done consicely and should be improved for code readability
def write_files(sub_file_obj,params):
  run_script_loc = ''
  sf = sub_file_obj
  p = params
  if sf.name != file_struct.run_job_obj.name:
    old_vals, new_vals = utils.grab_DB_data(p['DBname'],p['table'],sf.overwrite_vals,p['BatchID'])
  else:
    old_vals, new_vals = sf.overwrite_vals.keys(), (run_script_loc,)
  print("Writing submission file '{0}' based off of specifications of BatchID = {1}, GcardID = {2}".format(sf.filebase,
        p['BatchID'],p['GcardID']))
  extension = "_gcard_{}_batch_{}".format(p['GcardID'],p['BatchID'])
  newfile = sf.file_path+sf.filebase+extension+sf.file_end
  out_strn = utils.overwrite_file(p['temp_location']+sf.filebase+sf.file_end+".template",newfile,old_vals,new_vals)
  if sf.filebase == 'runscript':
    out_strn = utils.overwrite_file(newfile,newfile,['gcards_gcard',],[p['gfile'],])#Need to pass arrays to overwrite_file function
    run_script_loc = newfile
  str_script_db = out_strn.replace('"',"'") #I can't figure out a way to write "" into a sqlite field without errors
  #For now, we can replace " with ', which works ok, but IDK how it will run if the scripts were submitted to HTCondor
  for field, value in ((sf.field_loc,str_script_db),(sf.script_name,newfile)):
    strn = 'UPDATE Submissions SET {0} = "{1}" WHERE GcardID = {2};'.format(field,value,p['GcardID'])
    utils.sql3_exec(file_struct.DBname,strn)

#Grabs batch and gcards as described in respective files
BatchID = grab_batchID(file_struct.DBname,args)
gcards = grab_gcards(file_struct.DBname,BatchID)

#Create a set of submission files for each gcard in the batch
for gcard in gcards:
  GcardID = gcard[0]
  newfile = "gcard_{}_batch_{}.gcard".format(GcardID,BatchID)
  gfile= file_struct.sub_files_path+file_struct.gcards_dir+newfile
  with open(gfile,"w") as file: file.write(gcard[1])
  strn = "INSERT INTO Submissions(BatchID,GcardID) VALUES ({0},{1});".format(BatchID,GcardID)
  utils.sql3_exec(file_struct.DBname,strn)
  params = {'DBname':file_struct.DBname,'table':'Scards','BatchID':BatchID,'GcardID':GcardID,
            'gfile':gfile,'temp_location':file_struct.temp_location}
  write_files(file_struct.condor_file_obj,params)
  write_files(file_struct.runscript_file_obj,params)
  write_files(file_struct.run_job_obj,params)
