library(quickpsy)
library(dplyr)
library(stringr)

data1 <- read.csv('C:/Users/emma_/OneDrive/Skrivbord/R course/pilot2/pilot1_2022-01-24_14-35-33_P02_data.csv')

data2 <- read.csv('C:/Users/emma_/OneDrive/Skrivbord/R course/pilot2/pilot2_2022-01-24_14-43-41_P02_data.csv')

rbind(data1, data2)

filelist <- list.files(
  'C:/Users/emma_/OneDrive/Skrivbord/R course/pilot2', 
  pattern = 'data', 
  recursive = TRUE,
  full.names = TRUE)


data <- c()

for(currentfile in filelist){
  currentdata <- read.csv(currentfile) %>% 
    mutate(PID = str_extract(currentfile, "_P.*_"))
  #create variable film vs. shaved
  data <- rbind(data, currentdata)
  print(currentfile)
}


fit <- quickpsy(d = data, x = comparison, k = comparison.more.intense)
# add grouping back in (ID and condition)

plot(fit)

library(ggplot2)

ggplot(data = data, mapping = aes(x = comparison, y = comparison.more.intense)) +
            stat_summary(geom = 'point', fun = 'mean') +
  scale_y_continuous(limits = c(0,1))

