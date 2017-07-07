""" Repository manager version one
written by Eric Ohwotu """
import sys
import os
import xml.etree.cElementTree as ET
import shutil

#declare variables
VERBOSE = False #verbose mode for display status
MAX_MEMORY_SIZE = 30000 #max project size
DEF_PROJECT_PATH = "C:/Users/Eric/Documents/rep/"

""" first create the manifest file """
def create_manifest(projectName, version=1.0):
    newpath = DEF_PROJECT_PATH + projectName

    #create new path for the project
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        os.makedirs(newpath + "/version" + str(version)) # create folder for the version files
    else:
        display("Project already exists")
        return False
    #create xml file
    project = ET.Element("project")
    ET.SubElement(project, "name").text = projectName
    ET.SubElement(project, "version").text = str(version)
    ET.SubElement(project, "path").text = newpath
    ET.SubElement(project, "info").text = "manifest file created using rep version 1.0"
    files = ET.SubElement(project, "files")

    tree = ET.ElementTree(project)
    tree.write(newpath + "/manifest.xml")
    
    #write to display
    display("creating project for " + projectName + " at " + DEF_PROJECT_PATH)
    return True

""" add file to the project """
def add_file(projectName, filePath):
    filePath = filePath.replace("%20"," ")
    
    #ensure the file exists
    if not os.path.exists(filePath):
        display("file doesn't exists!!!")
        return False
    
    manifest = DEF_PROJECT_PATH + projectName + "/manifest.xml"
    tree = ET.parse(manifest)
    root = tree.getroot()

    #get the file node for the files to be appended to
    files = root.find('files')

    for f in files:
        if filePath == f.find('name').text:
            display("file already exists!!!")
            return False
        
    file = ET.SubElement(files, "file")
    ET.SubElement(file, "name").text = filePath

    tree.write(manifest)
    display("*** Adding " + filePath + " to project")
    return True

def set_target(projectName, filePath):
    filePath = filePath.replace("%20"," ")
    manifest = DEF_PROJECT_PATH + projectName + "/manifest.xml"
    tree = ET.parse(manifest)
    root = tree.getroot()

    #get the file node for the files to be appended to
    if not root.find("target") == None:
        root.find("target").text = filePath
    else:
        ET.SubElement(root, "target").text = filePath

    tree.write(manifest)
    display("*** setting target to "+ filePath)
    return True

def set_root(projectName, filePath):
    filePath = filePath.replace("%20"," ")
    manifest = DEF_PROJECT_PATH + projectName + "/manifest.xml"
    tree = ET.parse(manifest)
    root = tree.getroot()

    #get the file node for the files to be appended to
    if not root.find("root") == None:
        root.find("root").text = filePath
    else:
        ET.SubElement(root, "root").text = filePath

    tree.write(manifest)
    display("*** setting root to "+ filePath)
    return True

""" then move the files to repository folder """
def save(projectName):
    manifest = DEF_PROJECT_PATH + projectName + "/manifest.xml"
    tree = ET.parse(manifest)
    root = tree.getroot()

    vn = root.find('version').text
    if '.' in vn:
        root.find('version').text = get_version(float(vn))
    else:
        root.find('version').text = get_version(int(vn))

    tree.write(manifest)
    
    files = root.find("files")
    rp = root.find("root").text
    rf = "/version" + root.find("version").text + "/"
    nf = DEF_PROJECT_PATH + projectName + rf
    for file in files:
        fp = file.find("name").text
        display("*** Moving " + fp)
        nfn = nf + fp.replace(rp,"") #new file name
        os.makedirs(os.path.dirname(nfn),exist_ok=True)
        shutil.copy(fp,nfn)

    #get the file node for the files to be appended to
    if not root.find("saved") == None:
        root.find("saved").text = "yes"
    else:
        ET.SubElement(root, "saved").text = "yes"

    tree.write(manifest)
    
    display("*** Saving project for " + projectName)
    return True

""" commit files to new folder """
def commit(projectName):
    manifest = DEF_PROJECT_PATH + projectName + "/manifest.xml"
    tree = ET.parse(manifest)
    root = tree.getroot()

    files = root.find("files")
    
    rf = "/version" + root.find("version").text + "/"
    rp = DEF_PROJECT_PATH + projectName + rf #target path
    np = root.find("root").text
    nf = root.find("target").text 
    for file in files:
        fp = file.find("name").text
        fp = DEF_PROJECT_PATH + projectName + rf + fp.replace(np,"")
        display("*** Copying from " + fp)
        nfn =  nf + fp.replace(rp,"") #new file name
        display("*** Copying to " + nfn)
        os.makedirs(os.path.dirname(nfn),exist_ok=True)
        shutil.copy(fp,nfn)

    #get the file node for the files to be appended to
    if not root.find("committed") == None:
        root.find("committed").text = "yes"
    else:
        ET.SubElement(root, "committed").text = "yes"

    tree.write(manifest)
    
    display("pushing project for " + projectName + " to " + nf)
    return True

""" get file information from manifest """
def info(projectName):
    manifest = DEF_PROJECT_PATH + projectName + "/manifest.xml"

    tree = ET.parse(manifest).getroot()
    for i in tree:
        display(i.tag+": "+str(i.text))
        #show all files
        if i.tag == 'files':
            for j in i:
                display("|--> file: " + j.find('name').text)

def get_p(a):
    path=""
        
    for x in sys.argv[a:]:
        path += x + "%20"
        
    return path[:-3]

""" get the new version """
def get_version(x):
    #split the number
    if isinstance(x, int):
        return str(x+1)
    elif isinstance(x, float):
        num = str(x).split('.')
        incr = str(1).zfill(len(num[1]))
        newVal = int(num[1])+int(incr)
        return ".".join((num[0],str(newVal)))

        
def print_help():
    print("commands are a s follows:")
    print("   rep --create <projectname>: creates a project of <projectname> in the rep folder")
    print("   rep --save <projectname>: saves all files to a temporary location in the rep folder")
    print("   rep --add <projectname> <filename>: adds the file to the project manifest file")
    print("   rep --commit <projectname>: commits all files into the final project directory")
    print("   rep --root <projectname> <rootdirectory>: adds the working directory")
    print("   rep --target <projectname> <rootdirectory>: sets te final project directory")
    None


""" print information to console in verbose mode """
def display(s):
    print(s)
    None

if __name__ == "__main__":

    if sys.argv[1] == "--create":
        create_manifest(sys.argv[2])
    elif sys.argv[1] == "--save":
        save(sys.argv[2])
    elif sys.argv[1] == "--commit":
        commit(sys.argv[2])
    elif sys.argv[1] == "--info":
        info(sys.argv[2])
    elif sys.argv[1] == "--target":
        path = get_p(3)
        set_target(sys.argv[2], path)
    elif sys.argv[1] == "--root":
        path = get_p(3)
        set_root(sys.argv[2], path)
    elif sys.argv[1] == "--file":
        path = get_p(3)
        add_file(sys.argv[2],path)
    elif sys.argv[1] == "--help":
        print_help()
    
    
        
