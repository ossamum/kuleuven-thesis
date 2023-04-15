library(ggplot2)
library(dplyr)



df <- read.csv('dataviz/tweets_yearmonth.csv')


df %>% 
  ggplot(aes(x = created_at_year_month, y=tweets, fill=tweet_type)) +
  geom_bar(stat='identity') +
  labs(title='Number of tweets', x='Year and Month', y='Number of tweets') +
  scale_fill_discrete(name = "Tweet type") +
  theme_bw()

