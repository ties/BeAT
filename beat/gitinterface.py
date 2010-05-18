from git import *
import time
from os import chdir, system

class GitInterface:
	folder = ""
	"""
	@require folder to be an existion folder in the filesystem
	@assure if folder contains a git repository it will use that repository. Else it will make a git repository there.
	"""
	def __init__(self, folder):
		self.folder = folder
		try:
			Repo(self.folder)
		except InvalidGitRepositoryError:
			chdir(self.folder)
			system("git init")
			Repo(self.folder)

	"""
	This function will return a list of objects.
	It wil return the given code and number amount of parents of this node as a list newest item first.
	@requres code be a git.Commit item.
	"""
	def parents_list(self, code, number):
		a = [code]
		if number > 0:
			a.extend(parents_list(code.parents[0],number-1))
		return a
	
	"""
	Returns a list of git nodes.
	@requires folder to be a Sring with the location of a .git folder
	It will preform parents_list on the given git folder with the given number.
	"""
	def get_any_parent(self, number):
		return parents_list(Repo(self.folder).head.commit,number)
	
	"""
	Returns the git.Commit of the given git hash
	@requires folder to be a Sring with the location of a .git folder
	@returns the git.Commit of the object associated wiht the given hash. Will return the startnode of the tree if item does not exist.
	"""
	def get_matching_item(self, hash):
		#iterator for all commits.
		i = Repo(self.folder).iter_commits()
		h = i.next()
		try:
			# try to mach the srint with all commits.
			while not(str(h.sha).startswith(hash)):
				h = i.next()
		except StopIteration:
			# only gets here when nothing matches and does nothing
			pass
		return h
	
	"""
	Returns a list of all the commits in the given folder.
	"""
	def get_all_commits(self):
		#iterator for all commits.
		i = Repo(self.folder).iter_commits()
		h = []
		try:
			# add every commit to a list.
			while 0 < 1:
				h.append(i.next())
		except StopIteration:
			# terminates the loop when all items are done.
			pass
		return h
	
	"""
	Takes a Tag and gives the commit its part of.
	@requires a string representing the tag of your object
	@returns the item matching that tag or if non found the nieuwest tag.
	"""
	def match_from_tag(self, giventag):
		repo = Repo(self.folder)
		tagref = TagReference.list_items(repo)
		x = 0
		b = 1 > 0
		while x < len(tagref)-1 and b:
			b = not(str(tagref[x].path).endswith(giventag))
			x = x + 1
		return tagref[x-1].commit
		
	"""
	Gives the committime of the given git.Commit
	In the form of a time.struct_time object
	"""
	def get_date(self, gitcommit):
		return time.gmtime(gitcommit.authored_date)
	
	"""
	Gives the name of the persone who commited the given commit.
	"""
	def get_author(self, gitcommit):
		return gitcommit.committer
	
	"""
	Returns the parent of the given commit.
	"""
	def get_parents(self, gitcommit):
		return gitcommit.parents[0]
	
	"""
	Makes a new git repository and sets it as the new default.
	@require given folder to exsist in the file system.
	@returns a new Repo object that is created in the given folder.
	@assure given repository is working repository.
	"""
	def make_new_repository(self, folder):
		self.folder = folder
		chdir(self.folder)
		system("git init")
	
	"""
	Switches working repository
	@require folder to contain a .git file.
	@assure the working repository is the given repository.
	"""
	def switch_repository(self, folder):
		self.folder = folder
		
	"""
	Prefoms a git clone Action wiht the given repository and wil place it in the working directory.
	@require Given directory does not contain a .git folder.
	"""
	def clone_repository(self, git):
		chdir(self.folder)
		system("git clone %s" % git)
	"""
	Allows pulling form git needs the git server as a string
	"""
	def pull_from_git(self, git):
		print "cd %s; git pull %s" % (self.folder, git)
		chdir(self.folder)
		system("git pull %s master" % git)

#pull_from_git("git@github.com:ties/BeAT")
#print get_date(get_matching_item(".", "c2bee8864"))
#<git.Commit "c2bee88640cc6bebfb9b79a0601d74a67e0cd5c0">