library(ggplot2)
library(dplyr)
library(tidyr)
library(corrplot)
library(RColorBrewer)
library(gridExtra)
library(grid)
library(patchwork)


# DATA COLLECITON
df <- read.csv('dataviz/tweets_yearmonth.csv')

df %>% 
  ggplot(aes(x = created_at_year_month, y=tweets, fill=tweet_type)) +
  geom_bar(stat='identity') +
  labs(title='Number of tweets', x='Year and Month', y='Number of tweets') +
  scale_fill_discrete(name = "Tweet type") +
  theme_bw()

# METHODS
# DESCRIPTIVE
df <- read.csv('all_tweets_v15.csv') %>% 
  mutate(Gender = recode(gender_of_author,
                         'F' = 'Female',
                         'M' = 'Male',
                         'ORG' = 'Organization'),
        #  Verified = verified_author,
        #  Profession = profession_of_author,
        #  has_media = as.logical(has_media),
        #  has_hashtags = as.logical(has_hashtags),
        #  has_mentions = as.logical(has_mentions),
        #  Language = recode(new_lang ,
        #                    'tr' = 'Turkish',
        #                    'en' = 'English',
        #                    'short_text' = 'Short text',
        #                    'other' = 'Other'),
        #  is_trend_topic = ifelse(n_trend_topics > 0, TRUE, FALSE),
        # created_at_time = created_at %>% as.POSIXct() %>% format('%H'),
        # political_context = political_context_annotation,
        Topic = recode(sttm_topic,
                       "search for justice"= "Search for justice",
                       "other"= "Other",
                       "injustice against children"= "Injustice against children",
                       "decree-law"= "Decree-law",
                       "lost people"= "Lost people",
                       "politics"= "Politics",
                       "dismissal of governmental workers"= "Dismissal of governmental workers",
                       "inflation, financial instability"= "Inflation, financial instability",
                       "supreme court"= "Supreme court",
                       "expressing wishes"= "Expressing wishes",
                       "death, torture, suicide"= "Death, torture, suicide",
                       "vulnerable, sick people"= "Vulnerable, sick people",
                       "irrelevant tweets"= "Irrelevant tweets",
                       "Uyghurs in China"= "Uyghurs",
                       "woman rights"= "Woman rights",
                       "democracy"= "Democracy",
                       "activism for nature"= "Activism for nature",
                       "international relations"= "International relations",
                       "invitation, agenda declaration"= "Invitation, agenda declaration",
                       "freedom of speech"= "Freedom of speech")
  )

# targets




bx.like <- df %>% 
  ggplot(aes(x = Gender, color = Gender)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = Gender, color = Gender)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()




# gender

df.summ <- df %>%
  group_by(Gender) %>%
  summarize(
    Accounts = n_distinct(author_id),
    Tweets = n()
  ) %>% 
  mutate(Tweets_per_Account = as.integer(Tweets / Accounts))

bx.like <- df %>% 
  ggplot(aes(x = Gender, color = Gender)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = Gender, color = Gender)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.accounts <- ggplot(df.summ, aes(x = Gender, y = Accounts, color = Gender, fill = Gender)) +
  geom_col(colour='black') +
  geom_text(aes(label = Accounts), vjust = 1.5, colour = 'black') +
  labs(y='Number of accounts') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = Gender, y = Tweets_per_Account, color = Gender, fill = Gender)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets_per_Account), vjust = 1.5, colour = 'black') +
  labs(y='Number of tweets per account') +
  theme_bw()


bx.like + bx.retweet + bar.accounts + bar.tweets + plot_layout(nrow=2, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())

# verification

df.summ <- df %>%
  group_by(Verified) %>%
  summarize(
    Accounts = n_distinct(author_id),
    Tweets = n()
  ) %>% 
  mutate(Tweets_per_Account = as.integer(Tweets / Accounts))

bx.like <- df %>% 
  ggplot(aes(x = Verified, color = Verified)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = Verified, color = Verified)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.accounts <- ggplot(df.summ, aes(x = Verified, y = Accounts, color = Verified, fill = Verified)) +
  geom_col(colour='black') +
  geom_text(aes(label = Accounts), vjust = 1.5, colour = 'black') +
  labs(y='Number of accounts') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = Verified, y = Tweets_per_Account, color = Verified, fill = Verified)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets_per_Account), vjust = 1.5, colour = 'black') +
  labs(y='Number of tweets per account') +
  theme_bw()


bx.like + bx.retweet + bar.accounts + bar.tweets + plot_layout(nrow=2, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())

# profession

df.summ <- df %>%
  group_by(Profession) %>%
  summarize(
    Accounts = n_distinct(author_id),
    Tweets = n()
  ) %>% 
  mutate(Tweets_per_Account = as.integer(Tweets / Accounts))

bx.like <- df %>% 
  ggplot(aes(x = Profession, color = Profession)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = Profession, color = Profession)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.accounts <- ggplot(df.summ, aes(x = Profession, y = Accounts, color = Profession, fill = Profession)) +
  geom_col(colour='black') +
  geom_text(aes(label = Accounts), vjust = 1.2, colour = 'black') +
  labs(y='Number of accounts') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = Profession, y = Tweets_per_Account, color = Profession, fill = Profession)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets_per_Account), vjust = 1.5, colour = 'black') +
  labs(y='Number of tweets per account') +
  theme_bw()


bx.like + bx.retweet + bar.accounts + bar.tweets + plot_layout(nrow=2, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())

# hasmedia



df.summ <- df %>%
  group_by(has_media) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(x = has_media, color = has_media)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = has_media, color = has_media)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = has_media, y = Tweets, color = has_media, fill = has_media)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets), vjust = 1.2, colour = 'black') +
  labs(y='Number of tweets') +
  theme_bw()



