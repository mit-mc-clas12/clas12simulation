import argparse, sys, os, subprocess, socket

# declare a global dictionary to match genOutput and genExecutable to generator row
genOutput= {'clasdis': 'sidis.dat', 'dvcsgen': 'dvcs.dat','generate-dis':'dis-rad.dat'}
genExecutable =  {'clasdis': 'clasdis', 'dvcsgen': 'dvcsgen','generate-dis':'generate-dis'}

# Proper configuration of scard:
scard_key = ['group','user','nevents','generator', 'genOptions',  'gcards', 'jobs',  'project', 'luminosity', 'tcurrent',  'pcurrent']
parser_path = os.path.dirname(os.path.realpath(__file__))

# from https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
def ordinal(n):
    return "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class scard_parser:
# Default Constructor: a = scard_parser();  a.parse_scard("scard.txt")
# Parametrized Constructor:  a = scard_parser("scard.txt")
    def __init__(self, scard_filename=None):
        self.type ='scard parser'
        self.data = {}
        if scard_filename != None:
            self.parse_scard(scard_filename)

# void function for saving line into a dictionary
    def parse_scard_line(self, linenum, line):
        self.validate_scard_line(linenum, line) # 1st validating
        pos_delimeter_colon = line.find(":")
        pos_delimeter_hash = line.find("#")
        key =   line[:pos_delimeter_colon].strip()
        value=  line[pos_delimeter_colon+1:pos_delimeter_hash].strip()
        if key != scard_key[linenum]:
            print "ERROR: The " + ordinal(linenum+1) +" line of steering card starts with "+ key +"."
            print "That line must have the key " + scard_key[linenum] +"."
        self.data[key] = value

# voild function for parsing scard.txt into a dictionary
    def parse_scard(self, filename, store=True):
        scard=open(filename, "r")
        for linenum, line in enumerate(scard):
            self.parse_scard_line(linenum,line)
        if store == True:
            self.store()

#void function for validating s_card
    def validate_scard_line(self, linenum, line):
        if line.count("#") ==0:
            print "Warning: No comment in "+ ordinal(linenum+1) + " line."
        elif line.count("#")>1:
            print "ERROR: number of hashes>1 at "+ordinal(linenum+1)+" line."
            print "# can be only used for a delimeter and for once. Stopped."
            exit()
        if line.count(":") ==0:
            print "ERROR: No colon in "+ ordinal(linenum+1) + " line."
            print "The data cannot be interpreted. Stopped."
            exit()
        elif line.count(":")>1:
            print "ERROR: number of colons>1 at "+ordinal(linenum+1)+" line."
            print "\':\' can be only used for a delimeter and for once. Stopped."
            exit()
# store info's in dictionary into single variables
    def store(self):
        self.group = self.data.get("group")
        self.user = self.data.get("user")
        self.nevents = self.data.get("nevents")
        self.generator = self.data.get("generator")
        self.genOptions = self.data.get("genOptions")
        self.gcards = self.data.get("gcards")
        self.jobs = self.data.get("jobs")
        self.project = self.data.get("project")
        self.luminosity = self.data.get("luminosity")
        self.tcurrent = self.data.get("tcurrent")
        self.pcurrent = self.data.get("pcurrent")
        self.genOutput = genOutput.get(self.data.get("generator"))
        self.genExecutable = genExecutable.get(self.data.get("generator"))

def write_clas12_condor(project, nevents, jobs, scard_name):
    file_template = open(parser_path+"/clas12.condor.template","r")
    str_template = file_template.read()
    file_template.close()
    str_script=str_template.replace('project_scard', project)
    str_script=str_script.replace('nevents_scard', nevents)
    str_script=str_script.replace('jobs_scard', jobs)
    str_script=str_script.replace('scard_name', scard_name)
    # hostname = socket.gethostname()
    # if hostname == "scosg16.jlab.org":
    #     str_script=str_script.replace("(GLIDEIN_Site == \"MIT_CampusFactory\" && BOSCOGroup == \"bosco_lns\") ","HAS_SINGULARITY == TRUE")
    print "Preparing \'clas12.condor\' in current directory ..."
    file = open("clas12.condor","w")
    file.write(str_script)
    file.close()

