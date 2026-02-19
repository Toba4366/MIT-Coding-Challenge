# Author: Monroe Gamble
# Opportnity Insights Tasks
# Date: 11/5/2019
# Note: All charts and data manipulations can be found in this script. 
# This charts outputs Figures 1-4.
# The code is self contained. I have commeted out the working directory.
#
# Variance decomposition regressions were ran using STATA.
# If you have questions please don't hesitate to contact me at monroe.gamble@gmail.com or 
# by cell phone 816-977-3383.
#
# Thank you!
##########################################################################



# Load Packages ------------------------
library(tidyverse)
library(reshape2)
library(foreign)

# Set Directory ------------------------
# setwd('C:/Users/l1jmg03/Dropbox (FRB SF)/TEMP/OppTask')



############ Queston 1 ###################

# Load Data ------------------------
outcomes <- read.csv("national_percentile_outcomes.csv") %>% 
  as_tibble()

# Create Chart Theme ------------------------
chetty_theme <-
  function() {
    theme(
      panel.background = element_blank(),
      panel.grid.major.y = element_line(colour = '#e5e5e5'),
      panel.grid.major.x = element_blank(),
      text = element_text(color = 'black', size = 14),
      axis.text = element_text(color = 'black', size = 12),
      axis.ticks.y = element_blank(),
      plot.title = element_text(hjust = 0.5),
      axis.title = element_text(size = 12),
      axis.line.x.bottom = element_line(colour = 'black'),
      legend.title = element_text(size = 12),
      legend.key=element_blank()
    )
  }

# Figure 1. Plot Mean Child Income Rank vs. Parent Income Rank ------------------------

ggplot(data = outcomes, aes(x=par_pctile)) +
  geom_point(aes(y=kfr_stycz_black_pooled, color = "kfr_stycz_black_pooled"), size = 1.6) +
  geom_smooth(aes(y = kfr_stycz_black_pooled, color = "kfr_stycz_black_pooled"), method = lm, se = FALSE) +
  
  geom_point(aes(y=kfr_stycz_white_pooled, color = "kfr_stycz_white_pooled"), size = 1.6) +
  geom_smooth(aes(y = kfr_stycz_white_pooled, color = "kfr_stycz_white_pooled"), method = lm, se = FALSE) +
  
  geom_point(aes(y=kfr_black_pooled, color = "kfr_black_pooled"), size = 1.6) +
  geom_smooth(aes(y = kfr_black_pooled, color = "kfr_black_pooled"), method = lm, se = FALSE) +
  
  geom_point(aes(y=kfr_white_pooled,color = "kfr_white_pooled"), size = 1.6) +
  geom_smooth(aes(y = kfr_white_pooled, color = "kfr_white_pooled"), method = lm, se = FALSE) +
  
  scale_color_manual(
    "Groups by race and commuting zone", 
    labels = c( "White Changed Commuting Zone", "Black Changed Commuting Zone", 
                "Black Same Commuting Zone", "White Same Commuting Zone"),
    breaks = c("kfr_black_pooled", "kfr_white_pooled", "kfr_stycz_black_pooled", "kfr_stycz_white_pooled"),
    values = c("red", '#8baf3e', '#2e5e8b', '#fcc62d')
  ) +
  scale_x_continuous(expand = c(0,0), limits = c(-1, 101)) +
  scale_y_continuous(limits = c(.2, .75), labels = function(x) x*100, breaks = seq(0,1,.05)) +
  labs(y = "Mean Child Rank in National Income Distribution \n", x= "\nParent Rank in National Income Distribution", 
       title = "Figure 1. Mean Child Income Rank vs. Parent Income Rank") +
  chetty_theme()

  
# Save plot
ggsave("Fig1_ChildRank_ParentRank.png", dpi = 1080)


# Differential Rank (Compute difference for mover's) -----------------------------
differential_outcomes <-
  outcomes %>%
    mutate(black_difference = kfr_black_pooled - kfr_stycz_black_pooled, 
           white_difference = kfr_white_pooled - kfr_stycz_white_pooled ) %>%
    select(par_pctile, black_difference, white_difference)

# Figure 2. Changed Community Zone Income Differential ---------------

ggplot(data = differential_outcomes, aes(x=par_pctile)) +
  geom_point(aes(y=white_difference, color = "white_difference"), size = 1.6) +
  geom_smooth(aes(y = white_difference, color = "white_difference"), method = lm, se = FALSE) +
  
  geom_point(aes(y=black_difference, color = "black_difference"), size = 1.6) +
  geom_smooth(aes(y = black_difference, color = "black_difference"), method = lm, se = FALSE) +
  
  scale_color_manual(
    "Mover's Outcome\nDifferential by Race", 
    labels = c( "White", "Black"),
    breaks = c("white_difference", "black_difference"),
    values = c('#2e5e8b', '#8baf3e')
  ) +
  scale_x_continuous(expand = c(0,0), limits = c(-1, 101)) +
  scale_y_continuous(labels = function(x) scales::percent(x, accuracy = 1)) +
  labs(y = "Difference in Mover's Rank in \nNational Income Distribution \n", 
       x= "\n Parent Rank in National Income Distribution", 
       title = "Figure 2. Mover's Income Differential vs Parent Income Rank") +
  chetty_theme()

