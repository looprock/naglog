#!/usr/bin/env python
# Version: 0.1
import os, time, os.path, stat, MySQLdb
#TESTDEGBU import os, time, os.path, stat, rrdtool, MySQLdb

# the current time in common format: i.e.  Fri, 10 Jul 2009 15:04:01 PDT
recdate = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(time.time()))
# the nagios status file
#TESTDEGBU nagiosstatus = "/var/log/nagios/status.dat"
nagiosstatus = "./status.dat"
# current time in epoch format, needed for the rrd graphs
udtime = int(time.time())
# is logging enabled? 'T' for 'True' or 'F' for 'False'
logging = "F"

# is debugging enabled? 'T' for 'True' or 'F' for 'False', overrides logging
# True = output only goes to stdout, not logged or rrd inputted
# THIS SHOULD BE 'F' for prod!
debug = "T"

# database setup
# db_host = "localhost"
# db_username = "data_collector"
# db_password = "O9Nnj@ftw"
# db_name = "Test_Results"
# conn = MySQLdb.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
#if debug == "F":
#   curs = conn.cursor()

# where you want you rrd files to live
dbdir = "/usr/local/nagios/nagiosgraph/rrd/custom/"
# where you want your status files to live (will go away with the DB backend)
#TESTDEGBU statdir = "/var/www/html/status/"
statdir = "./"
# your log file if you're writing to it
#TESTDEGBU logfile = "/var/log/nagios/naglog.log"
logfile = "./naglog.log"

# this maps all the nagios service values by line number, so we can reference them more easily
nagiosmap = {
        'host_name' : 1,
        'service_description' : 2, 
        'modified_attributes' : 3, 
        'check_command' : 4, 
        'event_handler' : 5, 
        'has_been_checked' : 6,  
        'should_be_scheduled' : 7,
        'check_execution_time' : 8,
        'check_latency' : 9,
        'check_type' : 10,
        'current_state' : 11,
        'last_hard_state' : 12,
        'current_attempt' : 13,
        'max_attempts' : 14,
        'state_type' : 15,
        'last_state_change' : 16,
        'last_hard_state_change' : 17,
        'last_time_ok' : 18,
        'last_time_warning' : 19,
        'last_time_unknown' : 20,
        'last_time_critical' : 21,
        'plugin_output' : 22,
        'performance_data' : 23,
        'last_check' : 24,
        'next_check' : 25,
        'current_notification_number' : 26,
        'last_notification' : 27,
        'next_notification' : 28, 
        'no_more_notifications' : 29,
        'notifications_enabled' : 30,
        'active_checks_enabled' : 31,
        'passive_checks_enabled' : 32,
        'event_handler_enabled' : 33,
        'problem_has_been_acknowledged' : 34,
        'acknowledgement_type' : 35,
        'flap_detection_enabled' : 36,
        'process_performance_data' : 37,
        'obsess_over_service' : 38,
        'last_update' : 39,
        'is_flapping' : 40,
        'percent_state_change' : 41,
        'scheduled_downtime_depth' :42 
}

# just a file name munge for the rrd file
def printsuffix(name):
    return "_" + name + "___" + name + ".rrd"

# outputs unique elements in a single dimentional list
def unique(seq):
   # order preserving
   checked = []
   for e in seq:
       if e not in checked:
           checked.append(e)
   return checked

# returns all values where [0] matches a key in a list of lists
def searchlist(list, key):
    values = []
    for item in list:
      if item[0] == key:
        values.append(item[1])
    if debug == "N":
       print "FUNCTION: searchlist - values:"
       print values
    return values

# returns a list of unique keys for the above
def getservices(list):
  newlist = []
  for content in list:
      newlist.append(content[0])
  newlist = unique(newlist)
  return newlist

# generates a dictionary of keys and a lits of their values
def servicedict(list):
  newlist = getservices(list)
  results = {}
  for item in newlist:
      results[item] = searchlist(list, item)
  if debug == "N":
     print "FUNCTION: servicedict - results:"
     print results
  return results

# go through a list. If a value is NOT one, add one to the returned total
def listyesno(list):
  total = 0
  for val in list:
      if type(val) == str:
	strprts = val.split(".")
	if len(strprts) > 1:
	  #val = strprts[0]
	  val = float(val)
	else:
	  val = val
      val = int(val)
      if val != 0:
         val = 1
      total = total + val
  return total

# go through a list and return a sum of all the items
def listtotal(list):
  total = 0
  for val in list:
      if type(val) == str:
        strprts = val.split(".")
        if len(strprts) > 1:
          #val = strprts[0]
          val = float(val)
        else:
          val = val
      val = int(val)
      total = total + int(val)
  return total

# read the nagios status data and create a list of lists containing a service and it's value
def parsenag(statusfile, line):
  file = open(statusfile,'r').read()
  data = []
  services = file.split("}")
  for item in services:
    breakdown = item.split("{")
    if breakdown[0].strip() == 'service':
      lines = breakdown[1].split("\n")
      service = lines[1].split("=")[1].strip()
      status = lines[nagiosmap[line]].split("=")[1].strip()
      # this is where mysql insert should go
      checkname = lines[nagiosmap['check_command']].split("=")[1].strip()
      if debug == "F": 
         f = open(statdir + service + "-" + checkname + "-" + line + ".stat", 'w')
         f.write(recdate + "|" + status)
         f.close()
         #curs.execute('insert Nagios_Results (Service_Name, Test_Name, Result_Type, Result_Value, Result_Time) values (%s, %s, %s, %s, %s)', (service, checkname, line, status, str(udtime)))
         #conn.commit()
      else:
         print "FUNCTION: parsenag_mysqlstuff - service: " + service + ", checkname: " + checkname + ", information: " + line + ", status: " + status + ", time: " + str(udtime)
      data.append([service, status])
  if debug == "N":
     print "FUNCTION: parsenag - data:"
     print data
  return data

