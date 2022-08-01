#!/usr/bin/python
#========================================
#  Written By : Artur Kujawa
#  Contact :   zigfi7@gmail.com
#========================================

import sys,telnetlib,re,getopt

class bcolors:
  RESET     = "\033[0m"                   # Remove all atributes
  NOCOLOR   = "\033[39m"                  # Default foreground color 
  BLACK     = "\033[30m"                  # Black
  DRED      = "\033[31m"                  # Red
  DGREEN    = "\033[32m"                  # Green
  ORANGE    = "\033[33m"                  # Yellow
  BLUE      = "\033[34m"                  # Blue
  VIOLET    = "\033[35m"                  # Magenta
  CYAN      = "\033[36m"                  # Cyan
  LGRAY     = "\033[37m"                  # Light gray  
  DGRAY     = "\033[90m"                  # Dark gray 
  RED       = "\033[91m"                  # Light red 
  GREEN     = "\033[92m"                  # Light green  
  YELLOW    = "\033[93m"                  # Light yellow  
  DBLUE     = "\033[94m"                  # Light blue
  PINK      = "\033[95m"                  # Light magenta
  LBLUE     = "\033[96m"                  # Light cyan
  WHITE     = "\033[97m"                  # White

myname=__file__.split('/')[-1]
argv = sys.argv[1:]

ip=''
level = 1
crosses = ''
status= ''
helpmsg=myname,'-i <IP Address> -x <list of crosspoints> -l <level>'

try:
  opts, args = getopt.getopt(argv,"h:i:l:x:",["ip=","level=","cross=","help="])
except getopt.GetoptError:
  print (helpmsg)
  sys.exit(2)
for opt, arg in opts:
  if opt in ("-h", "--help"):
    print (helpmsg)
    sys.exit()
  elif opt in ("-i", "--ip"):
    ip = arg
  elif opt in ['-l', '--level']:
    try:
        level = int(arg)
    except ValueError:
      print ('L require integer value')
      sys.exit(2)
  elif opt in ("-x", "--cross"):
    crosses = arg.split(',')

if ip == "":                     # If there is no IP there is no point to continue.
  print (helpmsg)
  sys.exit(2)

#---------------------------------------------------------------------------------

timeout=5                           # Default timeout
user = "leitch"                     # Default username
password = "leitchadmin"            # Default passwords

try:
    tn = telnetlib.Telnet(ip)  # Try to connect
except OSError:
  print ('Host',ip,'is not responing.')
  sys.exit(2)

tn.read_until(b"login: ", timeout)
tn.write(user.encode('ascii') + b"\n\r")
tn.read_until(b"password: ", timeout)
tn.write(password.encode('ascii') + b"\n\r")
tn.read_until(b'.\r\n\r\n\r\n\r\n>', timeout)

# ------ connected ------------
print ( f"{bcolors.GREEN}Connected with ip:"+f"{bcolors.YELLOW} " + ip+f"{bcolors.NOCOLOR} ")
print ( f"{bcolors.LBLUE}Setting :{bcolors.NOCOLOR} " +str(crosses))

def panacea_cmd(commands,level=1):
  lev="l "+str(level)
  tn.write(lev.encode('ascii') + b"\r\n")
  tn.read_until(b'\r\n>', timeout)
  for cross in commands:
    command="x "+cross.replace("x", " ")
    tn.write(command.encode('ascii')+b"\r" )
    tn.read_until(b'\r\n>', timeout)

  tn.write(b"\n\r")
  tn.read_until(b'\r\n>', timeout)
  tn.write(b"r\n\r")                                        # read status
  status=str(tn.read_until(b"\r\n>", timeout).decode('ascii'))
  return status

def panacea_read(sts):
  stats=[]
  stsu=sts.strip('\r\n').split('Level')
  stsu.pop(0)                             #first split will be always empty
  for i in stsu:
    stat={}
    level   = int(i.split(':')[0])
    crosses = i.split(':')[1].replace(">", "")
    print(f"{bcolors.ORANGE}Level:"+f"{bcolors.YELLOW} "+str(level)+f"{bcolors.NOCOLOR}")
    crosses="".join(crosses.split()).replace(" ", "")
    cross_list = list(filter(None, crosses.split(';')))
    for xy in cross_list:
      x=int(xy.split(',')[0])
      y=int(xy.split(',')[1].replace('-----','0'))
      print (x,' <-- ',y)
      stat.update({x:y})
    stats.append(stat)
  print (f"{bcolors.DGREEN}"+str(stats)+f"{bcolors.NOCOLOR}")

status=panacea_cmd(crosses)
panacea_read(status)

tn.write(b"exit\n\r")       # close connection
tn.read_all()


