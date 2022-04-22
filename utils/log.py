def WriteLog(msg):
    print(msg)
    with open("runlog.log", "a+") as f:
        f.write(msg + "\n")
        f.close()
