README for visits.dta

The comma-separated file visits.csv contains data on campaign visits and newspaper article counts for US Pres and Vice-Pres candidates in 2000.

There are three main variables: (for each candidate C)

1. visit_C: Equal to 1 if C visited a given county on specific date
2. counts_C: Number of articles where the string "C" appears in the full text of newspapers within a given county and date
3. hcounts_C: Number of articles where the string "C" appears in the headline of newspapers within a given county and date

Descriptor variables include:
1. countycode: Standardized code for counties in the US
2. county: County name
3. state: Abbreviation of US states
4. date: Date in mm/dd/yyyy format

Note that 1,2,3 DO NOT contain all counties (and codes) and states in the US, e.g. if you look at the unique values for states, we only have 22. However, dates are complete.


