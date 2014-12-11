import sys 

num = 1

NB = 100000

c = 0
fic = None

with open(sys.argv[1],'r') as file:
    for line in file:
        if fic == None:
            print sys.argv[1] + str(num)
            fic = open(sys.argv[1] + str(num),"w")
        fic.write(line)
        c += 1
        if c % NB == 0:
            num += 1
            fic.close()
            fic = None
fic .close()