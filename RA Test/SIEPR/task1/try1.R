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

# Load Data ----------------------------------------
raw_data <- read.csv('visits.csv') %>%
  cbind(State = state.name[match(raw_data$state,state.abb)]) %>%
  select(1,2,3, State, everything()) %>%
  mutate(State = tolower(State)) %>%
  as.tibble()

# Canidate Visits ----------------------------------------

# Create Visits Dataframe
visits <-
  raw_data %>% 
  group_by(countycode) %>% 
    summarise(Bradley = sum(visit_bradley), 
              Buchanan = sum(visit_buchanan),
              Bush = sum(visit_bush),
              Cheney = sum(visit_cheney),
              Gore = sum(visit_gore),
              Lieberman = sum(visit_lieberman)
    ) %>% 
  left_join(unique(raw_data[c(1,2)]), by = 'countycode')












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
  
