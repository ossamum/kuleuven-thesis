library(ggplot2)
library(dplyr)
library(corrplot)
library(RColorBrewer)

# DATA COLLECITON
df <- read.csv('dataviz/tweets_yearmonth.csv')

df %>% 
  ggplot(aes(x = created_at_year_month, y=tweets, fill=tweet_type)) +
  geom_bar(stat='identity') +
  labs(title='Number of tweets', x='Year and Month', y='Number of tweets') +
  scale_fill_discrete(name = "Tweet type") +
  theme_bw()

# METHODS
# BOT BEHAVIOUR
df <- read.csv('dataviz/bot_dataset.csv')

like <- df %>% 
  filter(tweet_type == 'standard') %>% 
  select(-c(tweet_type, retweet_count)) 

quartiles <- quantile(like$like_count, probs=c(.25, .75), na.rm = FALSE)
iqr <- quartiles[2] - quartiles[1]


m <- like %>% 
  filter(like_count < quartiles[2] + (1.5 * iqr)) %>% 
  cor()


corrplot(m, type="upper", order="hclust",
         col=brewer.pal(n=8, name="RdYlBu"))



retweet <- df %>% 
  select(-c(tweet_type, like_count)) 

quartiles <- quantile(retweet$retweet_count, probs=c(.25, .75), na.rm = FALSE)
iqr <- quartiles[2] - quartiles[1]


m <- retweet %>% 
  filter(retweet_count < quartiles[2] + (1.5 * iqr)) %>% 
  cor()


corrplot(m, type="upper", order="hclust",
         col=brewer.pal(n=8, name="RdYlBu"))







bot_like
















