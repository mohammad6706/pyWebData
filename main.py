import datetime
import time
import threading
from exportWeb import exportWeb


def openFile(info, typ):
    import tkinter
    from tkinter import filedialog

    tkinter.Tk().withdraw()

    folder_path = filedialog.askopenfilenames(title=info, filetypes=[
        ("", typ)
    ])
    return folder_path[0]


def getDataFile():
    with open(openFile('Select your text file', '.txt'), 'r', encoding='utf-8') as file:
        s = file.read().split('\n')
        file.close()
        a = []
        n = len(s)//5
        while len(s) > n:
            a.append(s[:n])
            del s[:n]
        if len(s) < n:
            a.append(s)
        return a


def exportWebData(tUrl, tCount):
    for u in tUrl:
        exportWeb(u, tCount)


if __name__ == '__main__':
    dataFile = getDataFile()
    counter = 0
    for url in dataFile:
        counter += len(url)
        exportWebData(url, counter)
        t = threading.Thread(target=exportWebData, args=(url, counter))
        t.start()
        count = threading.active_count()
        if count >= 4:
            for i in range(1, count+1):
                t.join()
            time.sleep(3)