bx.like + bx.retweet + bar.tweets + plot_layout(nrow=1, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())


# has hashtag
df.summ <- df %>%
  group_by(has_hashtags) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(x = has_hashtags, color = has_hashtags)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = has_hashtags, color = has_hashtags)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = has_hashtags, y = Tweets, color = has_hashtags, fill = has_hashtags)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets), vjust = 1.2, colour = 'black') +
  labs(y='Number of tweets') +
  theme_bw()


bx.like + bx.retweet + bar.tweets + plot_layout(nrow=1, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())


# has mentions
df.summ <- df %>%
  group_by(has_mentions) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(x = has_mentions, color = has_mentions)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = has_mentions, color = has_mentions)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = has_mentions, y = Tweets, color = has_mentions, fill = has_mentions)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets), vjust = 1.2, colour = 'black') +
  labs(y='Number of tweets') +
  theme_bw()


bx.like + bx.retweet + bar.tweets + plot_layout(nrow=1, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())


# is trend topic
df.summ <- df %>%
  group_by(is_trend_topic) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(x = is_trend_topic, color = is_trend_topic)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = is_trend_topic, color = is_trend_topic)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = is_trend_topic, y = Tweets, color = is_trend_topic, fill = is_trend_topic)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets), vjust = 1.2, colour = 'black') +
  labs(y='Number of tweets') +
  theme_bw()


bx.like + bx.retweet + bar.tweets + plot_layout(nrow=1, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())



# language
df.summ <- df %>%
  group_by(Language) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(x = Language, color = Language)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = Language, color = Language)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = Language, y = Tweets, color = Language, fill = Language)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets), vjust = -0.4, colour = 'black') +
  labs(y='Number of tweets') +
  theme_bw()


bx.like + bx.retweet + bar.tweets + plot_layout(nrow=1, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())



# political context
df.summ <- df %>%
  group_by(political_context) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(x = political_context, color = political_context)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = political_context, color = political_context)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = political_context, y = Tweets, color = political_context, fill = political_context)) +
  geom_col(colour='black') +
  geom_text(aes(label = Tweets), vjust = 1.2, colour = 'black') +
  labs(y='Number of tweets') +
  theme_bw()


bx.like + bx.retweet + bar.tweets + plot_layout(nrow=1, guides = "collect") & theme(axis.title.x=element_blank(), axis.text.x=element_blank())



# BOT BEHAVIOUR

m <- df %>% 
  select(like_count,
         retweet_count,
         english,
         universal,
         eng_astroturf,
         eng_fake_follower,
         eng_financial,
         eng_other,
         eng_overall,
         eng_self_declared,
         eng_spammer,
         uni_astroturf,
         uni_fake_follower,
         uni_financial,
         uni_other,
         uni_overall,
         uni_self_declared,
         uni_spammer) %>% 
  cor(method = 'spearman')



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



# EMOTION 

m <- df %>% 
  select(
    anger,
    fear,
    anticipation,
    trust,
    surprise,
    sadness,
    joy,
    disgust,
    like_count,
    retweet_count
  ) %>% 
  na.omit() %>% 
  cor(method='spearman')
  

corrplot(m, type="upper", order="hclust",
         col=brewer.pal(n=8, name="RdYlBu"), insig = "p-value")





# CREATED AT
df.summ <- df %>%
  group_by(created_at_time) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(x = created_at_time, color = created_at_time)) +
  geom_boxplot(aes(y = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(x = created_at_time, color = created_at_time)) +
  geom_boxplot(aes(y = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw()

bar.tweets <- ggplot(df.summ, aes(x = created_at_time, y = Tweets, color = created_at_time, fill = created_at_time)) +
  geom_col(colour='black') +
  labs(y='Number of tweets') +
  theme_bw()


bx.like + bx.retweet + bar.tweets + plot_layout(nrow=3, guides = "collect") & theme(axis.title.x=element_blank(), legend.position = "none")

# TOPIC MODELING
df$Topic <- factor(df$Topic, levels = rev(sort(unique(df$Topic))))

df.summ <- df %>%
  group_by(Topic ) %>%
  summarize(
    Tweets = n()
  ) 

bx.like <- df %>% 
  ggplot(aes(y = Topic, color = Topic)) +
  geom_boxplot(aes(x = log(like_count + 1))) +
  labs(y='Log of number of likes') +
  guides(color = 'none') +
  theme_bw()

bx.retweet <- df %>% 
  ggplot(aes(y = Topic, color = Topic)) +
  geom_boxplot(aes(x = log(retweet_count + 1))) +
  labs(y='Log of number of retweets') +
  guides(color = 'none') +
  theme_bw() +
  theme(axis.title.y = element_blank(), legend.position = "none", axis.text.y = element_blank())



bar.tweets <- ggplot(df.summ, aes(y = Topic, x = Tweets, color = Topic, fill = Topic)) +
  geom_col(colour='black') +
  labs(y='Number of tweets') +
  theme_bw()


bx.like + bx.retweet + plot_layout(nrow=1, guides = "collect") & theme(axis.title.y=element_blank(), legend.position = "none")



# RESULTS
# hour
df <- read.csv('dataviz/created_at_retweet.csv')

df %>% 
  ggplot(aes(hour, retweet_count, fill='cyan')) +
  stat_summary(fun.data=mean_sdl, geom="bar") +
  stat_summary(fun.data=mean_cl_boot, geom="errorbar", width=0.3) +
  labs(title='Retweets by hour', y='Number of retweet') +
  scale_x_discrete('Hour', limits=seq(0, 23)) +
  guides(fill = F) +
  theme_bw()
  
















