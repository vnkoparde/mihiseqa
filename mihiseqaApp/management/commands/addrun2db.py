#!/usr/bin/env python
import os,json,datetime,click
import sys,glob2,itertools
import HTSeq
from django.core.management.base import BaseCommand, CommandError
from mihiseqaApp.models import *

class SSline:

	def getInstrument(self):
		for r in HTSeq.FastqReader(self.r1):
			serialNumber=r.name.split(":")[0]
			try:
				instrument=Instruments.objects.get(serial_number=serialNumber)
			except:
				sys.exit("Instrument with Serial Number "+serialNumber+" not found in the database!")
			break
		return instrument

	def getOperator(self):
		try:
			operator=Operators.objects.get(first_name=self.operatorName)
		except:
			try:
				operator=Operators.objects.get(last_name=self.operatorName)
			except:
				sys.exit("Operator "+self.operatorName+" not found in the database! \nCheck samplesheet in "+self.dir)
		return operator
	
	def parseStats(self):
		if self.r1==self.r2:
			return 1
		for i,r in enumerate([self.r1,self.r2]):
			if r=="":
				continue
			j=i+1
			rsltfile=r+".rslt"
			rsltpfile=r+".rsltp"
			if ( not os.access(rsltfile,os.R_OK) ) or ( not os.access(rsltpfile,os.R_OK) ):
				print rsltfile + " or " + rsltpfile + " not found or not readable!"
				print " Did you run fastq_mihiseqa on all the fastq.gz files????"
				sys.exit()
# parse the rslt file
			rsltfh=open(rsltfile)
			rsltflines=map(lambda x:x.strip().split("\t"),rsltfh.readlines())
			rsltfh.close()
			rsltflines.pop(0)
			for rsltfline in rsltflines:
				tile = int(rsltfline[0])
				if not tile in self.stats:
					self.stats[tile]=dict()
					for k in [1,2]:
						self.stats[tile][k]=dict()
						self.stats[tile][k]['position']=dict()
				self.stats[tile][j]['cumA']=int(rsltfline[1])
				self.stats[tile][j]['cumC']=int(rsltfline[2])
				self.stats[tile][j]['cumG']=int(rsltfline[3])
				self.stats[tile][j]['cumT']=int(rsltfline[4])
				self.stats[tile][j]['cumN']=int(rsltfline[5])
				self.stats[tile][j]['cumARQ']=float(rsltfline[6])
				self.stats[tile][j]['cumMEE']=float(rsltfline[7])
				self.stats[tile][j]['Nreads']=int(rsltfline[8])
				self.stats[tile][j]['Nbases']=int(rsltfline[9])
# parse the rsltp file				
			rsltpfh=open(rsltpfile)
			rsltpflines=map(lambda x:x.strip().split("\t"),rsltpfh.readlines())
			rsltpfh.close()
			rsltpflines.pop(0)
			for rsltpfline in rsltpflines:
				tile = int(rsltpfline[0])
				if not tile in self.stats:
					print "Tile: "+tile+" has no rslt stats loaded!"
					sys.exit()
				pos=int(rsltpfline[1])
				self.stats[tile][j]['position'][pos]=dict()
				for l,b in enumerate(["A", "C", "G", "T", "N"]):
					k=l+2
					cumb="cum"+b
					cumbq="cum"+b+"Q"
					cumbmee="cum"+b+"MEE"
					self.stats[tile][j]['position'][pos][cumb]=int(rsltpfline[k])
					self.stats[tile][j]['position'][pos][cumbq]=int(rsltpfline[k+5])
					self.stats[tile][j]['position'][pos][cumbmee]=float(rsltpfline[k+10])

# 			print r
# 			print json.dumps(self.stats,indent=4)
# 			sys.exit()
							
										
		return 1

	def __init__(self,line,dir):
		self.dir=dir
		self.flowcellid=line[0]
		self.lane=line[1]
		self.sample=line[2]
		self.index=line[4]
		self.operatorName=line[-2]
		self.operator=self.getOperator()
		self.projectName=line[-1]
		self.project,created=Projects.objects.update_or_create(project_name=self.projectName)
		try:
			self.r1=glob2.glob(dir+"/"+self.sample+"*_L00"+self.lane+"*_R1_001.fastq.gz")[0]
		except IndexError:
			self.r1=""
		try:
			self.r2=glob2.glob(dir+"/"+self.sample+"*_L00"+self.lane+"*_R2_001.fastq.gz")[0]
		except IndexError:
			self.r2=""
		if self.r1!="":
			self.instrument=self.getInstrument()
		self.stats=dict()
		self.obj=""
		
	def __str__(self):
		return "Dir: %s \tFlowcell: %s \tLane: %s \tSample: %s \tIndex: %s \tProject: %s" %(self.dir, self.flowcellid, self.lane, self.sample, self.index, self.projectName)
	
		