# the meat: process the data and write the results to logs, status files, and the rrd databases
def processdata(line, name, restype):
  if debug == "F":
    if logging == "T":
       log = open(logfile, 'a')
  datatype = parsenag(nagiosstatus, line)

  # we want to capture ALL information here
  allresults = []
  for entries in datatype:
     allresults.append(entries[1])
  if restype == "total":
     fullresult = listtotal(allresults)
  else:
     fullresult = listyesno(allresults)
  # write a status file for the homepage (will go away with database addition 
  if debug == "F":
    f = open(statdir + "all-" + name + ".stat", 'w')
    f.write(recdate + "|" + str(fullresult))
    f.close()
    # if the rrd database doesn't exist, we should make one first
    if not os.path.exists(dbdir + "all" + printsuffix(name)):
       rrdtool.create(dbdir + "all" + printsuffix(name), 'DS:' + name.capitalize() + ':GAUGE:600:0:U', 'RRA:AVERAGE:0.5:1:600', 'RRA:AVERAGE:0.5:6:700', 'RRA:AVERAGE:0.5:24:775', 'RRA:AVERAGE:0.5:288:797')
    # update the rrd database with ALL data
    rrdtool.update(dbdir + "all" + printsuffix(name), '%d:%d' % (udtime,fullresult))
    # write to the logfile if enabled
    # mysql stuff for ALL data goes here
    if logging == "T":
       log.write(recdate + ":" + dbdir + "all" + printsuffix(name) + ":values:" + str(udtime) + ":" + str(fullresult) + "\n")
  else:
    print recdate + "|" + str(fullresult)
    print recdate + ":" + dbdir + "all" + printsuffix(name) + ":values:" + str(udtime) + ":" + str(fullresult)
    print "FUNCTION: processdata_all_mysqlstuff - service: all, checkname: all, information: " + name + ", status: " + str(fullresult) + ", time: " + str(udtime)
  # actually we don't need this at all since we can get this value from the DB instead now
  #DEBUGDISABLED: if debug == "F":
  #curs.execute('insert Nagios_Results (Service_Name, Test_Name, Result_Type, Result_Value, Result_Time) values (%s, %s, %s, %s, %s)', ("all", "all", name, str(fullresult), str(udtime)))
  #conn.commit()
  
  # now we capture individual service org data
  serviceresults = servicedict(datatype)
  if debug == "T": 
     print "FUNCTION: processdata - serviceresults:"
     print serviceresults
  for service in getservices(datatype):
    if debug == "T":
       print "Processing line: " + str(line) + ", name: " + name + ", restype: " + restype + ", for service: " + service
    if restype == "total":
      endresult = listtotal(serviceresults[service])
    else:
      endresult = listyesno(serviceresults[service])
    # write a status file for the homepage (will go away with database addition 
    if debug == "F":
       f = open(statdir + service + "-" + name + ".stat", 'w')
       f.write(recdate + "|" + str(endresult))
       f.close()
       # again, make the rrd file if none exist
       if not os.path.exists(dbdir + service + printsuffix(name)):
        rrdtool.create(dbdir + service + printsuffix(name), 'DS:' + name.capitalize() + ':GAUGE:600:0:U', 'RRA:AVERAGE:0.5:1:600', 'RRA:AVERAGE:0.5:6:700', 'RRA:AVERAGE:0.5:24:775', 'RRA:AVERAGE:0.5:288:797')
       # update rrd data
       rrdtool.update(dbdir + service + printsuffix(name), '%d:%d' % (udtime,endresult))
       # write to the logfile if enabled
       if logging == "T":
          log.write(recdate + ":" + dbdir + service + printsuffix(name) + ":values:" + str(udtime) + ":" + str(endresult) + "\n")
    else:
       print recdate + "|" + str(endresult)
       print recdate + ":" + dbdir + service + printsuffix(name) + ":values:" + str(udtime) + ":" + str(endresult)
       print "FUNCTION: processdata_service_mysqlstuff - service: " + service + ", checkname: all, information: " + name + ", status: " + str(endresult) + ", time: " + str(udtime)
    #if debug == "F":
    #   curs.execute('insert Nagios_Results (Service_Name, Test_Name, Result_Type, Result_Value, Result_Time) values (%s, %s, %s, %s, %s)', (service, "all", name, str(endresult), str(udtime)))
    #   conn.commit()
  # now we're done with all logging
  if debug == "F":
     log.close()

# processdata arguments:
# 1. line from the service entry you want to graph (mapped via the nagiosmap dictionary)
# 2. name of the graph. This translates to a filename as well as graph title in nagiosgraph
# 3. how you want the numbers accounted for. So far there are two:
#    a. yesno - if any of the data in a list is NOT A 0, add 1 to the total. This is how we tally errors. 
#	The state is returned as a value between 0 and 3, but we only care that if it's not a 0, there's an error and we add 1.
#    b. total - this adds all the values in a list

servicereturn = processdata("current_state", 'failures', 'yesno')
servicereturn = processdata("check_execution_time", 'exectime', 'total')

# now we're done with all logging and the DB
#conn.close()
