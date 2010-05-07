import sys

class JobGenerator:
	
	__directory = "."
	
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
		return result
	
	__stdNodes = "1:E5335,walltime=4:00:00"
	
	def suitegen(self, modelname):
		base = modelname[:modelname.rfind(".")]
		lang = modelname[modelname.rfind("."):]
		
		pbsgen( "1:E5335,walltime=4:00:00", lang+"2lts-grey", "", modelname, filename=base+"-"+lang+"-idx" )
		pbsgen( "1:E5335,walltime=4:00:00", lang+"2lts-grey", "-cache", modelname, filename=base+"-"+lang+"-idx-cache" )
		for vset in ["list", "tree", "fdd"]:
			pbsgen( "1:E5225,walltime=4:00:00", lang+"2lts-grey", "--state vset --vset "+vset, modelname, filename=base+"-"+lang+"-"+vset )
		pass
		
	def generate_all(self):
		pass
		

if __name__ == '__main__':
	j = JobGenerator()
	print j.pbsgen("1", "lpo2lts-grey", "-cache", "dphil-10.tbf")
	sys.exit(0)
