from git import *

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
	
#print get_any_parent("C:\Vakken\OWP",5)

#<git.Commit "c2bee88640cc6bebfb9b79a0601d74a67e0cd5c0">
#die moet nog op een of andere manier in gevuld kunne worden en iets mee gedaan worden maar het wekrt niet als je hem invuld.
# <git.Commit "c2bee88640cc6bebfb9b79a0601d74a67e0cd5c0">.author zou een gebruiker naam op moeten leveren maar het errord
