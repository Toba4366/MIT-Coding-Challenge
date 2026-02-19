# Author: Monroe Gamble
# Project: RA research tasks
# Date: 10/08/2019

#** Does a campaign visit by a candidate affect the amount of newspaper coverage the candidate receives? **

##################################################
# Steps
# 1. Genearte Summary statistics 
# 2. Creat Visualization
# 3. Run Simple OLS regression
###################################################

# Load Packages ----------------------------------------
library(tidyverse)
library(reshape2)

# Set Directory ----------------------------------------

setwd('C:/Users/l1jmg03/Dropbox (FRB SF)/TEMP/SIEPR/task1')


date_fix <- function(x){
  as.Date(x, format = "%m/%d/%Y")
}

line_data <- read_csv('visits.csv') %>% 
  mutate(date = date_fix(date))


Bush <-
line_data %>% 
  select(1,4, contains("bush")) %>%
  group_by(countycode) %>%
  #filter(visit_bush == 1) %>%
  melt(. , id.vars=c('date', 'visit_bush', 'countycode')) %>%
  as_tibble()

ggplot(Bush, aes(x=date, y=value, colour = variable)) +
  geom_line() +
  geom_point(aes(y=visit_bush+100), size = 2, shape = 2)


bushreg <- lm(value ~ visit_bush + countycode-1, Bush)
summary(bushreg)



%>%
  group_by(date) %>%
  melt(. , id.vars=c('date')) %>%
  as.tibble()
  
ggplot(plot_line, aes(x=date, y = value, colour = variable)) +
  geom_line()







#################################################################################
# Canidate Visits ----------------------------------------

# Load Data 
raw_data <- read_csv('visits.csv') %>%
  cbind(State = state.name[match(raw_data$state,state.abb)]) %>%
  select(1,2,3, everything()) %>%
  mutate(State = tolower(State))

view <-
raw_data %>% 
  select(-date, -county, -state, -State) %>%
  group_by(countycode) %>%
  summarise_all(funs(sum))

plot_data <- view %>% 
  melt(., id.vars = c('countycode')) %>%
  left_join(unique(raw_data[c(1,2)]), by = 'countycode') %>%
  select(-countycode) %>%
  as.tibble()

ggplot(plot_data, aes(x=county, fill = variable)) +
  geom_bar(aes(y = value), stat = 'identity', position = 'dodge') +
  scale_y_continuous(expand = c(0,0),
                     # labels = scales::percent_format(accuracy = 1), 
                     # breaks = seq(-.55,.55,.1), 
                     #limits = c(0,500)
                     )

# Canidate Mentions by date ----------------------------------------
#Load Data
line_data <- read_csv('visits.csv') %>% 
  mutate(date = date_fix(date))


plot_line <-
  line_data %>% 
  select(4, contains("counts")) %>%
  group_by(date) %>%
  melt(. , id.vars=c('date')) %>%
  as.tibble()

ggplot(plot_line, aes(x=date, y = value, colour = variable)) +
  geom_line()

##########################################################################################

#Counties w/ Multiple Visits on the same day
mutiple_visit <- 
line_data %>%
  select(2:4,contains("visit")) %>%
  mutate(total = visit_bradley + visit_buchanan + visit_bush + visit_cheney + visit_gore) %>%
  select(date, total, county, state, contains("visit")) 

mvisits <-
line_data %>%
  filter(date == "2000-02-10" | date == "2000-10-31") %>% 
  select(date, county, state, contains("bradley"), contains("gore"), contains("bush")) %>%
  mutate(total = visit_bradley  + visit_bush + visit_gore) %>%
  filter(total >1)
  
#filter_all(all_vars(.==1))
################################################

# Count the Mentions by county
  mentions <-
    raw_data %>% 
    select(-date, -county, -state, -State) %>%
    group_by(countycode) %>%
    summarise_all(funs(sum)) %>%
    select(countycode, contains("counts")) %>%
    mutate(mentions = rowSums(.[2:13])) %>%
    select(countycode, mentions) %>%
    left_join(unique(raw_data[c(1:3)]), by = 'countycode') %>%
    arrange(desc(mentions))
  
