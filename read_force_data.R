library(signal)
library(tidyverse)
library(patchwork)
source('aurora_functions.R')
theme_set(theme_bw())

dataFolder <- '/Users/sarmc72/Library/CloudStorage/OneDrive-Linköpingsuniversitet/projects - in progress/Skin imaging/Data Pilot Indentation Discrimination/'
forceDataFiles <- list.files(dataFolder, 'ddf', recursive = TRUE)

outputFolder <- 'Processed Force Data/'
if (!dir.exists(outputFolder)) {dir.create(outputFolder)}
timenow <- format(Sys.time(), '%Y%m%d_%H%M%S')
outputDataFile <- paste0(outputFolder, 'force_data_',timenow,'.txt')
outputPlotFolder <- paste0(outputFolder,'Force Plots ',timenow,'/')
if (!dir.exists(outputPlotFolder)) {dir.create(outputPlotFolder)}
outputTracesFolder <- paste0(outputFolder,'Force Overlay ',timenow,'/')
if (!dir.exists(outputTracesFolder)) {dir.create(outputTracesFolder)}

overlayData <- tibble()
for (n in seq_along(forceDataFiles)) {
# for (n in 1:10) {
  ddfFile <- paste0(dataFolder,forceDataFiles[n])
  stimID <- str_extract(ddfFile, "--[0-9]+_[0-9]+") %>% str_split_fixed("_",2) 
  stimID1 <- stimID[1] %>% str_extract("[0-9]+") %>% parse_number()
  stimID2 <- stimID[2] %>% str_extract("[0-9]+") %>% parse_number()
  stimNo <- stimID1*100 + stimID2
  
  print(paste(n, 'of', length(forceDataFiles), ':', ddfFile))
  
  # read the protocol info
  ptcl <- ddfFile %>% read_force_protocol(skip = 16, n_max = 5)
  
  # read the raw data
  ddfData <- ddfFile %>% read_delim('\t', skip = 25, col_types = paste0(rep('d',12), collapse = ''))
  #ddfData %>% plot_ddf_data()
  
  # make noise filter
  SamplingRate <- read_lines(ddfFile, skip = 1, n_max = 1) %>% parse_number()
  FilterFreqCutOff <- ceiling(10^(1.4 + 0.6*log10( 1000/ptcl$rampOnDuration.ms))) 
  butterworthFilter <- butter(n = 2, W = FilterFreqCutOff/SamplingRate, type = "low")
  
  # data in real units, filtered data, and time derivative
  scaleUnits <- read_lines(ddfFile, skip = 8, n_max = 1) %>% 
    str_split('\t') %>% .[[1]] %>% .[-1] %>% parse_double()
  
  scaledData <- ddfData %>% 
    scale_and_filter(scaleUnits, SamplingRate, butterworthFilter) %>% 
    dplyr::filter(Time.ms %>% between(ptcl$stimWindowStart, ptcl$stimWindowEnd))
  
  # automatically find where the force ramps are
  forceRateThreshold <- 0.1*(ptcl$targetForce.mN/ptcl$rampOnDuration.ms)
  forceRamps <- find_ramps(scaledData, ptcl, ForceDeriv.Nps, forceRateThreshold)
  
  # save summary data
  summaryData <- scaledData %>%
    summarise_data(ramps = forceRamps) %>% 
    mutate(targetForce.mN = ptcl$targetForce.mN,
           targetRampTime.ms = ptcl$rampOnDuration.ms,
           positionLimit.mm = ptcl$lengthLimit.mm,
           sourceFile = ddfFile %>% str_replace(dataFolder,'')
    ) 
  
  tare <- summaryData %>% 
    dplyr::filter(phase == 'pre-stim') %>% 
    select(meanForce.mN, meanPosition.mm)
  
  overlayData <- bind_rows(overlayData,
                           scaledData %>% 
                             mutate(Force.mN = ForceFiltered.mN - tare$meanForce.mN,
                                    Length.mm = LengthFiltered.mm - tare$meanPosition.mm) %>% 
                             select(Time.ms, Force.mN, Length.mm) %>% 
                             mutate(targetForce.mN = ptcl$targetForce.mN,
                                    targetRampTime.ms = ptcl$rampOnDuration.ms,
                                    sourceFile = ddfFile %>% 
                                      str_replace(dataFolder,'')
                             )
  )
  
  summaryData %>% 
    write_delim(paste0(outputDataFile), '\t', append = n>1)
  print(paste("added data to", outputDataFile))
  
  if (.Platform$OS.type == "unix") {
    quartz(); plot(1:10)
  }  else { windows() }
  
  scaledData %>%
    ggplot(aes(x = Time.ms)) +
    geom_vline(xintercept = c(ptcl$rampOn,ptcl$hold,ptcl$rampOff,ptcl$endStim), colour = 'grey') +
    geom_vline(xintercept = unlist(forceRamps), colour = 'red') +
    geom_point(aes(y = ForceMeasured.mN), shape = 21, fill = 'black', alpha = 0.1, size = 3) +
    geom_point(aes(y = ForceFiltered.mN), colour = 'blue', size = 1) +
    labs(title = 'Force trace', x = 'Time (ms)', y = 'Force (mN)') -> force.trace
  
  scaledData %>%
    ggplot(aes(x = Time.ms)) +
    geom_vline(xintercept = unlist(forceRamps), colour = 'red') +
    geom_point(aes(y = ForceDeriv.Nps), colour = 'blue', size = 1) +
    labs(title = 'Force derivative', x = 'Time (ms)', y = 'Force rate (N/s)') -> force.deriv
  
  scaledData %>%
    ggplot(aes(x = Time.ms)) +
    geom_vline(xintercept = unlist(forceRamps), colour = 'red') +
    geom_point(aes(y = LengthMeasued.mm), shape = 21, fill = 'black', alpha = 0.1, size = 3) +
    geom_point(aes(y = LengthFiltered.mm), colour = 'purple', size = 1) +
    labs(title = paste('Displacement trace, limit =', ptcl$lengthLimit.mm, 'mm'),
         x = 'Time (ms)', y = 'Displacement (mm)') -> disp.trace
  
  scaledData %>%
    ggplot(aes(x = Time.ms)) +
    geom_vline(xintercept = unlist(forceRamps), colour = 'red') +
    geom_point(aes(y = LengthDeriv.mps), colour = 'purple', size = 1) +
    labs(title = 'Displacement derivative', x = 'Time (ms)', y = 'Velocity (m/s)') -> disp.deriv
  
  force.trace / force.deriv / disp.trace / disp.deriv +
    plot_annotation(title = paste('Target =', ptcl$targetForce.mN,'mN.',
                                  ptcl$rampOnDuration.ms,'ms ramp.',
                                  'Low pass butterworth filter',FilterFreqCutOff,'Hz'))

  plotFile <- ddfFile %>%
    str_replace(dataFolder,'') %>%
    str_replace_all('/','_') %>%
    paste0(outputPlotFolder,.) %>%
    str_replace('ddf', 'tiff')

  if (!dir.exists(file.path(dirname(plotFile))) ) dir.create(file.path(dirname(plotFile)), recursive = TRUE)
  ggsave(plotFile)
  print(paste('saved figure:',plotFile))

  dev.off()
}

