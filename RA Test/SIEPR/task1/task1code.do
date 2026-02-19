

** Data Setup ************************************************************************
clear
* Set Directory
cd "C:\Users\l1jmg03\Dropbox (FRB SF)\TEMP\SIEPR\task1"
pwd /*Shows the working directory*/

*Load Data
import delimited reduced_data.csv
save "C:\Users\l1jmg03\Dropbox (FRB SF)\TEMP\SIEPR\task1\visits.dta", replace

clear
use "visits.dta"
****************************************************
destring date, replace
gen date2 = date(date, "YMD")
format %td date2

gen dofw = dow(date(date, "YMD"))
gen month = month(date(date, "YMD"))

drop if month == 8

gen gore_total = hcounts_gore + counts_gore
gen bush_total = hcounts_bush + counts_bush

/*
gen visit_flag = 0
replace visit_flag = 1 if visit_gore == 1
replace visit_flag = 1 if visit_bush == 1
*/

reg bush_total visit_bush, r
reg gore_total visit_gore, r

*Panel Data Set
xtset countycode date2


* All Regressions
gen all_mentions = gore_total + bush_total
gen all_hcount = hcounts_gore + hcounts_bush
gen all_counts = counts_gore + counts_bush	

***************************************************************************
*0) ALL REG

eststo clear

eststo All: xtreg all_mentions visit_flag i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

*1) Bush/Gore
eststo Gore: xtreg gore_total visit_gore i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Bush: xtreg bush_total visit_bush i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

*2) Headline/no
eststo Headline: xtreg all_hcount visit_flag i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Intext: xtreg all_counts visit_flag i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

esttab All Headline Intext Gore Bush ///
using "T3. The Effect of Presidential Candiate Visit on Newspaper Coverage.html", html drop(*.date2) r2 replace title(Newspaper Mentions) ///
mtitles("All Mentions" "Headline Mentions" "In-Article" "Al Gore" "George Bush") ///
label s(N r2 county year robust , label("Observations" "R-squared" "County fixed effects" "Time fixed effects"  "Robust standard errors"))

***************************************************************************
*3) Lag

eststo clear

*All
eststo All: xtreg all_mentions visit_flag L7.all_mentions i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

*Candidates
eststo Gore: xtreg gore_total visit_gore L7.gore_total i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Bush: xtreg bush_total visit_bush L7.bush_total i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Headline: xtreg all_hcount visit_flag L7.all_hcount i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Intext: xtreg all_counts visit_flag L7.all_counts i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

esttab All Headline Intext Gore Bush ///
using "T2. The Effect of Presidential Candiate Visit on Newspaper Coverage.html", html drop(*.date2) r2 replace title(Newspaper Mentions 7-day Lag) ///
mtitles("All Mentions" "Headline Mentions" "In-Article" "Al Gore" "George Bush") ///
label s(N r2 county year robust , label("Observations" "R-squared" "County fixed effects" "Time fixed effects"  "Robust standard errors"))

***************************************************************************
*4) Lead 1 day

eststo clear

*All
eststo All: xtreg F.all_mentions visit_flag L7.all_mentions i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

*Candidates
eststo Gore: xtreg F.gore_total visit_gore L7.gore_total i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Bush: xtreg F.bush_total visit_bush L7.bush_total i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Headline: xtreg F.all_hcount visit_flag L7.all_hcount i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

eststo Intext: xtreg F.all_counts visit_flag L7.all_counts i.date2, r fe
estadd local county "yes"
estadd local year "yes"
estadd local robust "yes"

esttab All Headline Intext Gore Bush ///
using "T1. The Effect of Presidential Candiate Visit on Newspaper Coverage.html", html drop(*.date2) r2 replace title(Newspaper Mentions 1-day Lead 7-day Lag) ///
mtitles("All Mentions" "Headline Mentions" "In-Article" "Al Gore" "George Bush") ///
label s(N r2 county year robust , label("Observations" "R-squared" "County fixed effects" "Time fixed effects"  "Robust standard errors"))

***************************************************************************

*5) Impulse
forvalues i = 0/10 {
	foreach x in all_mentions all_hcount all_counts gore_total bush_total {
		gen `x'_`i' = F`i'.`x' - L3.`x'
	}
}


foreach x in all_mentions all_hcount all_counts {
	tempname result_`x'
	postfile `result_`x'' h visit visit_se using result_`x'.dta, replace
	
	forvalues i = 0/10 {
		qui xtreg `x'_`i' visit_flag i.date2, r fe
		post `result_`x'' (`i') (`=_b[visit_flag]') (`=_se[visit_flag]')
	}

	postclose `result_`x''
}

foreach x in gore bush {
	tempname result_`x'_total
	postfile `result_`x'_total' h visit visit_se using result_`x'.dta, replace
	
	forvalues i = 0/10 {
		qui xtreg `x'_total_`i' visit_`x' i.date2, r fe
		post `result_`x'_total' (`i') (`=_b[visit_`x']') (`=_se[visit_`x']')
	}

	postclose `result_`x'_total'
}

foreach x in all_mentions all_hcount all_counts gore bush {
	use result_`x', clear
	gen t = "`x'"
		
* Graph
	gen upper = visit + visit_se
	gen lower = visit - visit_se
	gen upper2 = visit + 2*visit_se
	gen lower2 = visit - 2*visit_se
	
	gen zero = 0
	
	if t == "all_mentions" {
		graph twoway rarea upper2 lower2 h, color(gs14) || rarea upper lower h, color(gs12) || line visit h, color(red) || line zero h, ///
		saving(result_`x', replace) title(Figure 1. All Mentions) leg(lab(1 "2*SE") lab(2 "SE"))
	}
	if t == "all_hcount" {
		graph twoway rarea upper2 lower2 h, color(gs14) || rarea upper lower h, color(gs12) || line visit h, color(red) || line zero h, ///
		saving(result_`x', replace) title(Figure 2. Headlines) leg(lab(1 "2*SE") lab(2 "SE"))
	}
	if t == "all_counts" {
		graph twoway rarea upper2 lower2 h, color(gs14) || rarea upper lower h, color(gs12) || line visit h, color(red) || line zero h, /// 
		saving(result_`x', replace) title(Figure 3. In-Text) leg(lab(1 "2*SE") lab(2 "SE"))
	}
	if t == "gore" {
		graph twoway rarea upper2 lower2 h, color(gs14) || rarea upper lower h, color(gs12) || line visit h, color(red) || line zero h, ///
		saving(result_`x', replace) title(Figure 4. Gore) leg(lab(1 "2*SE") lab(2 "SE"))
	}
	if t == "bush" {
		graph twoway rarea upper2 lower2 h, color(gs14) || rarea upper lower h, color(gs12) || line visit h, color(red) || line zero h, ///
		saving(result_`x', replace) title(Figure 5. Bush) leg(lab(1 "2*SE") lab(2 "SE"))
	}
}

graph combine result_all_mentions.gph result_all_hcount.gph result_all_counts.gph result_gore.gph result_bush.gph
graph export "impulse_results.png", as(png) replace