# Count the Mentions by county
  visits <-
    raw_data %>% 
    select(-date, -county, -state, -State) %>%
    group_by(countycode) %>%
    summarise_all(funs(sum)) %>%
    select(countycode, contains("visit")) %>%
    mutate(visits = rowSums(.[2:7])) %>%
    select(countycode, visits) %>%
    right_join(mentions) %>%
    arrange(desc(visits))
  
  topv <- visits %>% head(10) %>% select(-countycode, -mentions, county, state, visits)
  topm <- mentions %>% head(10) %>% select(-countycode, county, state, mentions)

write.table(topv, "visit_counts.txt")
write.table(topm, "metion_counts.txt")

#######Table 1####################################
# Count the Mentions by candidate
candidate_mentions <-
  line_data %>% 
  select(contains("counts")) %>%
  mutate(bradley = counts_bradley + hcounts_bradley,
         buchanan = counts_buchanan + hcounts_buchanan,
         bush = counts_bush + hcounts_bush,
         cheney = counts_cheney + hcounts_cheney,
         gore = counts_gore + hcounts_gore,
         lieberman = counts_lieberman + hcounts_lieberman
         ) %>%
  # select(bradley, counts_bradley, hcounts_bradley,
  #        buchanan, counts_buchanan, hcounts_buchanan,
  #        bush, counts_bush, hcounts_bush,
  #        cheney, counts_cheney, hcounts_cheney,
  #        gore, counts_gore, hcounts_gore,
  #        lieberman, counts_lieberman, hcounts_lieberman) %>%
  select(bradley, buchanan, bush, cheney, gore, lieberman) %>%
  summarise_all(funs(sum)) %>%
  melt(., value.name = "count") %>%
  arrange(desc(count))

ggplot(candidate_mentions, aes(x=variable, fill = variable)) +
  geom_bar(aes(y = count), stat = 'identity', position = 'dodge')


#####Table 2############################################
# Count Visits Before 2007
candidate_visits <- line_data %>% 
  #filter(date < "2000-11-07") %>% 
  select(contains("visit")) %>%
  summarise_all(funs(sum))
  

# Count the Mentions by candidate before 2007
candidate_mentions <-
  line_data %>% 
  filter(date < "2000-11-07") %>%
  select(contains("counts")) %>%
  mutate(bradley = counts_bradley + hcounts_bradley,
         buchanan = counts_buchanan + hcounts_buchanan,
         bush = counts_bush + hcounts_bush,
         cheney = counts_cheney + hcounts_cheney,
         gore = counts_gore + hcounts_gore,
         lieberman = counts_lieberman + hcounts_lieberman
  ) %>%
  select(bradley, counts_bradley, hcounts_bradley,
         buchanan, counts_buchanan, hcounts_buchanan,
         bush, counts_bush, hcounts_bush,
         cheney, counts_cheney, hcounts_cheney,
         gore, counts_gore, hcounts_gore,
         lieberman, counts_lieberman, hcounts_lieberman) %>%
  #select(bradley, buchanan, bush, cheney, gore, lieberman) %>%
  summarise_all(funs(sum)) %>%
  melt(., value.name = "count") %>%
  arrange(desc(count))

###Pat Buchanon#########################################
vist_totals <-
line_data %>%
  filter(date > "2000-03-09") %>%
  select(contains("visit")) %>% 
  summarise_all(funs(sum)) 
################################################

reduced_data <-
line_data %>%
  filter(date < "2000-11-07") %>%
  select(1:4, contains("bush"), contains("gore")) %>%
  mutate(
    total_bush = counts_bush + hcounts_bush,
    total_gore = counts_gore + hcounts_gore,
    visit_flag = ifelse(visit_gore==1, 1, ifelse(visit_bush==1, 1, 0))
    ) %>%
  select(visit_flag, visit_gore, visit_bush) %>%
  summarise(sum(visit_flag))


write.csv(reduced_data, "reduced_data.csv")

#######################################################
test <-
reduced_data %>%
  filter(date > "2000-08-01" & date < "2000-08-31") %>%
  select( contains("bush"), contains("gore")) %>% 
  summarise_all(funs(sum)) 


##### CREATE A Bar Graog if mentions by month
line_data %>%
  group_by(lubridate::month(date)) %>%
  #filter(date > "2000-08-01" & date < "2000-08-31") %>%
  select(lubridate::month(date), contains("bush"), contains("gore")) %>% 
  summarise_all(funs(sum)) 


  plot_data <- view %>% 
    melt(., id.vars = c('countycode')) %>%
    left_join(unique(raw_data[c(1,2)]), by = 'countycode') %>%
    select(-countycode) %>%
    as.tibble()