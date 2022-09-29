#!/usr/local/cs/bin/python3
import os, sys, zlib

#use snake case declaration 
#don't use any commands (including git)
#use strace -f to verify no commands are used

class CommitNode:
    def __init__(self, commit_hash):
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set() 
        self.children_copy = set() #for sticky start since my implementation of topo sort removes children
        self.branch = [] # if node is a branch head then we put its name here

    def __lt__(self, other): #for comparison operator overloading
      return (self.commit_hash < other.commit_hash) 
    
    def add_parent(self, parent_hash):
        self.parents.add(parent_hash)
    
    def add_children(self, children_hash):
        self.children.add(children_hash)
        self.children_copy.add(children_hash) 
    
    def add_branch(self, branch_name):
        self.branch.append(branch_name)

    def rem_children(self, children_hash):
        self.children.discard(children_hash)
    
    #finds commits that are children that have not yet been added and adds them
    def find_children(self, commit_graph): 
        for commit_node in commit_graph: 
            for commit_parent in commit_node.parents:
                if (self.commit_hash == commit_parent):
                    self.children.add(commit_node.commit_hash)
                    self.children_copy.add(commit_node.commit_hash)

    #generate branch head string 
    def print_branch(self):
        if (len(self.branch) == 0):
            return ""
        self.branch.sort() #for lexicographic order
        string = ""
        for name in self.branch:
            string = string + " " + name
        return string # (ex. " branch1 branch2" note the extra space in front!)

    #generate parents for sticky end
    def print_parents(self):
        if (len(self.parents) == 0):
            return ""
        string = ""
        for name in self.parents:
            string = string + " " + name
        return string[1:] #since there is an extra space in front
            
    #generate children for sticky start
    def print_children(self):
        if (len(self.children_copy) == 0):
            return ""
        string = ""
        for name in self.children_copy:
            string = string + " " + name
        return string[1:] #since there is an extra space in front

#creates a list of the current commits parent commit hashes
def find_parents(commit_hash, git_obj_dir):
    parent_stack = []
    #access commit object to obtain parent commits
    file = open(git_obj_dir + '/' + commit_hash[0:2] + '/' + commit_hash[2:40], 'rb')
    commit_code = file.read()
    file.close()
    commit_info = zlib.decompress(commit_code).decode('utf-8')
    #break down commit object until it is individual words to find parent commit hash
    for commit_line in commit_info.split('\n'):
        words = commit_line.split(' ')
        if (words[0] == "parent"):
            parent_stack.append(words[1])
    return parent_stack

def find_root(commit_graph):
    for commit in commit_graph:
        if (len(commit.parents) == 0):
            return commit

