import tarfile
import tempfile
import datetime
import time

def to_tar(jobs):
	"""
	Generates a temporary tarfile containing the contents of every script in a Job-list
	Returns tuple (filename, fileobj)
	"""
	tar_tempfile = tempfile.TemporaryFile()
	tfile = tarfile.open("jobs.tar.gz",mode="w|gz",fileobj=tar_tempfile)
	for job in jobs:
		file = tempfile.TemporaryFile()
		file.write(job.script)
		file.flush()
		file.seek(0)
		tarinf = tarfile.TarInfo(name="%s.pbs" % job.name)
		tarinf.size = len(job.script)
		tarinf.mtime = time.mktime(datetime.datetime.now().timetuple())
		tarinf.type = tarfile.REGTYPE
		tarinf.uname = 'beat'
		tarinf.gname = 'beat'
		tarinf.uid = 666
		tarinf.gid = 666
		tfile.addfile(tarinf,file)
	tfile.close()
	tar_tempfile.flush()
	return ("jobs.tar.gz",tar_tempfile)
	