#####initialization of this module
#settings
#from settings import LOGS_PATH
#dulwich
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree
from dulwich.objects import Commit, parse_timezone
#for fs mechanisms
from os import *
#time
from time import time

LOGS_PATH = path.join(getcwd(), "logs")

# initialize the repo if it doesn't exists, or load it if it does
if not path.exists(LOGS_PATH):
	print "creating folder "+ LOGS_PATH
	mkdir(LOGS_PATH)
	repo = Repo.init(LOGS_PATH)
	blob = Blob.from_string("data")
	tree =Tree()
	tree.add(0100644, "initfile", blob.id)
	c = Commit()
	c.tree = tree.id
	author = "Writer a@a.com"
	c.author=c.committer=author
	c.commit_time=c.author_time=int(time())
	tz = parse_timezone('-0200')
	c.commit_timezone=c.author_timezone=tz
	c.encoding="UTF-8"
	c.message="initial commit"
	store = repo.object_store
	store.add_object(blob)
	store.add_object(tree)
	store.add_object(c)
	repo.refs['refs/heads/master'] = c.id
	repo.refs['HEAD'] = 'ref: refs/heads/master'
	print "success!"
else:
	#this is how to create a Repo object from an existing repository
	repo = Repo(LOGS_PATH)

#####static variables
default_perms = 0100644
store=repo.object_store

#####functions of this module
def get_latest_tree(repo):
    """Return the last known tree.
	"""
    commit_id = repo.head()
    commit = repo.commit(commit_id)
    tree_id = commit.tree
    return repo.tree(tree_id)

def create_log(contents, filename=None, overwrite=False):
	"""creates a log with the specified content.
	This function creates a log file in the git repository specified by LOGS_PATH in settings.py.
	If a file with name filename exists, False is returned, unless overwrite=True.
	Arguments:
		contents		the contents of the log, as a simple string
		filename		the specific filename to use. defaults to None, which automatically generates a filename.
		overwrite		whether or not to overwrite existing files. defaults to False, does change behavior when filename=None.
	Returns:
		False on failure, the filename to which the log was saved on success.
	Raises:
		GitFileError	when the file exists while overwrite is False
	"""
#	if not filename:
		
	
	if not contents:
		return False
	#create file
	blob = Blob.from_string(contents)
	tree = get_latest_tree(repo)

	if not path.exists(path.join(LOGS_PATH, filename)):
		tree[filename]=(default_perms, blob.id)
	else:
		if overwrite:
			tree[filename]=(default_perms, blob.id)
		else:
			return False

	commit = Commit()
	commit.tree=tree.id
	commit.author = commit.committer = "Logwriter a@a.a"
	commit.commit_time = commit.author_time = int(time())
	commit.commit_timezone = commit.author_timezone = parse_timezone('+0100')
	commit.encoding = "UTF-8"
	commit.message = "Writing log file %s"%(filename)
	
	store.add_object(blob)
	store.add_object(tree)
	store.add_object(commit)

	repo.refs['refs/heads/master'] = commit.id

	return True

def get_log(filename):
	"""reads and returns the specified log
	This function fetches a log specified by filename, reads it and returns it as a single string.
	This function will always read from the HEAD commit.
	Arguments:
		filename			the name of the file being read,
	Returns:
		The contents of the log.
	Raises:
		GitFileError		when the file does not exists, or when an exception is raised
	NOT IMPLEMENTED YET
	"""
	pass


class GitFileError(Exception):
	def __init__(self, error, filename=None):
		self.error	  = error
		self.filename = filename
	def __str__(self):
		if filename:
			return "Error occured while working with %s: %s."%(filename, error)
		else:
			return "Error occured: %s."%(error)
