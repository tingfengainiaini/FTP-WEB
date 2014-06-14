#import sys
import os,glob,time
import string
import socket
ftproot="/home/wbq/projects/ftpweb"
#faitdir="-rw-rw-rw- 1 user group 1024 Jun 12 14:13 aaa.txt\r\n/-rw-rw-rw- 1 user group 1048576 May 12 16:12 bbb.txt\r\n";
#faitData="1234567890"*102+"12\r\n"
class FtpServ:#difine a ftp server class    
    def do_user(self):
        print self.cmd[5:]
        if(self.cmd[5:]=='haha\r\n'):
            self.userok=1
            self.connect.send("331 user name ok,need password.\r\n")
        else:
            self.connect.send("430 user name error.\r\n")
    def do_pass(self):
        print self.cmd[5:]
        if(self.cmd[5:]=='hehe\r\n'):
            if(self.userok==1):
                self.logined=1
                self.connect.send("230 User logged in, proceed.\r\n")
            else:
                self.connect.send("530 who are you\r\n")
        else:
            self.connect.send("430 pass word error.\r\n")
    def do_mode(self):
        if(self.comd[5]=='S'):
            self.connect.send("200 stream mode is ok\r\n")
        else:
            self.connect.send("500 only stream mode is support\r\n")
               
    def do_pwd(self):
        #show user the directory here
        self.connect.send("257 /"//" is current directory.\r\n")
        return
    def do_noop(self):
        self.connect.send("200 ok\r\n")
        return
    def do_type(self):
        print self.cmd[5:6]
        if(string.lower(self.cmd[5:6])=='i'):
            self.connect.send('200 type set to I.\r\n')
        elif(string.lower(self.cmd[5:6])=='a'):
            self.connect.send('200 type set to A.\r\n')
        else :
            self.connect.send('500 parm error.\r\n')
    def do_quit(self):
        self.connect.send("221 Goodbye.\r\n")
    def do_feat(self):
        return
    def do_port(self):
        client=string.split(self.cmd[5:],',')
        self.dataClient='.'.join(client[0:4])
        self.dataPort=int(client[4])*256+int(client[5])
        print "clinet ask data connect to ", self.dataClient,":",self.dataPort
        self.connect.send("200 PORT Command successful.\r\n")
        return
    def do_pasv(self):
        self.connect.send("500 passive mode not supported.\r\n")
#---------------------------------------------------
    def do_list(self):
        if(self.dataClient!=''):
            self.connect.send("150 Opening data connection.\r\n")
            self.datasocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #prepare for data trans
            self.datasocket.connect((self.dataClient,self.dataPort))
            filedir=""
            for i in self.fileList.keys() :
                filedir=filedir+self.fileList
            self.datasocket.send(filedir)
            #self.datasocket.send(faitdir)
            self.datasocket.close()
            self.connect.send("226 Transfer complete.\r\n")
            print "dir data sended."
        else:
            self.connect.send("503 on port specify\r\n")
        return
#--------------------------------------------------
    def do_retr(self):
        if self.cmd[5:-2] in self.fileList.keys():
            print "asking for ",self.cmd[5:-2]
            file=open(ftproot+"//"+self.cmd[5:-2],"rb")
            self.connect.send("150 Opening data connection.\r\n")
            self.datasocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #prepare for data trans
            self.datasocket.connect((self.dataClient,self.dataPort))
            #self.datasocket.send(faitData)
            data=file.read(1024)
            
            while(data!=""):
                self.datasocket.send(data)
                #print data
                data=file.read(1024)
            self.datasocket.close()
            self.connect.send("226 Transfer complete.\r\n")
        else:
            self.connect.send("503 no such file\r\n")
        return
#---------------------------------------------------------------------
    def do_stor(self):
        filename=self.cmd[5:-2]
        newfile=open(filename,'w')
        self.connect.send("150 Opening data connection.\r\n")
        self.datasocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #prepare for data trans
        self.datasocket.connect((self.dataClient,self.dataPort))
        while(1):
            buf=self.datasocket.recv(1400)
            if(len(buf)!=0):
                newfile.write(buf)
            else:
                self.datasocket.close()
                break
        newfile.close()
        self.connect.send("226 Transfer complete.\r\n")
        print filename," received."
        self.getFileList()
        return
#---------------------------------------------------------------------
    def getFileList(self):
        self.fileList={}
        tempList=glob.glob(ftproot+'//*.*')
        print tempList
        for i in tempList:
            file=glob.glob(i)[0]
            self.fileList[file[7:]]="-rw-rw-rw- 1 user group "+str(os.stat(file)[6])+" "+time.strftime("%m %d %H:%M",time.gmtime(os.stat(file)[8]))+" "+file[7:]+"\r\n"
        print self.fileList
        
#---------------------------------------------------------------------
    def __init__(self):
        self.commands={
              'USER':self.do_user,
              'PASS':self.do_pass,
              'LIST':self.do_list,
              'PORT':self.do_port,
              'RETR':self.do_retr,
              'STOR':self.do_stor,
              'XPWD':self.do_pwd,
              'PWD':self.do_pwd,
              'PASV':self.do_pasv,
              'FEAT':self.do_feat,
              'TYPE':self.do_type,
              'NOOP':self.do_noop,
              'MODE':self.do_mode,
              'QUIT':self.do_quit
              
              }
        self.cmd=""
        self.myHost=''
        self.myPort=21
        self.dataClient=''
        self.dataPort=25
        self.userok=0
        self.logined=0
        self.connect=None
        self.dataconnect=None
        self.fileList=[]
        self.getFileList()
        socket.setdefaulttimeout(5000);
        self.sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockobj.bind((self.myHost, self.myPort)) # bind it to server port number
        
        
        
    def loop(self):
        self.sockobj.listen(5) # listen, allow 5 pending connects
        while(1):
            print "starting ftp service"
            self.connect,self.addr=self.sockobj.accept()
            print 'Server connected by',self.addr
            self.connect.send("220 Wellcom to wbq's ftp.\r\n")
            while(self.connect.):
                self.cmd=self.connect.recv(256)
                print 'recv: ',self.cmd
                if not self.cmd:
                    break
                else:
                    if(self.cmd[0:4] in self.commands.keys()):
                        print "handle command ",self.cmd[0:4]
                        self.commands[self.cmd[0:4]]()
                        if(self.cmd[0:4]=="QUIT"):
                            print "client left!"
                            break
                    else:
                        self.connect.send("500 unkonw command.\r\n")
            print 'closing connection',self.addr
            self.connect.close()
            
if __name__ == "__main__":
    print "\n-----------------------ftp & webserver-------------------------"
    print "\n-----------------------13S103020wbq-------------------------"
    ftpserver=FtpServ()
    ftpserver.loop()
