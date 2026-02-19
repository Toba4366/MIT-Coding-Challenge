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


plot_line <-
line_data %>% 
  select(4, contains("counts")) %>%
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

