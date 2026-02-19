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



read.csv('visits.csv') %>% 













# Load Data ----------------------------------------
raw_data <- read.csv('visits.csv') %>%
  cbind(State = state.name[match(raw_data$state,state.abb)]) %>%
  select(1,2,3, everything()) %>%
  mutate(State = tolower(State)) %>%
  as.tibble()

# Canidate Visits ----------------------------------------

# Create Visits Dataframe
visits <-
  raw_data %>% 
  group_by(countycode, state) %>% 
    summarise(BradleyVisit = sum(visit_bradley), 
              BuchananV = sum(visit_buchanan),
              BushVisit = sum(visit_bush),
              CheneyVisit = sum(visit_cheney),
              GoreVisit = sum(visit_gore),
              LiebermanVisit = sum(visit_lieberman)
    ) %>% 
  left_join(unique(raw_data[c(1,2)]), by = 'countycode') 


view <-
raw_data %>% as.tibble() %>%
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


##########################################################################################










ggplot(plot_data, aes(x=county, fill = variable)) +
  geom_line(aes(y = value)) +
  scale_y_continuous(expand = c(0,0),
                     # labels = scales::percent_format(accuracy = 1), 
                     # breaks = seq(-.55,.55,.1), 
                     limits = c(0,500))


###############################
visit_plot <- visits %>% 
  ungroup() %>% 
  select(-countycode) %>% 
  group_by(county, state) %>%
  melt(., id.vars = c('county', 'state')) %>% 
  ungroup() %>%
  as.tibble() %>%
  filter(value > 0)

ggplot(visit_plot, aes(x=county, fill = variable)) +
  geom_bar(aes(y = value), stat = 'identity', position = 'dodge') +
  scale_y_continuous(expand = c(0,0),
                     #labels = scales::percent_format(accuracy = 1), 
                     #breaks = seq(-.55,.55,.1), 
                     limits = c(0,400))




#+
  scale_fill_manual('Fund type and strategy',
                    labels = c("Passive ETF", "Passive MF", "Active ETF", "Active MF", "SPY ETF"),
                    values=c(col1, col4, col3, col2, 'red')) +
?melt







max(visits$Bradley)

duplicated(visits$county)

# Visiualize Data ----------------------------------------






# Visiualize Data ----------------------------------------

# Map visits 
border <- map_data("usa")
US <- map_data("state")
county <- map_data("county")

#***Excludes Washington D.C.***
test <- raw_data[rowSums(is.na(raw_data)) > 0,] 
#US %>% filter(region %in% 'washington dc')

# Keep only visited states
visited_states <- unique(raw_data$State) %>% tolower() %>% na.omit
states <- subset(US, region %in% visited_states)
counties <- subset(county, region %in% visited_states)

# Keep Visited Counties
data_map <- 
  visits %>%
  #raw_data[,c("countycode", "county", "State")] %>% 
  mutate(State = tolower(State)) %>% 
  rename(countycode = countycode, subregion = county, region = State)

visited_counties <- visits %>% right_join(counties) %>% group_by(counties)


#rm(test, visited_states, US, county)

#map_us <-
  ggplot() + 
    geom_polygon(data = border, aes(x = long, y = lat, group = group), fill = NA, color = 'black') +
    geom_polygon(data = states, aes(x = long, y = lat, group = group), fill = NA, color = 'black') +
    geom_polygon(data = counties, aes(x = long, y = lat, group = group), fill = NA, color = 'black') +
    coord_fixed(1)
  
