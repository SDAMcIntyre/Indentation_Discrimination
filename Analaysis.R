library(quickpsy)
library(dplyr)
library(stringr)
library(ggplot2)

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

for(currentfile in filelist) {
  # which one are we up to
  print(currentfile)
  # extract info from filename
  extracted.PID <- str_extract(currentfile, "(P02|PEK|PMMM|PSM)")
  extracted.condition <- str_extract(currentfile, "shaved") 
  if (is.na(extracted.condition)) {
    extracted.condition <- "film"
    }
  # read data file and add columns with extracted info
  currentdata <- read.csv(currentfile) %>% 
    mutate(PID = extracted.PID,
           condition = extracted.condition,
           filename = currentfile)
  # add the new data to the end of the data frame
  data <- rbind(data, currentdata)
  rm(currentdata)
}

# simple figure to check the data
ggplot(data, aes(x = comparison, y = comparison.more.intense, colour = condition)) +
  stat_summary(geom = 'point', fun = 'mean') +
  facet_wrap(. ~ PID, scales = 'free') +
  scale_y_continuous(limits = c(0,1))

# fit psychometric functions
fit <- quickpsy(
  d = data, 
  x = comparison, 
  k = comparison.more.intense,
  grouping = .(condition, PID),
  log = TRUE,
  fun = cum_normal_fun,
  B = 100, # 10 or 100 for testing code, 10000 once everything is working, it will take time
  ci = 0.95
  )

# plot  psychometric functions
theme_set(theme_bw(base_size = 14))

xbreaks <- unique(data$comparison)

quartz() #mac os
# windows() # windows
plot(fit) + 
  scale_x_continuous(breaks = xbreaks) +
  coord_cartesian(xlim = c(100,1000), ylim = c(0,1)) +
  geom_vline(xintercept = 600, linetype = 'dotted') +
  labs(x = "comparison force (mN)", y = "Proporion called more intense")

ggsave("pilot2_psychfuns.pdf")