def write_runscript_sh(group, user, genExecutable, nevents, genOptions, genOutput, gcards, luminosity, tcurrent, pcurrent, scard_name):
    file_template = open(parser_path+"/runscript.sh.template","r")
    str_template = file_template.read()
    file_template.close()
    str_script=str_template.replace('group_scard', group)
    str_script=str_script.replace('user_scard',user)
    str_script=str_script.replace('genExecutable_scard', genExecutable)
    str_script=str_script.replace('nevents_scard', nevents)
    str_script=str_script.replace('genOptions_scard', genOptions)
    str_script=str_script.replace('genOutput_scard', genOutput)
    if luminosity == '0':
        LUMIOPTION = ''
    else:
        LUMIOPTION = ' -LUMI_EVENT=\"'+luminosity+', 248.5*ns, 4*ns\" -LUMI_P=\"e-, 10.6*GeV, 0*deg, 0*deg\" -LUMI_V=\"(0.0, 0.0, -10)cm\" -LUMI_SPREAD_V=\"(0.03, 0.03)cm\"'
    str_script=str_script.replace('LUMIOPTION_scard', LUMIOPTION)
    str_script=str_script.replace('gcards_scard', gcards)
    str_script=str_script.replace('NLUMI_scard', luminosity)
    str_script=str_script.replace('tcurrent_scard', tcurrent)
    str_script=str_script.replace('pcurrent_scard', pcurrent)
    str_script=str_script.replace('scard_name', scard_name)
    print "Preparing \'runscript.sh\' in current directory ..."
    file = open("runscript.sh","w")
    file.write(str_script)
    file.close()
   #subprocess.call(["chmod","+x","runscript.sh"])
    os.chmod("runscript.sh", 0775)

def write_clas12_osg_condor(project, nevents, jobs, scard_name):
    file_template = open(parser_path+"/clas12_osg.condor.template","r")
    str_template = file_template.read()
    file_template.close()
    str_script=str_template.replace('project_scard', project)
    str_script=str_script.replace('nevents_scard', nevents)
    str_script=str_script.replace('jobs_scard', jobs)
    str_script=str_script.replace('scard_name', scard_name)
    # hostname = socket.gethostname()
    # if hostname == "scosg16.jlab.org":
    #     str_script=str_script.replace("(GLIDEIN_Site == \"MIT_CampusFactory\" && BOSCOGroup == \"bosco_lns\") ","HAS_SINGULARITY == TRUE")
    print "Preparing \'clas12_osg.condor\' in current directory ..."
    file = open("clas12_osg.condor","w")
    file.write(str_script)
    file.close()

def write_runscript_osg_sh(group, user, genExecutable, nevents, genOptions, genOutput, gcards, luminosity, tcurrent, pcurrent, scard_name):
    file_template = open(parser_path+"/runscript_osg.sh.template","r")
    str_template = file_template.read()
    file_template.close()
    str_script=str_template.replace('group_scard', group)
    str_script=str_script.replace('user_scard',user)
    str_script=str_script.replace('genExecutable_scard', genExecutable)
    str_script=str_script.replace('nevents_scard', nevents)
    str_script=str_script.replace('genOptions_scard', genOptions)
    str_script=str_script.replace('genOutput_scard', genOutput)
    str_script=str_script.replace('gcards_scard', gcards)
    if luminosity == '0':
        LUMIOPTION = ''
    else:
        LUMIOPTION = ' -LUMI_EVENT=\"'+luminosity+', 248.5*ns, 4*ns\" -LUMI_P=\"e-, 10.6*GeV, 0*deg, 0*deg\" -LUMI_V=\"(0.0, 0.0, -10)cm\" -LUMI_SPREAD_V=\"(0.03, 0.03)cm\"'
    str_script=str_script.replace('LUMIOPTION_scard', LUMIOPTION)
    str_script=str_script.replace('tcurrent_scard', tcurrent)
    str_script=str_script.replace('pcurrent_scard', pcurrent)
    str_script=str_script.replace('scard_name', scard_name)
    print "Preparing \'runscript_osg.sh\' in current directory ..."
    file = open("runscript_osg.sh","w")
    file.write(str_script)
    file.close()
   #subprocess.call(["chmod","+x","runscript_osg.sh"])
    os.chmod("runscript_osg.sh", 0775)


def condor_submit():
    print "submitting jobs from python script...\n"
    subprocess.call(["condor_submit","clas12.condor"])

def condor_osg_submit():
    print "submitting jobs from python script...\n"
    subprocess.call(["condor_submit","clas12_osg.condor"])
