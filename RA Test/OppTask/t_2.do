
** Data Setup ************************************************************************

/*
clear
* Set Directory
cd "C:\Users\l1jmg03\Dropbox (FRB SF)\TEMP\Opptask"
pwd /*Shows the working directory*/

*Load Data
use "tract_outcomesSTATA.dta"

drop if female == 0

*eststo clear
*Fixed Effects Regressions**********************************************

*Panel Data Set
xtset tract
eststo household: xtreg percent household, r fe
*/

forvalue i = 1/2 {
	forvalue j = 0/2 {

		clear
		* Set Directory
		cd "C:\Users\l1jmg03\Dropbox (FRB SF)\TEMP\Opptask"
		pwd /*Shows the working directory*/
		
		*Load Data
		use "tract_outcomesSTATA.dta"

		drop if female == 0


			if `i' == 0 {
				xtset tract
			}
			if `i' == 1 {
				xtset cz
			}
			if `i' == 2 {
				xtset county_full
			}

			preserve
			
			*regress percent tract
			*local full_model_r2 = e(r2)
			
			
			if `j'== 0 & `i' != 0 {
				drop if individual != 1
				
				*Fixed Effects Regressions
				eststo: xtreg percent tract, r fe
				
				*display "Variance contribution of `i': =`full_model_r2' - e(r2)"
				
				esttab ///
				using "T_`i'_`j'.html", html r2 replace title(Funds Panel_`i'_Group_`j') ///

			}
			
			if `j' == 1 & `i' != 0 {
				drop if household != 1
				
				*Fixed Effects Regressions
				eststo: xtreg percent tract, r fe
				
				esttab ///
				using "T_`i'_`j'.html", html r2 replace title(Funds Panel_`i'_Group_`j') ///

			}
			if `j' == 2 & `i' != 0 {
				drop if teenbirth != 1
				
				*Fixed Effects Regressions
				
				
				
				
				eststo: xtreg percent tract, r fe
				
				esttab ///
				using "T_`i'_`j'.html", html r2 replace title(Funds Panel_`i'_Group_`j') ///
			
			}
			
			restore
			eststo clear
		
		}
		

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
