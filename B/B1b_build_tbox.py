from rdflib import Graph, Namespace, RDF, RDFS, XSD

EX = Namespace("http://example.org/research#")

g = Graph()
g.bind("", EX)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# --------------------------------------------------------------------------- #
# helper shortcuts
# --------------------------------------------------------------------------- #
def cls(c):
    g.add((c, RDF.type, RDFS.Class))

def objprop(p, d, r, super_p=None):
    g.add((p, RDF.type, RDF.Property))
    g.add((p, RDFS.domain, d))
    g.add((p, RDFS.range,  r))
    if super_p:
        g.add((p, RDFS.subPropertyOf, super_p))

def dtprop(p, rng=XSD.string, dom=None):
    g.add((p, RDF.type, RDF.Property))
    g.add((p, RDFS.range, rng))
    if dom:
        g.add((p, RDFS.domain, dom))

# --------------------------------------------------------------------------- #
# classes
# --------------------------------------------------------------------------- #
for c in (
    "Agent Author Reviewer Paper Topic Review PublicationVenue Proceeding "
    "Journal JournalVolume ConferenceEdition Conference Workshop "
    "City TimeSpan"
).split():
    cls(EX[c])

# subclass axioms
g.add((EX.Author,   RDFS.subClassOf, EX.Agent))
g.add((EX.Reviewer, RDFS.subClassOf, EX.Author))
g.add((EX.Proceeding,    RDFS.subClassOf, EX.PublicationVenue))
g.add((EX.JournalVolume, RDFS.subClassOf, EX.PublicationVenue))
g.add((EX.Workshop,      RDFS.subClassOf, EX.Conference))

# --------------------------------------------------------------------------- #
# object properties
# --------------------------------------------------------------------------- #
# authorship & roles
objprop(EX.writes,              EX.Author,           EX.Paper)
objprop(EX.correspondingAuthor, EX.Author,           EX.Paper, super_p=EX.writes)

# citations & keywords
objprop(EX.cites,               EX.Paper,            EX.Paper)
objprop(EX.hasKeyword,          EX.Paper,            EX.Topic)

# publishing
objprop(EX.publishedIn,         EX.Paper,            EX.PublicationVenue)
objprop(EX.hasEdition,          EX.Conference,       EX.ConferenceEdition)
objprop(EX.heldInCity,          EX.ConferenceEdition,EX.City)
objprop(EX.heldDuring,          EX.ConferenceEdition,EX.TimeSpan)
objprop(EX.proceedingOf,        EX.ConferenceEdition,EX.Proceeding)

objprop(EX.hasVolume,           EX.Journal,          EX.JournalVolume)
objprop(EX.volumeOf,            EX.JournalVolume,    EX.Journal)  # optional inverse

# peer-review
objprop(EX.hasReview,           EX.Paper,            EX.Review)
objprop(EX.reviewer,            EX.Review,           EX.Reviewer)
objprop(EX.reviewsPaper,        EX.Reviewer,         EX.Paper)
g.add((EX.reviewsPaper, RDFS.subPropertyOf, EX.hasReview))

# --------------------------------------------------------------------------- #
# datatype properties
# --------------------------------------------------------------------------- #
dtprop(EX.title)                                   # label for anything
dtprop(EX.abstract,               dom=EX.Paper)    # paper abstract
dtprop(EX.year,      rng=XSD.gYear)                # generic year literal
dtprop(EX.startDate, rng=XSD.date, dom=EX.TimeSpan)
dtprop(EX.endDate,   rng=XSD.date, dom=EX.TimeSpan)

# --------------------------------------------------------------------------- #
g.serialize("research_publications_tbox.ttl")
print("TBOX serialised with", len(g), "triples.")
