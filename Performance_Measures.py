import numpy as np
import pandas as pd
from datetime import datetime as dt

#1: clean the file by pulling out the program name into sep fields
#TODO 2: match with program file based on ProgID for:
#         amenitites
#3: add fiscal year/quarter info
#4: summarize the numbers and export

#don't touch this
pd.set_option("display.max_colwidth", 1000)

#the program attendance file is a mess
#many rows aren't formatted properly, and the whole dataset is
#decidedly un-tidy. Not good for analysis.
#this cleans it up 
def clean_DF(df,sep='   '):
    vect = df['Program'].copy()
    #make new columns
    df.insert(3,"Description",'nan',False)
    df.insert(4,"Facilitator",'nan',False)
    df.insert(5,"Gender",'nan',False)
    df.insert(6,"AgeGroup",'nan',False)
    df.insert(7,"ProgramID",'nan',False)
    df.insert(8,'amenityName','nan',False)
    df.insert(9,'amenityID','nan',False)
    for i in range(len(vect)):
        #split the string based on sep
        currStr = vect[i]
        #sometimes the seperator is 4-5 white spaces instead of 3
        #No, I don't know how or why
        #I think deep in the dataset there are even more whacky formatting errors this won't catch,
        #so be wary of going too far back in time (2023-2024 are for sure good)
        currStr.replace('      ','   ')
        currStr.replace('    ','   ')
        splitStr = currStr.split(sep)
        #seperate age and unique id
        age = splitStr[4]
        tmp = age.replace('(','')
        cleanAge = tmp.replace(')','')
        justAge = cleanAge.split('#')[0]
        key = cleanAge.split('#')[1]
        #assign values to new columns
        df.iloc[i,3]=splitStr[1]
        df.iloc[i,4]=splitStr[2]
        df.iloc[i,5]=splitStr[3]
        df.iloc[i,6]=justAge
        df.iloc[i,2]=splitStr[0]
        df.iloc[i,7]=key
    return df

#TODO: get this working
#assigns ammenities to each program
#again, the formatting of the data file is a big problem
def prog_match(attdf,progdf):
    uniqueKeys = np.unique(attdf['ProgramID'])
    for key in uniqueKeys:
        ammenity = progdf['Amenities'][progdf['ProgramID']==int(key)].to_string()
        ammenity = ammenity.split('    ')[1]
        print(key)
        if len(ammenity)!=0:
            ammenity = ammenity.replace(')','')
            if '\n' in ammenity:
                print(ammenity)
                ammenityList = ''
                ammenityIDList = ''
                tmp = ammenity.splitlines()
                print(len(tmp[1]))
                for i in tmp:
                    ammenityList = ammenityList+'; '+i.split('(#')[0]
                    ammenityIDList = ammenityIDList+'; '+i.split('(#')[1]
                ammenityName = ammenityList[1:]
                ammenityID = ammenityIDList[1:]
            else:
                ammenityName = ammenity.split('(#')[0]
                ammenityID = ammenity.split('(#')[1]
            ind = np.where(attdf['ProgramID']==key)[0]
            print(ammenityName)
            print(ammenityID)
            attdf.iloc[ind,8]=ammenityName
            attdf.iloc[ind,9]=ammenityID
    return attdf

#assign year and fiscal quarter to each row of the dataframe
#Q3 jan 1 - mar 31
#Q4 apr 1 - jun 30
#Q1 July 1 - Sept 30
#Q2 Oct 1 - Dec 31
##def fiscal_quarters(attdf):
##    #preset and name the new columns
##    attdf.insert(14,"FiscalQuarter",'nan',False)
##    attdf.insert(15,"FiscalYear",0,False)
##    for i in range(len(attdf)):
##        #timestamp the attendance date
##        tstmp = dt.strptime(str(attdf['AttendanceWeekDate'][i]),'%m/%d/%Y')
##        date = tstmp.strftime('%Y%m%d')
##        #extract year information
##        year = int(date[0:4])
##        #convert date to an int
##        date = int(date)
##        #create arrays for the range of dates in each fiscal quarter
##        yearFactor = year*10000
##        Q3 = np.arange(yearFactor+101,yearFactor+331)
##        Q4 = np.arange(yearFactor+401,yearFactor+630)
##        Q1 = np.arange(yearFactor+701,yearFactor+930)
##        Q2 = np.arange(yearFactor+1001,yearFactor+1231)
##        #assign quarter and covert year if neccessary before assignment
##        if date in Q3:
##            quarter = 'Q3'
##            attdf.iloc[i,15] = year
##        elif date in Q4:
##            quarter = 'Q4'
##            attdf.iloc[i,15] = year
##        elif date in Q1:
##            quarter = 'Q1'
##            attdf.iloc[i,15] = year+1 
##        elif date in Q2:
##            quarter = 'Q2'
##            attdf.iloc[i,15] = year+1
##        attdf.iloc[i,14] = quarter
##    return attdf

