# 03_train_kge_models.py
# ------------------------------------------------------------
# Train & evaluate 4 KGE models on B2_research_publications KG
# PyKEEN ≥ 1.10   (pip install pykeen)
# ------------------------------------------------------------
import json, pathlib, itertools, datetime, torch
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory

ROOT = pathlib.Path("experiments")
ROOT.mkdir(exist_ok=True)

KG_FILE = "B2_research_publications_abox.tsv"
tf = TriplesFactory.from_path(KG_FILE)
train, test = tf.split()          # stratified split

## ----- Small test

from pykeen.triples import CoreTriplesFactory

# Sample N triples manually
n = 500
indices = torch.randperm(test.num_triples)[:n]
sampled_triples = test.mapped_triples[indices]

# Create CoreTriplesFactory manually
small_test = CoreTriplesFactory(
    mapped_triples=sampled_triples,
    num_entities=len(test.entity_to_id),
    num_relations=len(test.relation_to_id),
)


## -----
device = "cuda" if torch.cuda.is_available() else "cpu"

MODELS = ["TransE", "TransH", "RotatE", "ComplEx"]
EMB_DIMS = [128, 256]             # two embedding sizes
NEGS = [1, 5]                     # negatives / positive

def run_one(model_name, emb_dim, negs):
    tag = f"{model_name}_d{emb_dim}_n{negs}"
    out_dir = ROOT / tag
    if out_dir.exists():
        print(f"✓ {tag} already trained")
        return

    print(f"▶ Training {tag}")
    # result = pipeline(
    #     training=train,
    #     testing=test,
    #     model=model_name,
    #     model_kwargs=dict(embedding_dim=emb_dim),
    #     training_kwargs=dict(num_epochs=30),
    #     negative_sampler_kwargs=dict(num_negs_per_pos=negs),
    #     optimizer_kwargs=dict(lr=0.01),
    #     random_seed=2025,
    #     device=device,
    # )

    result = pipeline(
        training=train,
        testing=small_test,
        model=model_name,
        model_kwargs=dict(embedding_dim=emb_dim),
        training_kwargs=dict(num_epochs=3),
        negative_sampler_kwargs=dict(num_negs_per_pos=negs),
        optimizer_kwargs=dict(lr=0.01),
        random_seed=2025,
        device=device,
    )





    # save metrics & model
    out_dir.mkdir()
    (out_dir / "metrics.json").write_text(
        json.dumps(result.metric_results.to_dict(), indent=2))
    result.save_to_directory(out_dir)

for m, d, n in itertools.product(MODELS, EMB_DIMS, NEGS):
    run_one(m, d, n)

print("Finished:", datetime.datetime.now())
