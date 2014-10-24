import sys
import math
import glob
import subprocess
import numpy
from threading import Thread

TOTAL_RUN = 20
THREAD_COUNT = 2

ROW = 12
COL = 0
data = []
mean_data = []
stdev = []


def getReports(experiment_number, start):
    for i in range(TOTAL_RUN / THREAD_COUNT):
        start_time = float(( start + i )/ (100.0 / TOTAL_RUN))
        end_time = start_time + 10
        subprocess.check_output(("java Experiment" + experiment_number + " " + str(start_time) + " " + str(end_time)).split())

def read_into_data(filename, i):
    global data
    file = open (filename, "r")
    lines = file.readlines()
    file_data = []
    for row in range(ROW):
        col_data = lines[row].split(" ")[:COL]
        col_data = [ float(x) for x in col_data ]
        file_data.append(col_data)
    data.append(file_data)
    file.close()
    subprocess.check_output(("rm " + filename).split())

def calculate():
    global mean_data, stdev
    mean_data = numpy.zeros(shape=(ROW,COL))
    stdev = numpy.zeros(shape=(ROW, COL))
    for i in xrange(TOTAL_RUN):
        for j in xrange(ROW):
            for k in xrange(COL):
                mean_data[j][k] += data[i][j][k]
    for j in xrange(ROW):
        for k in xrange(COL):
            mean_data[j][k] = float(mean_data[j][k] / TOTAL_RUN)

    for i in xrange(TOTAL_RUN):
        for j in xrange(ROW):
            for k in xrange(COL):
                stdev[j][k] = stdev[j][k] + math.pow(data[i][j][k] - mean_data[j][k], 2)

    for j in xrange(ROW):
        for k in xrange(COL):
            stdev[j][k] = math.sqrt(stdev[j][k] / TOTAL_RUN)


def clean_up():
    global data
    data = []
    mean_data = []
    stdev = []

def write_to_disk(experiment_number, param):
    filename = "report/REPORT%s_%s" % (experiment_number, param)
    file = open (filename, "w")
    file.write("Total run: " + str(TOTAL_RUN) + " \n")
    for l in mean_data:
        l = [str(x) for x in l]
        file.write(" ".join(l) + "\n")

    file.write("\n")
    for l in stdev:
        l = [str(x) for x in l]
        file.write(" ".join(l) + "\n")

    file.close()




def getResult(experiment_number):
    global COL
    params = ["delay", "droprate", "throughput"]
    for param in params:
        for i in range(TOTAL_RUN):
            start_time = i / (100.0 / TOTAL_RUN);
            if experiment_number == "1":
                combinations = [""]
                COL = 4
            elif experiment_number == "2":
                combinations = ["NewReno_Reno", "NewReno_Vegas", "Reno_Reno", "Vegas_Vegas"]
                COL = 2

            for j in range(len(combinations)):
                if experiment_number == "1":
                    suffix = str(start_time)
                elif experiment_number == "2":
                    suffix = combinations[j] + "_" + str(start_time)
                filename = "report/Report%s_%s_%s" % (experiment_number, param, suffix)
                read_into_data(filename, i)
        # print data
        calculate()
        write_to_disk(experiment_number, param)
        clean_up()
    return 

def main(argv):
    threads = []
    for i in range(THREAD_COUNT):
        thread = Thread(target = getReports, args = (argv[0], TOTAL_RUN / THREAD_COUNT * i))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    
    getResult(argv[0]);

if __name__ == "__main__":
    main(sys.argv[1:])