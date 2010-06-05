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

from beat.settings import LOGS_PATH

class GitFileError(Exception):
	def __init__(self, error, filename=None):
		self.error	  = error
		self.filename = filename
	def __str__(self):
		if filename:
			return "Error occured while working with %s: %s."%(filename, error)
		else:
			return "Error occured: %s."%(error)

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
	tz = parse_timezone('+0200')
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
	from dulwich.errors import NotGitRepository
	try:
		repo = Repo(LOGS_PATH)
	except NotGitRepository as e:
		raise GitFileError("Error: the path %s exists but is not a git repository."%LOGS_PATH)

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

def create_log(contents, filename, overwrite=False):
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
	
	if not contents:
		return "Error: empty contents"

	if path.exists(path.join(LOGS_PATH, filename)) and not overwrite:
		return "Error: file exists, overwrite not specified"


	#create file
	blob = Blob.from_string(contents)
	tree = get_latest_tree(repo)

	tree[filename]=(default_perms, blob.id)

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
	try:
		for commit_id in repo.revision_history(repo.head()):
			tree = repo.tree(repo.commit(repo.head()).tree)
			if tree.__contains__(filename):
				(perms, file_blob_id)=tree.__getitem__(filename)
				return repo.get_blob(file_blob_id).as_raw_string()
	except Exception as e:
		raise GitFileError(e)


