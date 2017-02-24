
import numpy as np
import scipy.io as sio
from scipy.sparse import csc_matrix, coo_matrix, csr_matrix, lil_matrix

def saveSimpleDictData(simdict, outdata):
    with open(outdata, 'w') as fw:
        for k, v in simdict.iteritems():
            fw.write("{}:{}\n".format(k,v))
        fw.close()

def loadSimpleDictData(indata):
    simdict={}
    with open(indata, 'r') as fr:
        lines=fr.readlines()
        for line in lines:
            line = line.strip().split(':')
            simdict[int(line[0])]=float(line[1])
        fr.close()
    return simdict

def saveDictListData(dictls, outdata):
    with open(outdata, 'w') as fw:
        for k, l in dictls.iteritems():
            if type(l) != list:
                print "This is not a dict of value list.\n"
                break
            fw.write("{}:".format(k))
            for i in range(len(l)-1):
                fw.write("{} ".format(l[i]))
            fw.write("{}\n".format(l[-1]))
        fw.close()

def loadDictListData(indata, ktype=str, vtype=str):
    dictls={}
    with open(indata, 'r') as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip().split(':')
            lst=[]
            for e in line[1].strip().split(' '):
                lst.append(vtype(e))
            dictls[ktype(line[0].strip())]=lst
        fr.close()
    return dictls

def saveSimpleListData(simls, outdata):
    with open(outdata, 'w') as fw:
        fw.write('\n'.join(map(str, simls)))
        fw.write('\n')
        '''
        for v in simls:
            fw.write("{}\n".format(v))
        '''
        fw.close()

def loadSimpleList(indata, dtype=None):
    sl=[]
    with open(indata, 'r') as fi:
        for e in fi:
            e = e.strip()
            if e == '':
                continue
            if dtype is not None:
                e = dtype(e)
            sl.append(e)
        fi.close()
    return sl

def save2DarrayData(sarray,outdata):
    with open(outdata, 'w') as fw:
        for l in sarray:
            if len(l) > 0:
                for i in range(len(l)-1):
                    fw.write("{} ".format(l[i]))
                fw.write("{}\n".format(l[-1]))
        fw.close()

def load2DarrayData(indata):
    a2d=[]
    with open(indata, 'r') as fi:
        for l in fi:
            arr = l.strip().split(' ')
            a2d.append(arr)
        fi.close()
    return a2d

def scsmatrix2edgelist(scsm, weighted=False):
    el = []
    rows, cols = scsm.nonzero()
    l = len(rows)
    for i in range(l):
        if weighted == True:
            el.append((rows[i], cols[i], scsm[rows[i], cols[i]]))
        else:
            el.append((rows[i], cols[i]))
    return el

def writeedgelist(el, ofile, weighted=False):
    out = open(ofile, "wb")
    for e in el:
        if weighted==True:
            out.write("%d %d %f\n" % (e[0], e[1], e[2]))
        else:
            out.write("%d %d\n" % (e[0], e[1]))
    out.close()

def readedge2squarecscm(ifile, weighted=False, delimiter=' '):
    xs=[]
    ys=[]
    data=[]
    with open(ifile, 'rb') as fin:
        for line in fin:
            coords=line.strip().split(delimiter)
            xs.append(int(coords[0]))
            ys.append(int(coords[1]))
            if weighted:
                data.append(float(coords[2]))
            else:
                data.append(1.0)
        fin.close()
    M = max(max(xs), max(ys)) +1
    cscm = csc_matrix((data, (xs, ys)), shape=(M,M))
    return cscm

def cscmatrix2groupedges(scsm):
    ges = []
    rows, cols = scsm.nonzero()
    l = len(rows)
    for i in range(l):
        ges.append((rows[i], cols[i]))
    return ges

def writegroupedges(ges, ofile):
    out = open(ofile, "wb")
    for ge in ges:
        out.write("%d %d\n" % ge)
    out.close()

def readedge2coom(ifile, weighted=False, delimiter=' ', idstartzero=True):
    xs=[]
    ys=[]
    data=[]
    if idstartzero is True:
        offset = 0
    else:
        offset = -1
    with open(ifile, 'rb') as fin:
        for line in fin:
            coords=line.strip().split(delimiter)
            xs.append( int(coords[0]) + offset )
            ys.append( int(coords[1]) + offset )
            if weighted:
                data.append(float(coords[2]))
            else:
                data.append(1)
        fin.close()
    M = max(xs) + 1
    N = max(ys) + 1
    coom = coo_matrix((data, (xs, ys)), shape=(M,N))
    #M1 = coom > 0
    #return M1.astype('int')
    return coom

def loadedge2sm(ifile, mtype=csc_matrix, weighted=False, dtype=int, delimiter=' ',
                idstartzero=True, issquared=False):
    '''
    load edge list into sparse matrix
    matrix dimensions are decided by max row id and max col id
    support csr, coo, csc matrix
    '''
    xs=[]
    ys=[]
    data=[]
    if idstartzero is True:
        offset = 0
    else:
        offset = -1
    with open(ifile, 'rb') as fin:
        for line in fin:
            coords=line.strip().split(delimiter)
            xs.append( int(coords[0]) + offset )
            ys.append( int(coords[1]) + offset )
            if weighted:
                data.append(dtype(coords[2]))
            else:
                data.append(1)
        fin.close()
    m = max(xs) + 1
    n = max(ys) + 1
    if issquared is False:
        M, N = m, n
    else:
        M = max(m,n)
        N = max(m,n)
    sm = mtype((data, (xs, ys)), shape=(M,N))
    return sm

def savesm2edgelist(sm, ofile, idstartzero=True, delimiter=' ', kformat=None):
    '''
    Save sparse matrix into edgelist
    kformat = "{0:.1f}"
    '''
    offset = 0 if idstartzero else 1
    lsm = sm.tolil()
    with open(ofile, 'wb') as fout:
        i = 0
        for row, d in zip(lsm.rows, lsm.data):
            for j,w in zip(row, d):
                if kformat is not None:
                    w = str.format(kformat, w)
                ostr = delimiter.join([str(i+offset), str(j+offset), str(w)])
                #fout.write('{} {} {}\n'.format(i+offset, j+offset, w))
                fout.write(ostr+'\n')
            i+=1
        fout.close()
    return

def procHomo():
    hm=sio.loadmat("../Homo_sapiens.mat")
    hel = scsmatrix2edgelist(hm['network'])
    writeedgelist(hel, "../HomoSapiens-dataset/Homo_sapiens.edgelist")
    hges = scsmatrix2groupedges(hm['group'])
    writegroupedges(hges, "../HomoSapiens-dataset/Homo_sapiens.groupedges")

def procWiki():
    wm = sio.loadmat("../POS-wikipedia.mat")
    wel = scsmatrix2edgelist(wm['network'], weighted=True)
    writeedgelist(wel, "../WikipediaPOS-dataset/Wikipedia_POS.edgelist",
                  weighted=True)
    wges = scsmatrix2groupedges(wm['group'])
    writegroupedges(wges, "../WikipediaPOS-dataset/Wikipedia_POS.groupedges")

if __name__== "__main__":
    #procHomo()
    #procWiki()
    from os.path import expanduser
    home = expanduser("~")
    path= home+'/Data/wbdata/'
    ifile = path+"usermsg.edgelist"
    sm = loadedge2sm(ifile, csr_matrix, idstartzero=False)