def topo_order_commits():
    repo_exit = False
    cur_dir = os.getcwd()
    #look for repo while ascending to root dir
    while (cur_dir != '/'):
        #check for repo existence
        if (os.path.isdir(cur_dir + "/.git")):
            repo_exit = True
            break
        #go to parent repo
        cur_dir = os.path.dirname(cur_dir)
    #throw error
    if (repo_exit == False):
        sys.stderr.write("Not inside a Git repository")
        exit(1)

    git_branch_dir = cur_dir + "/.git/refs/heads"
    git_obj_dir = cur_dir + "/.git/objects"
    
    #name of heads files (that contain each heads commit hash)
    possible_branch_list = os.listdir(git_branch_dir)
    branch_list = []
    for branch in possible_branch_list:
        while (os.path.isdir(git_branch_dir + '/' + branch)):
            inside_branch = os.listdir(git_branch_dir + '/' + branch)
            for branch_with_slash in inside_branch: #assuming that listdir only gives back one result
                branch = branch + '/' + branch_with_slash
        branch_list.append(branch)
            
    #set for commit graph
    commit_graph = set()

    #algorithm to create commit graph
    for branch_name in branch_list:

        parent_stack = []
        
        #obtain hash
        file = open(git_branch_dir + '/' + branch_name, 'r')
        branch_id = file.read()  #commit hash
        branch_id_new = branch_id[0:40] #need '0:40' because it contains a '\n' at the end
        file.close()

        #check if branch head commit already exists (different branch same commit)
        #still need to add branch name in 
        branch_exists = False
        for commit in commit_graph:
            if (branch_id_new == commit.commit_hash):
                branch_exists = True
                commit.add_branch(branch_name)
                break
        if (branch_exists):
            continue

        #set up branch head commit
        branch_node = CommitNode(branch_id_new) 
        branch_node.add_branch(branch_name)
        branch_parents = find_parents(branch_id_new, git_obj_dir) #no parent case will catch itself
        
        #unnecessary for first branch but needed for the rest
        #configure its parents
        for parent in branch_parents:
            branch_node.add_parent(parent)
            #we dont want to add to parent stack if already in commit graph
            node_exists = False
            for possible_parent in commit_graph:
                if (parent == possible_parent.commit_hash):
                    #update the existing parent's children 
                    possible_parent.add_children(branch_node.commit_hash)
                    node_exists = True
                    break
            if (not node_exists):
                parent_stack.append(parent)    
        
        #add commit to graph
        commit_graph.add(branch_node)

        #now complete rest of graph
        while (len(parent_stack) != 0):
            #set up current node 
            cur_node = CommitNode(parent_stack.pop())
            cur_node.find_children(commit_graph)
            cur_node_parents = find_parents(cur_node.commit_hash, git_obj_dir)
            
            #configure its parents
            for parent in cur_node_parents:
                cur_node.add_parent(parent)
                #we dont want to add to parent stack if already in commit graph
                node_exists = False
                for possible_parent in commit_graph:
                    if (parent == possible_parent.commit_hash):
                        #update the existing parent's children 
                        possible_parent.add_children(cur_node.commit_hash)
                        node_exists = True
                        break
                if (not node_exists):
                    parent_stack.append(parent)
            
            #finish by adding current node to graph
            commit_graph.add(cur_node)
        #once parent stack is empty (we have hit the root commit), we move to next branch

    #find root commit
    root_commits = find_root(commit_graph)

    #topological sort commit graph 
    sorted_commit_graph = sorted(commit_graph)

    topo_order_sort = []
    queue = []
    
    while (len(sorted_commit_graph) != 0):
        #find all commits with no children and add to queue
        copied_commit_graph = sorted_commit_graph.copy()
        for commit in copied_commit_graph:
            if (len(commit.children) == 0):
                queue.append(commit)
                sorted_commit_graph.remove(commit)
        
        cur_node = queue.pop(0)
        topo_order_sort.append(cur_node)

        #remove itself from its parents' children
        parent_list = sorted(cur_node.parents)
        for parent in parent_list:
            for commit in sorted_commit_graph:
                if (parent == commit.commit_hash):
                    commit.rem_children(cur_node.commit_hash)

    #print commit hashes in topological ordering
    for i in range(len(topo_order_sort)):
        string = topo_order_sort[i].commit_hash + topo_order_sort[i].print_branch()
        print(string)
        if (topo_order_sort[i].commit_hash == root_commits.commit_hash):
             break 
        #check if need sticky end and start
        need_sticky = True
        for parent in topo_order_sort[i].parents:
            if (topo_order_sort[i+1].commit_hash == parent):
                need_sticky = False
                break
        if (need_sticky):
            stickyend = topo_order_sort[i].print_parents() + '='
            print(stickyend + '\n')
            stickystart = '=' + topo_order_sort[i+1].print_children()
            print(stickystart)

                     

if __name__ == "__main__":
    topo_order_commits()

#//////////////////////////////////////////////////////////////////////////////////////


#For my implementation, I made sure to not call any git plumbing commands such as cat-file. 
#Furthermore, I did not use any shell commands for my implementation as well. All the 
#functions I have called pertain to python libraries that are permitted such using 
#os for file system information, sys for printing to stderr, and zlib to decompress files. 
#I used the command "strace -f python3 ./topo_order_commits.py" to verify this. The output
#of this function gives a stream of sys calls that were made during the execution of the 
#python script. Tracing through the code, I do not see any illegal calls to git commands
#so my code pertains to the requirements. 


#/////////////////////////////////////////////////////////////////////////////////////


# #time for some debugging
# i = 1
# for commit in commit_graph:
#     print(str(i) + ":")
#     print(commit.commit_hash)
#     print(commit.branch)
#     i = i + 1
# commit graph is functional

# print(root_commits.commit_hash)
# for commit in root_commits.children:
#     print(commit)
#root commits is functional