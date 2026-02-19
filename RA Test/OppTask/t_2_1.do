			
			
			

** Data Setup ************************************************************************

clear
* Set Directory
cd "C:\Users\l1jmg03\Dropbox (FRB SF)\TEMP\Opptask"
pwd /*Shows the working directory*/

*Load Data
use "tract_outcomesSTATA.dta"

*Regressions**********************************************
gen cz_r2 = .
gen county_r2 = .
gen tract_r2 = .
 
gen full_model_r2 = .

gen  value = .
gen value1 = .
gen value2 = .
gen value3 = .


local xvars i.individual i.household i.teenbirth

reg percent percent county_full tract `xvars'
local full_r2 = e(r2)

foreach x of local xvars{

	*County
	eststo: reg percent county_full `x', r
	local county_r2 = e(r2)

	*Commuting Zone
	eststo: reg percent cz `x', r
	local cz_r2 = e(r2) 

	*Tract
	eststo: reg percent tract `x', r
	local tract_r2 = e(r2) 


	local value  =  `full_r2'
	local value1 =  `full_r2' - `county_r2'
	local value2 =  `full_r2' - `cz_r2'
	local value3 =  `full_r2' - `tract_r2'

	display "Varaince all = `value' group `x'"
	display "Variance contribution of cz = `value2' group `x'"
	display "Variance contribution of county = `value1' group `x'"
	display "Variance contribution of tract = `value3' group `x'"
	
	esttab ///
	using "T_`xvars'.html", html r2 replace title(Group_`xvars')

}

/*
local xvars x1 x2 x3 x4 // etc.
regress y `xvars'
local full_model_r2 = e(r2)
gen byte include = e(sample)

foreach x of local xvars {
    local short_list: subinstr local xvars "`x'" ""
    regress y `short_list' if include
    display "Variance contribution of `x': =`full_model_r2' - e(r2)"
}
*/
