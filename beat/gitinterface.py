from git import *
import time
from os import system

class GitInterface:
	folder = ""
	def __init__(self, folder):
		self.folder = folder
	
	# this function will return a list of objects.
	# it wil return the given code and number amount of parents of this node as a list newest item first.
	# @requres code be a git.Commit item.
	def parents_list(self, code, number):
		a = [code]
		if number > 0:
			a.extend(parents_list(code.parents[0],number-1))
		return a
		
	# returns a list of git nodes.
	# @requires folder to be a Sring with the location of a .git folder
	# it will preform parents_list on the given git folder with the given number.
	def get_any_parent(self, number):
		return parents_list(Repo(self.folder).head.commit,number)
	
	# returns the git.Commit of the given git hash
	# @requires folder to be a Sring with the location of a .git folder
	# @returns the git.Commit of the object associated wiht the given hash. Will return the startnode of the tree if item does not exist.
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
	
	#returns a list of all the commits in the given folder.
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
	
	#gives the committime of the given git.Commit
	#in the form of a time.struct_time object
	def get_date(self, gitcommit):
		return time.gmtime(gitcommit.authored_date)
	
	# gives the name of the persone who commited the given commit.
	def get_author(self, gitcommit):
		return gitcommit.committer
	
	#returns the parent of the given commit.
	def get_parents(self, gitcommit):
		return gitcommit.parents[0]
	
	# allows pulling form git needs the git server as a string
	def pull_from_git(self, git):
		print "cd %s; git pull %s" % (self.folder, git)
		system("cd %s" % self.folder)
		system("git pull %s" % git)

#pull_from_git("git@github.com:ties/BeAT")
#print get_date(get_matching_item(".", "c2bee8864"))
#<git.Commit "c2bee88640cc6bebfb9b79a0601d74a67e0cd5c0">