overlayData <- overlayData %>% 
  mutate(PID = str_extract(sourceFile, "(P02|EK|MM|SM)"),
         condition = if_else(
           str_detect(sourceFile, "shaved"),
           "shaved",
           "film"
         )) 

overlayData %>% 
  group_by(condition,targetForce.mN,PID,sourceFile) %>% 
  tally() %>% 
  xtabs( ~ condition + targetForce.mN + PID, .)

participants <- sort_unique(overlayData$PID)
forces <- sort_unique(overlayData$targetForce.mN)

for (participantN in seq_along(participants)) {
  plotlist = list()
  for (forceN in seq_along(forces)) {
    print(paste("force:",forces[forceN], "mN"))
    plotData <- overlayData %>% 
      dplyr::filter(PID == participants[participantN] & targetForce.mN == forces[forceN]) %>% 
      mutate(nfiles = n_distinct(sourceFile),
             targetForceLabel = paste0('t=',targetForce.mN,'mN, n=',nfiles))
 
    force.trace <- plotData %>%
      ggplot(aes(x = Time.ms/1000, y = Force.mN)) +
      facet_wrap( ~ targetForceLabel) +
      # , colour = condition
      geom_line(aes(group = sourceFile), size = 0.5, alpha = 0.4) +
      labs(x = NULL, y = NULL)
    if (forceN==1) force.trace <- force.trace + labs(y = 'Force (mN)') 
    if (forceN!=length(forces)) force.trace <- force.trace + theme(legend.position = "none") 
    
    pos.trace <- plotData %>%
      ggplot(aes(x = Time.ms/1000, y = Length.mm)) +
      facet_wrap( ~ targetForceLabel) +
      # , colour = condition
      geom_line(aes(group = sourceFile), size = 0.5, alpha = 0.4) +
      labs(x = 'Time (sec)', y = NULL)
    if (forceN==1) pos.trace <- pos.trace + labs(y = 'Position (mm)')
    if (forceN!=length(forces)) pos.trace <- pos.trace + theme(legend.position = "none") 
    
    plotlist[[forceN]] = (force.trace / pos.trace)
  }
  
  w = 17.5; h = 4.5
  if (.Platform$OS.type == "unix") {
    quartz(width = w, height = h); plot(1:10)
  }  else { windows(w,h) }
  wrap_plots(plotlist, ncol = length(forces)) + 
    plot_annotation(title = paste0('PID = ',participants[participantN]),
                    caption = paste0('Overlaid force traces (top) and position traces (bottom) for different target forces (columns), PID = ',participants[participantN]))
  
  plotFile <- paste0(outputTracesFolder,'Force overlay ',participants[participantN],'.tiff')
  if (!dir.exists(file.path(dirname(plotFile))) ) dir.create(file.path(dirname(plotFile)), recursive = TRUE)
  ggsave(plotFile)
  dev.off()
}
