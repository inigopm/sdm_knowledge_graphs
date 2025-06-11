from rdflib import Graph, Namespace, RDF, RDFS, XSD

EX = Namespace("http://example.org/research#")

g = Graph()
g.bind("", EX)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# helper
def cls(c):
    g.add((c, RDF.type, RDFS.Class))

def objprop(p, d, r):
    g.add((p, RDF.type, RDF.Property))
    g.add((p, RDFS.domain, d))
    g.add((p, RDFS.range, r))

# classes
for c in (
    "Agent Author Reviewer Paper Topic Review PublicationVenue "
    "Proceeding JournalVolume ConferenceEdition Conference Workshop "
    "City TimeSpan"
).split():
    cls(EX[c])

# subclass axioms
g.add((EX.Author, RDFS.subClassOf, EX.Agent))
g.add((EX.Reviewer, RDFS.subClassOf, EX.Author))
g.add((EX.Proceeding, RDFS.subClassOf, EX.PublicationVenue))
g.add((EX.JournalVolume, RDFS.subClassOf, EX.PublicationVenue))
g.add((EX.Workshop, RDFS.subClassOf, EX.Conference))

# object properties
objprop(EX.writes,              EX.Author,           EX.Paper)
objprop(EX.correspondingAuthor, EX.Author,           EX.Paper)
g.add((EX.correspondingAuthor, RDFS.subPropertyOf, EX.writes))

objprop(EX.cites,               EX.Paper,            EX.Paper)
objprop(EX.hasKeyword,          EX.Paper,            EX.Topic)
objprop(EX.publishedIn,         EX.Paper,            EX.PublicationVenue)
objprop(EX.hasEdition,          EX.Conference,       EX.ConferenceEdition)
objprop(EX.heldInCity,          EX.ConferenceEdition,EX.City)
objprop(EX.heldDuring,          EX.ConferenceEdition,EX.TimeSpan)
objprop(EX.hasReview,           EX.Paper,            EX.Review)
objprop(EX.reviewer,            EX.Review,           EX.Reviewer)
objprop(EX.reviewsPaper,        EX.Reviewer,         EX.Paper)
g.add((EX.reviewsPaper, RDFS.subPropertyOf, EX.hasReview))

# datatype properties
g.add((EX.title, RDF.type, RDF.Property))
g.add((EX.title, RDFS.range, XSD.string))

g.add((EX.year, RDF.type, RDF.Property))
g.add((EX.year, RDFS.range, XSD.gYear))

g.add((EX.startDate, RDF.type, RDF.Property))
g.add((EX.startDate, RDFS.domain, EX.TimeSpan))
g.add((EX.startDate, RDFS.range, XSD.date))

g.add((EX.endDate, RDF.type, RDF.Property))
g.add((EX.endDate, RDFS.domain, EX.TimeSpan))
g.add((EX.endDate, RDFS.range, XSD.date))

g.serialize("research_publications_tbox.ttl")
print("TBOX serialised.")
