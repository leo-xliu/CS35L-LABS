#!/usr/bin/python

import random, sys, string, argparse

def shuffle(shuflist, rflag):
    length = len(shuflist)
    if rflag==False:
        for end in range(length, 0, -1):
            rand = random.randrange(end)
            print(shuflist.pop(rand))
    else:
        while True:
            rand = random.randrange(length)
            print(shuflist[rand])

def nshuffle(shuflist, rflag, nval):
    if rflag==False:
        end = len(shuflist)
        if (nval > end):
            nval = end
        while (nval != 0):
            rand = random.randrange(end)
            print(shuflist.pop(rand))
            end -= 1
            nval -= 1
    else:
        while (nval != 0):
            print(random.choice(shuflist))
            nval -= 1

def fshuffle(shuflist, rflag):
    length = len(shuflist)
    if rflag==False:
        for end in range(length, 0, -1):
            rand = random.randrange(end)
            sys.stdout.write(shuflist.pop(rand))
    else:
        while True:
            rand = random.randrange(length)
            sys.stdout.write(shuflist[rand])

def nfshuffle(shuflist, rflag, nval):
    endval = nval
    if rflag==False:
        end = len(shuflist)
        if(nval > end):
            endval = end
        while (endval != 0):
            rand  =random.randrange(end)
            sys.stdout.write(shuflist.pop(rand))
            end -= 1
            endval -= 1
    else:
        while (endval != 0):
            sys.stdout.write(random.choice(shuflist))
            endval -= 1
            
def main():
    parser = argparse.ArgumentParser(usage='shuf.py [OPTION]... [FILE]\n  or:  shuf.py -e [OPTION]... [ARG]...\n  or:  shuf.py -i LO-HI [OPTION]...\nWrite a random permutation of the input lines to standard output.',
                                     description='With no FILE, or when FILE is -, read standard input.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--echo', nargs='*', required=False, help='treat each ARG as an input line')

    group.add_argument('-i', '--input-range', required=False, help='treat each number LO through HI as an input line')

    parser.add_argument('-n', '--head-count', type=int, required=False, help='output at most COUNT lines', dest='COUNT')

    parser.add_argument('-r', '--repeat', action='store_true', required=False, help='output lines can be repeated')
    group.add_argument('infile', nargs='?', type=argparse.FileType('r'))
    args = parser.parse_args()

    command = sys.argv[1:]

    if (len(command) == 0):
        stdinlist = sys.stdin.readlines()
        fshuffle(stdinlist, args.repeat)
        exit()
    
    nbool = False
    try:
        ind = command.index('-n')
        command.pop(ind)
        command.pop(ind)
        nbool = True
    except:
        pass
    if nbool==True:
        if (args.COUNT < 0):
            raise Exception(f"invalid line count: {nval}")
    match command:
        case ['-e', *objs] | ['-r', '-e', *objs]:
            if nbool==True:
                nshuffle(args.echo, args.repeat, args.COUNT)
            else:
                print(nval)
                shuffle(args.echo, args.repeat)
        case ['-i', *objs] | ['-r', '-i', *objs]:
            if (args.input_range.find('.') != -1):
                raise Exception("invalid input type")
            ran = args.input_range.split('-')
            if (len(ran) != 2):
                raise Exception("invalid input range")
            int1 = int(ran[0])
            int2 = int(ran[1])
            diff = int2 - int1
            if (diff < 0):
                raise Exception("invalid input range")
            intlist=[]
            for i in range(int1, int2+1):
                intlist.append(i)
            if nbool==True:
                nshuffle(intlist, args.repeat, args.COUNT)
            else:
                shuffle(intlist, args.repeat)            
        case [*obj, '-'] | ['-', *obj]:
            stdinlist = sys.stdin.readlines()
            if nbool==True:
                nfshuffle(stdinlist, args.repeat, args.COUNT)
            else:
                fshuffle(stdinlist, args.repeat)
        case [*obj, infile] | [infile, *obj]:
            filelist = args.infile.readlines()
            if nbool==True:
                nfshuffle(filelist, args.repeat, args.COUNT)
            else:
                fshuffle(filelist, args.repeat)

if __name__ == "__main__":
    main()