#Save
ggsave("Fig2_Income_differential.png", dpi = 1080)





############ Queston 2 ---------------

# Load Data
tract_outcome <- 
  read_csv('tract_outcomes.csv') 

# Create Indicator variables & Filter for females
tract_indicator <-
  tract_outcome %>% 
  melt(id.vars = c("county_full", "tract", "cz", "czname"), 
       value.name = "percent", variable.name = "group", na.rm = T) %>% 
  as_tibble() %>%
  mutate(household = ifelse(grepl("kfr", group) == T, 1, 0),
         individual = ifelse(grepl("kir", group) == T, 1, 0),
         teenbirth = ifelse(grepl("teen", group) == T, 1, 0),
         female = ifelse(grepl("female", group) == T, 1, 0),
  ) %>%
  filter(female == 1, grepl("kir", group) | grepl("kfr", group) | grepl("teen", group)) %>%
  select(-female) %>%
  group_by(cz, tract, county_full)

# Output data to STATA
write.dta(tract_indicator, 'tract_outcomesSTATA.dta')

# Regressions run in STATA, code provided in the file  ----------------------

# Create Data Frame (values sum to 1)  ----------------------
indiv <- data.frame(tract = .022938, county = .194702, cz = .782360) 
house <- data.frame(tract = .042876, county = .008586, cz = .948538)  
teen <-  data.frame(tract = .01194, county = .12558, cz = .86248)    

# Merge Data Frames
var_df <- 
  rbind("Individual Income" = indiv, "Household income" = house, "Teenbirth Income" = teen) %>%
  rownames_to_column("group")

# Organize data for stacked bar chart
var_melt <- melt(var_df, id.vars = c("group"), value.name = 'percent') %>% 
  group_by(group)

# Figure 3. Geographi Decompostion Stacked Bar Chart ----------------------------
ggplot(var_melt, aes(fill = variable, x= group, y=percent)) +
  geom_bar(position = "stack", stat = "identity") +
  scale_fill_manual(" ",
    labels = c( "Tract", "County", "Commuting zone"),
    #breaks = c("white_difference", "black_difference", 'adf'),
    values = c('#fcc62d', '#2e5e8b', '#8baf3e')
  ) +
  scale_y_continuous(labels = function(x) scales::percent(x, accuracy = 1), expand = c(0,0)) +
  labs(title = "Figure 3. Geographic Decomposition of Variance in Upward Mobility",
       x="", y = "Percentage of Signal Variance") +
  chetty_theme()

ggsave("Fig3_Variance.png", dpi = 1080)


############ Queston 3 ###################

# Teacher Distribution--------------------------
teacher_dist <- read_csv("teacher_effects.csv")

ggplot(teacher_dist, aes(x = observed_teacher_effect)) +
  geom_vline(aes(xintercept = mean(observed_teacher_effect)), color = '#2e5e8b', linetype = 
               'dashed', size = 1.6) +
  geom_density(color = 'red', fill = "#e5e5e5", alpha = .4) +
  theme_classic() +
  scale_y_continuous(expand = c(0,0)) + #labels = function(x) scales::percent(x, accuracy = 1)) +
  scale_x_continuous(expand = c(0,0)) +
  labs(
    y = 'Density',
    x = 'Observed Teacher Effect',
    title = "Figure 4. Distribution of Teacher Effects"
  ) +
  theme(
    #plot.caption = element_text(hjust = -.001, margin =  margin(0, 0, 2, 0)),
    panel.background = element_blank(),
    panel.grid.major.y = element_line(colour = '#e5e5e5'),
    panel.grid.major.x = element_blank(),
    text = element_text(color = 'black', size = 14),
    axis.text = element_text(color = 'black', size = 12),
    axis.ticks.y = element_blank(),
    plot.subtitle = element_text(margin = margin(0, 0, 15, 0), hjust = -.05, size = 12),
    plot.title = element_text(hjust = 0.5),
    axis.line.x.bottom = element_line(colour = 'black'),
    legend.key=element_blank()
  )


ggsave("Fig4_distribution.png", dpi = 1080)

mean(teacher_dist$observed_teacher_effect)
median(teacher_dist$observed_teacher_effect)
sd(teacher_dist$observed_teacher_effect)
min(teacher_dist$observed_teacher_effect)
max(teacher_dist$observed_teacher_effect)


