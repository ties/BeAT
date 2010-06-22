from git import *
import time
from os import chdir, system

class GitInterface:
	folder = ""
	has_repository = True

	def __init__(self, folder):
		"""
		@require folder to be an existion folder in the filesystem
		@assure if folder contains a git repository it will use that repository. Else it sets the working directory there and makes has_repository false.
		to get a working repository use make_new_repository,switch_repository or clone_repository
		"""
		self.folder = folder
		try:
			Repo(self.folder)
		except InvalidGitRepositoryError:
			chdir(self.folder)
			has_repository = False

	def parents_list(self, code, number):
		"""
		This function will return a list of objects.
		It wil return the given code and number amount of parents of this node as a list newest item first.
		@requres code be a git.Commit item.
		"""
		a = [code]
		if number > 0:
			a.extend(parents_list(code.parents[0],number-1))
		return a
	
	def get_any_parent(self, number):
		"""
		Returns a list of git nodes.
		@requires folder to be a Sring with the location of a .git folder
		It will preform parents_list on the given git folder with the given number.
		"""
		return parents_list(Repo(self.folder).head.commit,number)
	
	def get_matching_item(self, hash):
		"""
		Returns the git.Commit of the given git hash
		@requires folder to be a Sring with the location of a .git folder
		@returns the git.Commit of the object associated wiht the given hash. Will return the startnode of the tree if item does not exist.
		"""
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
	
	def get_all_commits(self):
		"""
		Returns a list of all the commits in the given folder.
		"""
		#iterator for all commits.
		i = Repo(self.folder).iter_commits()
		h = []
		try:
			# add every commit to a list.
			while True:
				h.append(i.next())
		except StopIteration:
			# terminates the loop when all items are done.
			pass
		return h
	
	def match_from_tag(self, giventag):
		"""
		Takes a Tag and gives the commit its part of.
		@requires a string representing the tag of your object
		@returns the item matching that tag or if non found the nieuwest tag.
		"""
		repo = Repo(self.folder)
		tagref = TagReference.list_items(repo)
		x = 0
		b = 1 > 0
		while x < len(tagref)-1 and b:
			b = not(str(tagref[x].path).endswith(giventag))
			x = x + 1
		return tagref[x-1].commit
		
	def get_date(self, gitcommit):
		"""
		Gives the committime of the given git.Commit
		In the form of a time.struct_time object
		"""
		return time.gmtime(gitcommit.authored_date)
	
	def get_author(self, gitcommit):
		"""
		Gives the name of the persone who commited the given commit.
		"""
		return gitcommit.committer
	
	def get_parents(self, gitcommit):
		"""
		Returns the parent of the given commit.
		"""
		return gitcommit.parents[0]
	
	def make_new_repository(self, folder):
		"""
		Makes a new git repository and sets it as the new default.
		@require given folder to exsist in the file system.
		@returns a new Repo object that is created in the given folder.
		@assure given repository is working repository.
		"""
		has_repository = True
		self.folder = folder
		chdir(self.folder)
		system("git init")
	
	def switch_repository(self, folder):
		"""
		Switches working repository
		@assure if folder contains a .git the working repository is the given repository with a repo. else you can now create a new repo here with clone_repository.
		"""
		has_repository = True
		self.folder = folder
		try:
			Repo(self.folder)
		except InvalidGitRepositoryError:
			has_repository = False
		
	def clone_repository(self, git):
		"""
		Prefoms a git clone Action wiht the given repository and wil place it in the working directory.
		@require Given directory does not contain a .git folder.
		"""
		chdir(self.folder)
		system("git clone %s" % git)
		has_repository = True

	def pull_from_git(self, git):
		"""
		Allows pulling form git needs the git server as a string
		"""
		chdir(self.folder)
		system("git pull %s master" % git)

#pull_from_git("git@github.com:ties/BeAT")
#print get_date(get_matching_item(".", "c2bee8864"))
#<git.Commit "c2bee88640cc6bebfb9b79a0601d74a67e0cd5c0">
