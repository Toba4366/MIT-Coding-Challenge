# Author: Monroe Gamble
# Project: RA research tasks
# Date: 10/11/2019

# Load Packages ----------------------------------------
library(tidyverse)
library(reshape2)

# Set Directory ----------------------------------------

setwd('C:/Users/l1jmg03/Dropbox (FRB SF)/TEMP/SIEPR/task2/')

# Load Data
raw_papers <- read.delim("newspapers.txt") %>%
  as_tibble() %>%
  mutate(cnty = as.character(cnty),
         state = as.character(state))

#Find max for each paeper
max_circ <- raw_papers %>% 
  group_by(membernumber) %>%
  summarise(dailycirc = max(dailycirc)) %>%
  mutate(HQ_Flag = 1)

HQ <- left_join(raw_papers, max_circ, by = c("membernumber", "dailycirc")) %>%
  mutate(HQ_Flag = ifelse(HQ_Flag %in% NA, 0, 1),
         HQcounty = ifelse(HQ_Flag %in% 0, NA, cnty),
         HQfp = ifelse(HQ_Flag %in% 1, stcntyfp, NA),
         HQstate = ifelse(HQ_Flag %in% 1, state, NA))

HQ_ID <- HQ[,c('membernumber', 'HQcounty', 'HQfp', 'HQstate')] %>% 
  na.omit

# Get County ID's
County_ID <- raw_papers %>% 
  select(stcntyfp, cnty, state)

data <-
HQ %>% select(-HQcounty, -HQfp, -HQstate) %>% 
  left_join(HQ_ID, by = "membernumber") %>%
  select(stcntyfp_1 = HQfp, cnty_1 = HQcounty, state_1 = HQstate, stcntyfp_2 = cnty, state_2 = state, dailycirc) %>%
  arrange(stcntyfp_1, stcntyfp_2)

write_delim(data, "newspaper_EDIT.txt")
