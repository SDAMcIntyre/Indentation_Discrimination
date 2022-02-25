library(rlang)
library(quickpsy)
library(dplyr)
library(stringr)
library(ggplot2)

filelist <- list.files(
  'C:/Users/emma_/OneDrive/Skrivbord/R course/data',
  # 'C:/Users/emma_/OneDrive/Skrivbord/R course/pilot2', 
  # '/Users/sarmc72/Library/CloudStorage/OneDrive-Linköpingsuniversitet/projects - in progress/Skin imaging/Data Pilot Indentation Discrimination',
  pattern = 'data', 
  recursive = TRUE,
  full.names = TRUE)


data <- c()
for(currentfile in filelist) {
  # which one are we up to
  print(currentfile)
  
  # find settings file
  settingsfile <- str_replace(currentfile,"data.csv","settings.csv")
  
  # extract condition from settings file
  extracted.condition <- read.csv(settingsfile)[7,2]
  
  # extract info from filename
  extracted.PID <- str_extract(currentfile, "(P[0-9]{2})")

  # read data file and add columns with extracted info
  currentdata <- read.csv(currentfile) %>% 
    mutate(PID = extracted.PID,
           condition = extracted.condition,
           filename = currentfile)
  # add the new data to the end of the data frame
  data <- rbind(data, currentdata)
  rm(currentdata)
}

# exclusions (comment out and enter file name + trial number)
# data <- data %>%
#   filter(
#     !(str_detect(filename,"2022-02-21_16-09-28") & trial.number ==7) & # bad stimulus delivery
#       !(str_detect(filename,"2022-02-21_16-09-28") & trial.number ==8)
#     )

# simple figure to check the data
ggplot(data, aes(x = comparison, y = comparison.more.intense, colour = condition)) +
  stat_summary(geom = 'point', fun = 'mean') +
  facet_wrap(. ~ PID, scales = 'free') + # comment out to create a graph that contains all the participants together (mean of all trials)
  scale_y_continuous(limits = c(0,1))

# fit psychometric functions
shaved_only_data <- filter(data, condition == "shaved")
fit <- quickpsy(
  d = shaved_only_data, 
  x = comparison, 
  k = comparison.more.intense,
  grouping = .(condition, PID),
  # parini = c(250, 2000),
  log = TRUE,
  fun = cum_normal_fun,
  B = 100, # 10 or 100 for testing code, 10000 once everything is working, it will take time
  ci = 0.95
)
# plot  psychometric functions
theme_set(theme_bw(base_size = 14))

xbreaks <- unique(data$comparison)

# quartz() #mac os
windows() # windows
plot(fit) + 
  scale_x_continuous(breaks = xbreaks) +
  geom_vline(xintercept = 600, linetype = 'dotted') +
  labs(x = "comparison force (mN)", y = "Proporion called more intense")

ggsave("pilot2_psychfuns.pdf")

# Plot the PSE
plotthresholds(fit)

# plot the PSE and the slope
plotpar(fit)

#convert from log
PSEfilm_for_stats <- fit$par %>% 
  filter(parn == "p1" & condition == "film") %>% 
  mutate(
    PSE.mN = exp(par),
    CIupper = exp(parsup),
    CIlowe = exp(parinf)
  )

#t-test
t.test(
  x = PSEfilm_for_stats$PSE.mN,
  mu = 600,
  var.equal = TRUE
)