class Command(BaseCommand):
    help = 'Calculating and inserting run data into the database.'

    def add_arguments(self, parser):
        parser.add_argument('--rundate', nargs='?', type=str, help='Run date in YYMMDD format.', required=True)
        parser.add_argument('--demuxfolder', nargs='?', type=str, help='Full path to demultiplexed folder', required=True)
#         parser.add_argument('--ncpus', nargs='?', type=int, help='Number of cores to use', required=False, default=4)
#         parser.add_argument('--samplesheet', nargs='?', type=str, help='Full path to samplesheet.csv', required=True)

    def handle(self, *args, **options):
    	def parseStats(ss):
    		return ss.parseStats()

# get the date in right format
    	if len(options['rundate']) != 6:
    		sys.exit("Invalid run date entered!")
    	else:
    		runyear=int(options['rundate'][:2])+2000
    		runmonth=int(options['rundate'][2:4])
    		runday=int(options['rundate'][4:])
    	rundate=datetime.date(runyear,runmonth,runday)

# get all the samplesheet csv files and populate ss objects
    	df=options['demuxfolder']
    	if df.endswith("/"):
    		df=df[:-1]
    	ssfiles=glob2.glob(df+"/**/SampleSheet.csv")
    	
    	ss=[]
    	for ssfile in ssfiles:
    		dir=os.path.dirname(ssfile)
    		ssfile_fh=open(ssfile)
    		ssfile_lines=map(lambda x:x.strip().split(","),ssfile_fh.readlines())
    		ssfile_lines.pop(0)
    		ssfile_fh.close()
    		ss.extend(map(lambda x:SSline(x,dir),ssfile_lines))

    	flowcellid=[]
    		
    	for x in ss:
    		flowcellid.append(x.flowcellid)
    	
    	flowcellid=list(set(flowcellid))
    	if len(flowcellid)!=1:
    		sys.exit("Multiple flowcellids found! Possibly data from multiple runs!")
    	else:
    		flowcellid=flowcellid[0]

		run,created=Runs.objects.update_or_create(flowcell_id=flowcellid,
		rundate=rundate,
		operator=ss[0].operator,
		instrument=ss[0].instrument)
		
		for x in ss:
			x.obj,created=SampleSheet.objects.update_or_create(run_id=run,
			lane=x.lane,
			sample=x.sample,
			index1=x.index,
			project=x.project)
			if created==0:
				print "WARNING!!!! Samplesheet object \n"+str(x)+"\nalready in database! Was this run already imported to database before?"
		
		
		with click.progressbar(range(len(ss)),label="Parsing datafiles and updating database..") as bar:
			for xi in bar:
				x=ss[xi]
				x.parseStats()
				for t,tstats in x.stats.iteritems():
					for read12 in [1,2]:
						if not read12 in tstats:
							continue
						rsltobj,created=ReadStatsPerTile.objects.update_or_create(rsl=x.obj,
						tile=t,
						read12=read12,
						cum_a=tstats[read12]['cumA'],
						cum_c=tstats[read12]['cumC'],
						cum_g=tstats[read12]['cumG'],
						cum_t=tstats[read12]['cumT'],
						cum_n=tstats[read12]['cumN'],
						cum_arq=tstats[read12]['cumARQ'],
						cum_mee=tstats[read12]['cumMEE'],
						nreads=tstats[read12]['Nreads'],
						nbases=tstats[read12]['Nbases'])
						for p,pdict in tstats[read12]['position'].iteritems():
							rsltpobj,created=PositionStatsPerTile.objects.update_or_create(rslt=rsltobj,
							position=p,
							cum_a = pdict['cumA'],
							cum_c = pdict['cumC'],
							cum_t = pdict['cumT'],
							cum_g = pdict['cumG'],
							cum_n = pdict['cumN'],
							cum_aq = pdict['cumAQ'],
							cum_cq = pdict['cumCQ'],
							cum_tq = pdict['cumTQ'],
							cum_gq = pdict['cumGQ'],
							cum_nq = pdict['cumNQ'],
							cum_amee = pdict['cumAMEE'],
							cum_cmee = pdict['cumCMEE'],
							cum_tmee = pdict['cumTMEE'],
							cum_gmee = pdict['cumGMEE'],
							cum_nmee = pdict['cumNMEE'])		

			
		
			
