# from sentence_transformers import SentenceTransformer
# import pandas as pd
#
# model = SentenceTransformer("emrecan/bert-base-turkish-cased-mean-nli-stsb-tr")
#
# batch_size = 5000
#
# embeddings = None
# for i in tqdm(range((tweets_df_v16.shape[0] // batch_size) + 1)):
#     sentences = tweets_df_v16.iloc[
#                 (i * batch_size): ((i + 1) * batch_size)
#                 ].text.to_list()
#     embeddings_tmp = model.encode(sentences)
#     if embeddings is None:
#         embeddings = embeddings_tmp
#     else:
#         embeddings = np.concatenate([embeddings, embeddings_tmp], axis=0)
#
# assert embeddings.shape[0] == tweets_df_v16.shape[0]
#
# tweets_df_v16_tmp = pd.concat(
#     [
#         tweets_df_v16.reset_index(drop=True),
#         pd.DataFrame(embeddings).reset_index(drop=True),
#     ],
#     axis=1,
# )
#
# tweets_df_v16_tmp = tweets_df_v16_tmp.rename(
#     columns={i: f"sentence_embedding_{i}" for i in range(768)}
# )