#assign year and month of attendance
def month_and_year(attdf):
    #preset and name the new columns
    attdf.insert(14,"Month",0,False)
    attdf.insert(15,"Year",0,False)
    for i in range(len(attdf)):
        #timestamp the attendance date
        tstmp = dt.strptime(str(attdf['AttendanceWeekDate'][i]),'%m/%d/%Y')
        date = tstmp.strftime('%Y%m%d')
        #extract year and month information
        year = int(date[0:4])
        month = int(date[4:6])
        #assign month and year
        attdf.iloc[i,15] = year
        attdf.iloc[i,14] = month
    return attdf

#create the performance measures we want for each fiscal quarter at each facility
#(unique participants and unique programs)
def summary_stats(attdf,year):
    #define the columns of the output dataframe
    returnDF = pd.DataFrame(columns=['Facility', 'Year', 'Month',
                                     'UniqueIndividuals','UniquePrograms'])
    #get the nan values to the right datatype
    attdf['Facility'] = attdf['Facility'].replace(np.nan,'nan')
    #loop for facilities
    for ifac in np.unique(attdf['Facility']):
        #find the entries for the facility we're working with
        facilityFilteredDF = attdf[attdf['Facility']==ifac]
        #find the entries for the fiscal year we want (calculated in fiscal_quarters)
        yearFilteredDF = facilityFilteredDF[facilityFilteredDF['Year']==year]
        #get a list of all the fiscal quarters in the df
        months = np.unique(yearFilteredDF['Month'])
        #set the out variables to 0 so we can add them in the next loop
        numUniqueIndividuals = np.zeros((12,))
        #get list of all programs (program IDs) in the data set 
        progList = np.unique(yearFilteredDF['ProgramID'])
        numUniquePrograms = np.zeros((12,))
        #loop through programs (program IDs) to count number of individuals
        for iprog in progList:
            #get the entries for the program we're working on
            programFilteredDF = yearFilteredDF[yearFilteredDF['ProgramID']==iprog].copy()
            #find the FIRST month a program appear in within a year
            sortedDF = programFilteredDF.sort_values('AttendanceWeekDate',ignore_index=True)
            mo = sortedDF['Month'][0]
            #get the maximum number of individuals that a program has in attendance for the ENTIRE year
            maxIndividuals = np.max(sortedDF['UniqueIndividualCount'])
            #add the previous step to the total participants in a quarter thus far
            #also assigns the quarterly information (as a variable name rather than a variable)
            #note that this will result in cases where the max from the previous step might be in a different quarter
            #than the one it is assigned to
            #We do this because the PROGRAM is reported in the first quarter is appears, so the max has to go with it,
            #even if its in another quarter
            #this step also assigns adds one to the program count for the first quarter the program appears
            numUniqueIndividuals[mo-1]=numUniqueIndividuals[mo-1]+maxIndividuals
            numUniquePrograms[mo-1] = numUniquePrograms[mo-1] + 1
        #now loop through the quarters and assign the out variables
        #for each facility, there will be a max of 4 quarters (although there may be less)
        #each quarter at each facility will end up being represented by one row (nice and tidy)
        for iq in months:
            #assigns the data to the new row
            newRow = pd.DataFrame({'Facility':ifac,
                                   'Year':year,
                                   'Month':iq,
                                   'UniqueIndividuals':numUniqueIndividuals[iq-1],
                                   'UniquePrograms':numUniquePrograms[iq-1],},
                                  index=[0])
            #adds the row to the output dataframe
            returnDF = pd.concat([newRow,returnDF.loc[:]]).reset_index(drop=True)
    return returnDF
            
#driver code
print("please type the file path to the data files on your machine (on PC replace \ with /):")
fpath = input()
attFname = fpath+"/programattendance.csv"
progFname = fpath+"/program.csv"
print("please type the calendar year you want to data for:")
year = input()
year = int(year)
programattendance = pd.read_csv(attFname)
program = pd.read_csv(progFname)
programattendance = clean_DF(programattendance[:][0:12000])
#programattendance = prog_match(programattendance,program)
#programattendance = fiscal_quarters(programattendance)
programattendance = month_and_year(programattendance)
summaryDF = summary_stats(programattendance,year)
summaryDF.to_csv(fpath+'/PerformanceMeasures.csv')
print("PerformanceMeasures.csv saved to "+fpath)






