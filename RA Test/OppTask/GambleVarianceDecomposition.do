
** Data Setup ************************************************************************


clear
* Set Directory
cd "C:\Users\l1jmg03\Dropbox (FRB SF)\TEMP\Opptask"
pwd /*Shows the working directory*/

*Load Data
use "tract_outcomesSTATA.dta"

*eststo clear
*Fixed Effects Regressions**********************************************


gen cz_r2 = .
gen county_r2 = .
gen tract_r2 = .
 
gen full_model_r2 = .


gen  value = .
gen value1 = .
gen value2 = .
gen value3 = .

gen perc1 = .
gen perc2 = .
gen perc3 = .

forvalue j = 0/2 {
						
			preserve
			
			if `j'== 0 {
				drop if individual != 1
			}
			
			if `j' == 1 {
				drop if household != 1
			}
			if `j' == 2 {
				drop if teenbirth != 1
			}

			
			*Regressions
			
			*County
			eststo: reg percent tract, r
			local tract_r2 = e(r2)
			
			*Commuting Zone
			eststo: reg percent tract county_full, r
			local county_r2 = e(r2) 
			
			*Tract
			eststo: reg percent tract county_full cz, r
			local cz_r2 = e(r2) 
			
			local value1 =  `tract_r2'
			local value2 =  `county_r2' - `tract_r2'
			local value3 =  `cz_r2' - `county_r2'  
			
			local value  =  `value1' + `value2' + `value3'
			
			
			local perc1 = `value1' / `value'
			local perc2 = `value2' / `value'
			local perc3 = `value3' / `value'
			
			display "Varaince all = `value' group`j'"
			display "Variance contribution of tract = `perc1' group`j'"
			display "Variance contribution of county = `perc2' group`j'"
			display "Variance contribution of cz = `perc3' group`j'"
			esttab ///
			using "T_`j'.html", html r2 replace title(Group_`j')

						
			restore
			eststo clear
			
	}
