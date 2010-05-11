import sys
import time
import os

class Job:
	
	def __init__(self, fileName, script):
		self.name = fileName
		self.script = script


class JobGenerator:
	
	__directory = "."
	jobs = []
	
	
	def __getSysInfo(self, toolname, modelname, tooloptions):
		result = ""
		
		result += "echo BEGIN OF HEADER\n"
		
		result += "echo Nodename: $(uname -n)\n"
		result += "echo Hardware-name: $(uname -m)\n"
		result += "echo OS: $(uname -o)\n"
		result += "echo Kernel-name: $(uname -s)\n"
		result += "echo Kernel-release: $(uname -r)\n"
		result += "echo Kernel-version: $(uname -v)\n"
		result += "echo Hardware-platform: $(uname -i)\n"
		result += "echo Processor: $(uname -p)\n"
		result += "echo Memory-total: $(cat /proc/meminfo | grep MemTotal | tr -s \" \" | cut -d\" \" -f 2 -)\n"
		result += "echo DateTime: $(date '+%Y %m %d %H %M %S') $[ $(date '+%N') / 1000]\n"
		
		result += "echo ToolVersion: $(" + toolname + " --version | cut -d' ' -f 2)\n"
		result += "echo Call: " + toolname + " " + tooloptions + " " + modelname + "\n"
		
		result += "echo END OF HEADER\n"
		return result
	
	def __makePBSHeader(self, filename, nodes):
		result = ""
		result += "#PBS -q default\n"
		result += "#PBS -N beat_" + filename + "\n"
		result += "#PBS -l nodes=" + nodes + "\n"
		result += "#PBS -j oe\n"
		result += "#PBS -W x=NACCESSPOLICY:SINGLEJOB\n"
		return result
	
	def __setStack(self):
		result = ""
		result += "echo Setting stack to 64MB\n"
		result += "ulimit -s 65536\n"
		return result
	
	def pbsgen(self, nodes, toolname, tooloptions, modelname, prefix="", postfix="", filename=None):
		"""Generates the jobs"""
		result = ""
		if filename is None:
			result += self.__makePBSHeader(toolname, nodes)
		else:
			result += self.__makePBSHeader(filename, nodes)
		result += "\n"
		
		result += "cd " + self.__directory + "\n"
		result += self.__setStack()
		result += "echo command: " + prefix + " memtime " + toolname + " " + tooloptions + " " + modelname + "\n"
		result += self.__getSysInfo(toolname, modelname, tooloptions)
		result += "\n"
		if prefix:
			result += prefix + " memtime " + toolname + " " + tooloptions + " " + modelname + " " + postfix + "\n"
		else:
			result += "memtime " + toolname + " " + tooloptions + " " + modelname + " " + postfix + "\n"
		result += "\n"
		result += "REPORT ENDS HERE\n"
		return result
	
	def jobgen(self, nodes, toolname, tooloptions, modelname, prefix="", postfix="", filename=None):
		j= Job( filename+".pbs", self.pbsgen(nodes, toolname, tooloptions, modelname, prefix=prefix, postfix=postfix, filename=filename) )
		self.jobs.append(j)
		return j
	
	__ext2type = dict({'.lps': 'lps', '.tbf': 'lpo', '.b': 'nips', '.dve': 'dve'})
	
	def __extension_to_type(self, extension):
		return self.__ext2type.get(extension)
	
	def suitegen(self, modelname):
		
		base = modelname[:modelname.rfind('.')]
		lang = self.__extension_to_type(modelname[modelname.rfind('.'):])
		
		greytool = lang+"2lts-grey"
		reachtool = lang+"-reach"
		mpitool = lang+"2lts-mpi"
		stdNodes = "1:E5335,walltime=4:00:00"
		filenameBase = base + "-" + lang
		
		self.jobgen( stdNodes, greytool, "", modelname, filename=filenameBase+"-idx" )
		self.jobgen( stdNodes, greytool, "-cache", modelname, filename=filenameBase+"-idx-cache" )
		for vset in ["list", "tree", "fdd"]:
			self.jobgen( stdNodes, greytool, "--state vset --vset "+vset, modelname, filename=filenameBase+"-"+vset )
			self.jobgen( stdNodes, greytool, "--state vset --vset "+vset+" --cache", modelname, filename=filenameBase+"-"+vset+"-cache" )
		for order in ["bfs", "bfs2", "chain"]:
			for vset in ["list", "fdd"]:
				self.jobgen( stdNodes, reachtool, "--order "+order+" --vset "+vset, modelname, filename=filenameBase+"-"+order+"-"+vset )
		
		for W in [1, 2, 4]:
			mpiNodes = str(W)+":ppn=6:E5335,walltime=4:00:00"
			self.jobgen( mpiNodes, mpitool, "", modelname, filename=filenameBase+"-mpi-"+str(W)+"-6", prefix="mpirun -mca btl tcp,self" )
			self.jobgen( mpiNodes, mpitool, "--cache", modelname, filename=filenameBase+"-mpi-cache-"+str(W)+"-6", prefix="mpirun -mca btl tcp,self" )
		
	def generate_all(self):
		contents = os.listdir('.')
		for f in contents:
			if os.path.isfile(f) and os.path.splitext(f)[1] in self.__ext2type:
				self.suitegen(os.path.basename(f))
		

if __name__ == '__main__':
	j = JobGenerator()
	#print j.pbsgen("1", "lpo2lts-grey", "-cache", "dphil-10.tbf")
	#time.sleep(3)
	#j.suitegen("dphil-10.tbf")
	j.generate_all()
	for job in j.jobs:
		print job.name
	sys.exit(0)
