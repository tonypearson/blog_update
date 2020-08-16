# DataFile -- Python class for data files
import datetime
import os
import re
import sys

DATADIR = "data"
COMMITFILE = "master_commits.txt"
BRANCHFILE = "all_branches.txt"

class DataFile():
    """
    Class to manage intermediate text files

    from TextFile import TextFile
    """

    def __init__(self, logger, filename):
        """ Set file name """
        self.logger = logger
        os.makedirs(DATADIR, exist_ok=True)   # store in sub-directory
        self.filename = os.path.join(DATADIR, filename)
        self.readmsg = 'Reading file:'
        self.writemsg = 'Writing file:'
        self.lines = []
        return None

    def read(self):
        """ Read file into lines array """
        self.lines = []
        if self.readmsg:
            print(self.readmsg, self.filename)
        with open(self.filename, 'r') as in_file:
            lines = in_file.read().splitlines()
            for line in lines:
                self.read_parse(line)
                line = in_file.readline()
        return self


    def read_parse(self, line):
        self.lines.append(line)
        return self

    def add_line(self, line):
        self.lines.append(line)
        return self

    def write(self):
        """ Write lines array to file """
        with open(self.filename, 'w') as out_file:
            for line in self.lines:
                print(line, file=out_file)
        if self.writemsg:
            print(self.writemsg, self.filename)
        return self

class CommitFile(DataFile):
    """ List of Github commits """

    def __init__(self, logger):
        super().__init__(logger, COMMITFILE)
        self.main = []
        self.data = {}
        self.issueRegex = re.compile(r'([@#][0-9]+)')
        self.masterRegex = re.compile(r'(\d*) (\w*) (.*)')
        self.outForm = '{:04d} {} {}'
        self.onelineForm = "{:.7} {}"
        return None


    def read_parse(self, line):
        mo = self.masterRegex.search(line)
        if mo:
            num, sha, msg = int(mo.group(1)), mo.group(2), mo.group(3)
            self.main.insert(0, sha)
            self.data[sha] = msg
            line = self.outForm.format(num, sha, msg)
            super().read_parse(line)
        else:
            self.logger.info('MALFORMED: {}'.format(line))
        return self


    def add_commit(self, sha, msg):
        self.main.insert(0, sha)   # main[0] is first commit
        msg = msg.replace('♥', '')
        self.data[sha] = msg
        self.logger.info(self.oneline(sha, msg))
        return self
        

    def oneline(self, sha, msg):
        single = "{:.7} {}".format(sha, msg)
        return single


    def position(self, sha):
        pos = self.main.index(sha)
        return pos
      

    def write(self):
        self.lines = []
        for n, sha in enumerate(self.main):
            line = self.outForm.format(n, sha, self.data[sha])
            self.lines.insert(0, line)
        super().write()
        return self


class BranchFile(DataFile):
    """ List of Github branches """

    def __init__(self, logger):
        super().__init__(logger, BRANCHFILE)
        self.branches = []
        self.data = {}
        self.bRegex = re.compile(r'Root=(\d*)-(\w*) Stop=(\d*)-(\w*) (.*)')
        self.bForm = "Root={:04d}-{} Stop={:04d}-{} {}"
        return None


    def add_branch(self, rpos, root, spos, stop, branchname):
        bline = self.bForm.format(rpos, root, spos, stop, branchname)
        self.branches.append(branchname)
        self.update_branch(rpos, root, spos, stop, branchname)
        self.add_line(bline)
        return self


    def update_branch(self, rpos, root, spos, stop, branchname):
        self.data[branchname] = {'rpos': rpos,
                                'root': root,
                                'spos': spos,
                                'stop': stop,
                                }
        return self


    def read_parse(self, line):
        mo = self.bRegex.search(line)
        rpos = mo.group(1)
        root = mo.group(2)
        spos = mo.group(3)
        stop = mo.group(4)
        branchname = mo.group(5)
        self.branches.append(branchname)
        self.update_branch(rpos, root, spos, stop, branchname)
        self.logger.info(line)
        return self


class IssueFile(DataFile):
    """ List of Github issues and comments """

    def __init__(self, logger, branchname):
        filename = "{}.md".format(branchname)
        super().__init__(logger, filename)
        self.gen_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.headForm = "# Release Notes"
        self.dateForm = "### Date: {}"
        self.branchStem = "## Branch: "
        self.issueForm = '* Issue:{:04d} ({}) {}'
        return None

    def add_header(self):
        # Header showing Selected branch
        iline = self.headForm
        self.add_line(iline)
        # These notes were generated on this date
        iline = self.dateForm.format(self.gen_date)
        self.add_line(iline)
        return self


if __name__ == "__main__":
    print('Testing: ', sys.argv[0])

    logger = None
    filename = 'test_datafile.txt'
    ofile = DataFile(logger, filename)
    ofile.add_line('This class simplifies the processing of text files')
    ofile.add_line('Especially useful if you are writing scripts that')
    ofile.add_line('Create reports, *.html, or markdown *.md format')
    ofile.write() 

    ifile = DataFile(logger, filename)
    ifile.read()
    for line in ifile.lines:
        print(line)

    print('Congratulations')


