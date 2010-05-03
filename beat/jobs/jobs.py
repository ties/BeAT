import sys



class JobGenerator:
	
	__directory = "."
	
	def __getSysInfo(self, toolname):
		result = ""
		result += "echo Nodename: $(uname -n)\n"
		result += "echo Hardware-name: $(uname -m)\n"
		result += "echo OS: $(uname -o)\n"
		result += "echo Kernel-name: $(uname -s)\n"
		result += "echo Kernel-release: $(uname -r)\n"
		result += "echo Kernel-version: $(uname -v)\n"
		result += "echo Hardware-platform: $(uname -i)\n"
		result += "echo Processor: $(uname -p)\n"
		result += "echo Memory-total: $(cat /proc/meminfo | grep MemTotal | tr -s " " | cut -d\" \" -f 2 -\n"
		result += "echo DateTime: $(date '+%Y %m %d %H %M %S') $[ $(date '+%N') / 1000]\n"
		
		result += "echo Tool version: $(" + toolname + " --version | cut -d' ' -f 2)\n"
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
	
	def pbsgen(self, toolname, modelname, nodes, tooloptions):
		"""Generates the jobs"""
		result = ""
		result += self.__makePBSHeader(modelname, toolname, nodes)
		result += "\n"
		
		result += "cd " + self.__directory + "\n"
		result += self.__setStack()
		result += "echo command: " + command + "\n"
		result += self.__getSysInfo()
		result += "\n"
		result += "memtime " + toolname + " " + tooloptions + " " + modelname + "\n"
		return result

if __name__ == '__main__':
	j = JobGenerator()
	print j.pbsgen("naam","20","memtime hoi")
	sys.exit(0)
