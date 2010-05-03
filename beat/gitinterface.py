from git import *
import time

# this function will return a list of objects.
# it wil return the given code and number amount of parents of this node as a list newest item first.
# @requres code be a git.Commit item.
def parents_list(code, number):
	a = [code]
	if number > 0:
		a.extend(parents_list(code.parents[0],number-1))
	return a
	
# returns a list of git nodes.
# @requires folder to be a Sring with the location of a .git folder
# it will preform parents_list on the given git folder with the given number.
def get_any_parent(folder, number):
	return parents_list(Repo(folder).head.commit,number)

# returns the commit date of the git hash
# @requires folder to be a Sring with the location of a .git folder
# @returns the committime in the form of a time.struct_time object of the object associated wiht the given hash will return he startdate of the tree if item does not exist.
def get_date(folder, hash):
	i = Repo(folder).iter_commits()
	h = i.next()
	try:
		while not(str(h.sha).startswith(hash)):
			h = i.next()
	except StopIteration:
		h
	return time.gmtime(h.authored_date)

print get_date("C:\Vakken\OWP", "c2bee8864")
#print get_any_parent("C:\Vakken\OWP",5)

#<git.Commit "c2bee88640cc6bebfb9b79a0601d74a67e0cd5c0">

