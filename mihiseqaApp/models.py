# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Instruments(models.Model):
    instrument_id = models.AutoField(primary_key=True)
    instrument_name = models.CharField(max_length=20)
    serial_number = models.CharField(unique=True, max_length=10)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'instruments'
    
    def __unicode__(self):
    	return "%d|%s|%s" % (self.instrument_id,self.serial_number,self.instrument_name)


class Operators(models.Model):
    operator_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = 'operators'
    
    def __unicode__(self):
    	return "%d|%s|%s" % (self.operator_id,self.first_name,self.last_name)


class PrincipalInvestigators(models.Model):
    pi_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    department = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = 'principal_investigators'
    
    def __unicode__(self):
    	return "%d|%s|%s" % (self.pi_id,self.first_name,self.last_name)


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=40)
    description = models.TextField(blank=True, null=True)
    pi = models.ForeignKey(PrincipalInvestigators, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'projects'
    
    def __unicode__(self):
    	return "%d|%s" % (self.project_id,self.project_name)


class Runs(models.Model):
    run_id = models.AutoField(primary_key=True)
    flowcell_id = models.CharField(unique=True, max_length=10)
    rundate = models.DateField()
    operator = models.ForeignKey(Operators, on_delete=models.CASCADE)#    operator = models.ForeignKey(Operators, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    instrument = models.ForeignKey(Instruments, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'runs'


class SampleSheet(models.Model):
    rsl_id = models.AutoField(primary_key=True)
    run = models.ForeignKey(Runs, on_delete=models.CASCADE)    
    lane = models.IntegerField()
    sample = models.CharField(max_length=20)
    index1 = models.CharField(max_length=15)
    index2 = models.CharField(max_length=15, blank=True, null=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    
    def __unicode__(self):
    	return "Run=%d|Lane=%d|Sample=%s|Project=%s"%(self.run.run_id,self.lane,self.sample,self.project.project_name)
    
    class Meta:
        db_table = 'sample_sheet'
        unique_together = ('run','project','sample','index1')


class ReadStatsPerTile(models.Model):
	read_choices=((1,'read1'),(2,'read2'))
	rslt_id = models.AutoField(primary_key=True)
	rsl = models.ForeignKey(SampleSheet, on_delete=models.CASCADE)    
	tile = models.PositiveSmallIntegerField()
	read12 = models.PositiveSmallIntegerField(choices=read_choices,default=1) # specify if read 1 or read 2
	cum_a = models.BigIntegerField()
	cum_c = models.BigIntegerField()
	cum_t = models.BigIntegerField()
	cum_g = models.BigIntegerField()
	cum_n = models.BigIntegerField()
	cum_arq = models.FloatField()
	cum_mee = models.FloatField()
	nreads = models.BigIntegerField()
	nbases = models.BigIntegerField()
	
	class Meta:
			db_table = 'read_stats_per_tile'


class PositionStatsPerTile(models.Model):
    rsltp_id = models.AutoField(primary_key=True)
    rslt = models.ForeignKey(ReadStatsPerTile, on_delete=models.CASCADE)    
    position = models.PositiveSmallIntegerField()
    cum_a = models.BigIntegerField()
    cum_c = models.BigIntegerField()
    cum_t = models.BigIntegerField()
    cum_g = models.BigIntegerField()
    cum_n = models.BigIntegerField()
    cum_aq = models.BigIntegerField()
    cum_cq = models.BigIntegerField()
    cum_tq = models.BigIntegerField()
    cum_gq = models.BigIntegerField()
    cum_nq = models.BigIntegerField()
    cum_amee = models.FloatField(default=0)
    cum_cmee = models.FloatField(default=0)
    cum_tmee = models.FloatField(default=0)
    cum_gmee = models.FloatField(default=0)
    cum_nmee = models.FloatField(default=0)
    

    class Meta:
        db_table = 'position_stats_per_tile'

