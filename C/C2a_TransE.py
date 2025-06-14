import torch
from pathlib import Path
from pykeen.triples import TriplesFactory
from sklearn.metrics.pairwise import euclidean_distances

# --- load trained TransE model and triples -----------------
save_dir = Path('C/KGE_B2_research_publications_model1')
model = torch.load(save_dir / 'trained_model.pkl', weights_only=False)
tf = TriplesFactory.from_path_binary(save_dir / 'training_triples')

entity_emb = model.entity_representations[0]().detach().cpu()
rel_emb    = model.relation_representations[0]().detach().cpu()

id2ent = {v: k for k, v in tf.entity_to_id.items()}
ent2id = tf.entity_to_id
rel2id = tf.relation_to_id

# --- choose an example paper that cites others --------------
paper_A = 'http://example.org/research#paper100221604'
paper_vec = entity_emb[ent2id[paper_A]]

# --- (i) most-likely cited paper ----------------------------
cites_vec = rel_emb[rel2id['http://example.org/research#cites']]
est_cited = paper_vec + cites_vec

dists = euclidean_distances([est_cited], entity_emb)[0]
cited_idx = torch.argmin(torch.tensor(dists)).item()
paper_C   = id2ent[cited_idx]

# --- (ii) most-likely author of that cited paper ------------
writes_vec = rel_emb[rel2id['http://example.org/research#writes']]
est_author = entity_emb[cited_idx] - writes_vec

auth_dists = euclidean_distances([est_author], entity_emb)[0]
author_idx = torch.argmin(torch.tensor(auth_dists)).item()
author_A   = id2ent[author_idx]

print('Predicted cited paper:', paper_C)
print('Predicted author    :', author_A)


# ----------- Result -------------- 
# Predicted cited paper: http://example.org/research#paper100221604
# Predicted author    : http://example.org/research#author155959512