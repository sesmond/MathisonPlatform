import os
import time
from logging.handlers import TimedRotatingFileHandler

'''
    多进程下TimedRotatingFileHandler有丢日志的问题，重新实现一个类
    参考：https://www.jianshu.com/p/d615bf01e37b 方案1
    此方案在大并发下，仍然会丢失日志，大概1%左右，但是已经解决了之前的严重丢失日志的问题，
    考虑到午夜00:00时候，日志量不是很大，可以接受这个方案，
    另外，在不切换的情况下，多大日志并发都不会丢失。
'''


class SafeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))

        # 不再删除切换过去的已经存在文件ocr.2020.4.25.log，防止别人先切了，你把人家的日志改删掉了
        # if os.path.exists(dfn):
        #    os.remove(dfn)

        # 如果目标文件ocr.2020.4.25.log不存在，并且基准文件ocr.log还在呢，就把ocr.log改名成ocr.2020.4.25.log
        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            self.rotate(self.baseFilename, dfn)

        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
