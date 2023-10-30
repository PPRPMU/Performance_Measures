# Performance_Measures
Script to summarize high level usage data for PPR facilities

If you run into any errors, try running install_packages.sh

Takes in the program attendance csv file (usually stored on the MyPPR - Documents onedrive folder)

Outputs a csv with the number of unique individuals and unique programs at a facility for each month of a given year
Unique individuals are the maximum number of participants in a program and are assigned to the FIRST month the program appears in the year
Unique programs are the number of programs whose FIRST occurence is in that month

The output csv is suitable (and indeed intended for) uploading to Knack as the Facility Measurements records. 
