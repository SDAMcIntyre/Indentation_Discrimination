library(quickpsy)
library(dplyr)
library(stringr)

# data1 <- read.csv('C:/Users/emma_/OneDrive/Skrivbord/R course/pilot2/pilot1_2022-01-24_14-35-33_P02_data.csv')
# 
# data2 <- read.csv('C:/Users/emma_/OneDrive/Skrivbord/R course/pilot2/pilot2_2022-01-24_14-43-41_P02_data.csv')
# 
# rbind(data1, data2)

filelist <- list.files(
  #'C:/Users/emma_/OneDrive/Skrivbord/R course/pilot2', 
  '/Users/sarmc72/Library/CloudStorage/OneDrive-Linköpingsuniversitet/projects - in progress/Skin imaging/Data Pilot Indentation Discrimination',
  pattern = 'data', 
  recursive = TRUE,
  full.names = TRUE)


data <- c()

for(currentfile in filelist){
  # which one are we up to
  print(currentfile)
  # extract info from filename
  extracted.PID <- str_extract(currentfile, "_P.*_") %>% str_remove_all('_')
  extracted.condition <- str_extract(currentfile, "shaved") 
  if (is.na(extracted.condition)) {extracted.condition <- "film"}
  # read data file and add columns with extracted info
  currentdata <- read.csv(currentfile) %>% 
    mutate(PID = extracted.PID,
           condition = extracted.condition,
           filename = currentfile)
  # add the new data to the end of the data frame
  data <- rbind(data, currentdata)
  rm(currentdata)
}


fit <- quickpsy(
  d = data, 
  x = comparison, 
  k = comparison.more.intense,
  grouping = .(condition, PID),
  log = FALSE,
  fun = cum_normal_fun,
  B = 100,
  ci = 0.95
  )
# add grouping back in (ID and condition)

plot(fit)

library(ggplot2)

ggplot(data = data, mapping = aes(x = comparison, y = comparison.more.intense)) +
            stat_summary(geom = 'point', fun = 'mean') +
  scale_y_continuous(limits = c(0,1))

