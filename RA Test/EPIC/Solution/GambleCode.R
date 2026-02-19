# Author: Monroe Gamble
# EPIC Tasks
# Date: 11/7/2019
# Note: All charts and data manipulations can be found in this script. 
# The code is self contained. I have commeted out the working directory.
#
# Variance decomposition regressions were ran using STATA.
# If you have questions please don't hesitate to contact me at monroe.gamble@gmail.com or 
# by cell phone 816-977-3383.
#
# Thank you!
##########################################################################


##### 2 Data Cleaning ######
# Load Packages -------------------------------------
library(tidyverse)

# Set Directory -------------------------------------
#setwd('C:/Users/l1jmg03/Dropbox (FRB SF)/TEMP/EPIC/')

# Load & Merge Data ---------------------------------

# Rainfall
rain_files <- list.files("Rainfall/", full.names = T)
#load rain data
rain <- lapply(rain_files, function(x) {read_csv(x)})
rain_data <- do.call("rbind", rain) %>% 
  mutate(date2 = as.Date(paste0(year, "-", month, "-", day)),
         date = as.character(date))

# Temperature
temperature_files <- list.files("Temperature/", full.names = T)
# Load temp data
temp <- lapply(temperature_files, function(x) {read_csv(x)})
temp_data <- do.call("rbind", temp) %>%
  mutate(date2 = as.Date(paste0(year, "-", month, "-", day)))

# Merge Temp & Rainfall
data <- left_join(rain_data, temp_data, by = c('latitude', 'longitude', "date2")) %>%
  select(date2, latitude, longitude, rainfall, temperature) #%>% na.omit()

# Crosswalk ---------------------------------
c_walk <- read_csv('Geo/district_crosswalk_small.csv') %>%
  rename(longitude = centroid_longitude, latitude = centroid_latitude)

# Add centroids
joinData <- data %>% fuzzyjoin::geo_left_join(c_walk, by = c("latitude", "longitude"), max_dist = 100, unit = "km")

cdata <-  
  joinData %>% 
    group_by(date2, distname_iaa, stname_iaa) %>%
    summarise(avg_temp = mean(temperature),
              avg_rainfall = mean(rainfall),
              total_rain = sum(rainfall),
              )
    



###### 3 Data Exploration ######

# 1 Timeseries of daily rainfall ----------------------------------
jaipur <- cdata %>% 
  filter(distname_iaa == "jaipur") %>%
  select(-avg_temp, date = date2, avg_rainfall)

# Save Data
write.csv(jaipur %>% select(-total_rain), "1_jaipur.csv", row.names = F)

# Create theme for graph
epic_theme <-
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

# 2,3 Plot Data ---------------------------------
ggplot(data = jaipur, aes(x=date)) +
  geom_point(aes(y=avg_rainfall), color = "blue") +
  scale_x_date(date_breaks = "6 months", 
               date_labels = "%b '%y",
               limits = c(min(jaipur$date)-25, max(jaipur$date)+25),
               expand = c(0,0)) +
  scale_y_continuous(expand = c(0,0), limits = c(0,150), breaks = seq(0,150, 25)) +
  labs(x = "Date", y = "Average Rainfall", title = "Average Daily Rainfall in Jaipur") +
  epic_theme() +
  geom_vline(xintercept = c(as.Date('2009-06-01'), as.Date('2010-06-01'), 
                            as.Date('2011-06-01'), as.Date('2012-06-01'),
                            as.Date('2013-06-01')), color = 'green') +
  geom_vline(xintercept = c(as.Date('2009-10-01'), as.Date('2010-10-01'), 
                            as.Date('2011-10-01'), as.Date('2012-10-01'),
                            as.Date('2013-10-01')), color = 'red')

ggsave("3_Jaipur_Monsoon.pdf", dpi = 1080)


jaipur %>% 
  group_by(lubridate::year(date)) %>%
  filter(median != 0) %>%
  summarise(median = median(avg_rainfall)) %>%

# 4 Create Data for Table -----------------------------------------
temp_table <- joinData %>% 
  group_by(stname_iaa, lubridate::year(date2)) %>%
  na.omit() %>%
  summarise(avgYearly_Temp = mean(temperature))

# Save Table
write.csv(temp_table, "4_AvgYearlyTemp.csv", row.names = F)


jaipur %>% filter(avg_rainfall == max(avg_rainfall) | total_rain == max(total_rain))


India <- map_data("world") %>% filter(region == "India")

ggplot() +
  geom_polygon(data = India, aes(x=long, y = lat, group = group), fill = 'light grey') +
  coord_fixed(1) +
  geom_segment(color = "red") +
  geom_point(data = test, aes(x = longitude.x, y = latitude.x))

