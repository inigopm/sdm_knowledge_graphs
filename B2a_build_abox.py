import csv
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
import pandas as pd
import random

EX = Namespace("http://example.org/research#")

g = Graph()
g.bind("", EX)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)


def uri(kind, id_):
    return EX[f"{kind}{id_}"]
import re

def clean_uri_string(s):
    s = s.lower()
    s = re.sub(r'[\"\'<>#%{}|\\^~\[\]`]','', s)
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = s.strip('_')
    return s

#authors
with open("dataset_csv/Node_author.csv", newline='', encoding='utf-8') as authors:
    reader = csv.DictReader(authors)
    for row in reader:
        author_uri = uri("author", row['author_id'])
        g.add((author_uri, RDF.type, EX.Author))
        g.add((author_uri, EX.title, Literal(row['author_name'], datatype=XSD.string)))

#papers
with open("dataset_csv/Node_paper.csv", newline='', encoding='utf-8') as papers:
    reader = csv.DictReader(papers)
    for row in reader:
        paper_uri = uri("paper", row['id_paper'])
        g.add((paper_uri, RDF.type, EX.Paper))
        g.add((paper_uri, EX.title, Literal(row['paper_title'], datatype=XSD.string)))
        year_str = row['year'].strip()
        if year_str.isdigit():
            g.add((paper_uri, EX.year, Literal(year_str, datatype=XSD.gYear)))

#conferences
with open("dataset_csv/Node_conference.csv", newline='', encoding='utf-8') as conferences:
    reader = csv.DictReader(conferences)
    for row in reader:
        conf_uri = uri("conference", row['conference_name'].replace(" ", "_"))
        g.add((conf_uri, RDF.type, EX.Conference))
        g.add((conf_uri, EX.title, Literal(row['conference_name'], datatype=XSD.string)))

#editions
with open("dataset_csv/Node_edition.csv", newline='', encoding='utf-8') as editions:
    reader = csv.DictReader(editions)
    for row in reader:
        edition_uri = uri("edition", clean_uri_string(row['edition_id']))
        g.add((edition_uri, RDF.type, EX.ConferenceEdition))
        year_str = row['year'].strip()
        if year_str.isdigit():
            g.add((edition_uri, EX.year, Literal(year_str, datatype=XSD.gYear)))
        g.add((edition_uri, EX.heldInCity, uri("city", row['city'].replace(" ", "_"))))
        timespan_uri = uri("timespan", clean_uri_string(row['edition_id']))
        g.add((timespan_uri, RDF.type, EX.TimeSpan))
        g.add((edition_uri, EX.heldDuring, timespan_uri))
        if year_str.isdigit():
            start_month = random.randint(1, 12)
            start_day = random.randint(1, 21)
            duration = random.randint(1, 7)# no more than a week
            end_day = start_day + duration
            if end_day > 28:
                end_day = 28
            g.add((timespan_uri, EX.startDate, Literal(f"{year_str}-{start_month:02d}-{start_day:02d}", datatype=XSD.date)))
            g.add((timespan_uri, EX.endDate, Literal(f"{year_str}-{start_month:02d}-{end_day:02d}", datatype=XSD.date)))


#journals
with open("dataset_csv/Node_journals.csv", newline='', encoding='utf-8') as journals:
    reader = csv.DictReader(journals)
    for row in reader:
        journal_uri =uri("journal", clean_uri_string(row['journal_name']))
        g.add((journal_uri, RDF.type, EX.PublicationVenue))
        g.add((journal_uri, EX.title, Literal(row['journal_name'], datatype=XSD.string)))

#volumes
with open("dataset_csv/Node_volume.csv", newline='', encoding='utf-8') as volumes:
    reader = csv.DictReader(volumes)
    for row in reader:
        volume_uri = uri("volume", row['volume'])
        g.add((volume_uri, RDF.type, EX.JournalVolume))
        year_str = row['year'].strip()
        if year_str.isdigit():
            g.add((volume_uri, EX.year, Literal(year_str, datatype=XSD.gYear)))
        if 'journal_name' in row and row['journal_name'].strip():
            journal_uri = uri("journal", row['journal_name'].replace(" ", "_"))
            g.add((journal_uri, EX.hasEdition, volume_uri))

#keywords
with open("dataset_csv/Node_keywords.csv", newline='', encoding='utf-8') as keywords:
    reader = csv.DictReader(keywords)
    for row in reader:
        topic_uri = uri("topic", row['keyword'].replace(" ", "_"))
        g.add((topic_uri, RDF.type, EX.Topic))
        g.add((topic_uri, EX.title, Literal(row['keyword'], datatype=XSD.string)))

#cities?
cities = set()
with open("dataset_csv/Node_edition.csv", newline='', encoding='utf-8') as cities_files:
    reader = csv.DictReader(cities_files)
    for row in reader:
        city_name = row['city'].replace(" ", "_")
        if city_name not in cities:
            cities.add(city_name)
            city_uri = uri("city", city_name)
            g.add((city_uri, RDF.type, EX.City))
            g.add((city_uri, EX.title, Literal(row['city'], datatype=XSD.string)))

#author-paper wrote
with open("dataset_csv/Edge_paper_author_wrote.csv", newline='', encoding='utf-8') as writes:
    reader = csv.DictReader(writes)
    for row in reader:
        author_uri = uri("author", row['author_id'])
        paper_uri = uri("paper", row['id_paper'])
        g.add((author_uri, EX.writes, paper_uri))
        g.add((author_uri, EX.correspondingAuthor, paper_uri))

#author-paper co-wrote
with open("dataset_csv/Edge_paper_author_cowrote.csv", newline='', encoding='utf-8') as cowrites:
    reader = csv.DictReader(cowrites)
    for row in reader:
        author_uri = uri("author", row['author_id'])
        paper_uri = uri("paper", row['id_paper'])
        g.add((author_uri, EX.writes, paper_uri))

#author-paper reviews
with open("dataset_csv/Edge_paper_author_reviews.csv", newline='', encoding='utf-8') as reviews:
    reader = csv.DictReader(reviews)
    for row in reader:
        reviewer_uri = uri("author", row['author_id'])
        paper_uri = uri("paper", row['id_paper'])
        review_uri = URIRef(f"http://example.org/research#review_{row['author_id']}_{row['id_paper']}")
        g.add((review_uri, RDF.type, EX.Review))
        g.add((review_uri, EX.reviewer, reviewer_uri))
        g.add((review_uri, EX.reviewsPaper, paper_uri))
        g.add((paper_uri, EX.hasReview, review_uri))
        g.add((reviewer_uri, RDF.type, EX.Reviewer))  

#edition - conference
with open("dataset_csv/edge_edition_conference.csv", newline='', encoding='utf-8') as edition_conference:
    reader = csv.DictReader(edition_conference)
    for row in reader:
        edition_uri = uri("edition", clean_uri_string(row['edition_id']))
        conference_uri = uri("conference", row['conference_name'].replace(" ", "_"))
        g.add((conference_uri, EX.hasEdition, edition_uri))

#paper - edition
with open("dataset_csv/edge_paper_edition.csv", newline='', encoding='utf-8') as paper_edition:
    reader = csv.DictReader(paper_edition)
    for row in reader:
        paper_uri = uri("paper", row['id_paper'])
        edition_uri = uri("edition", clean_uri_string(row['edition_id']))
        g.add((paper_uri, EX.publishedIn, edition_uri))

#paper - keywords
with open("dataset_csv/edge_paper_keywords.csv", newline='', encoding='utf-8') as paper_keywords:
    reader = csv.DictReader(paper_keywords)
    for row in reader:
        paper_uri = uri("paper", row['id_paper'])
        topic_uri = uri("topic", row['keyword'].replace(" ", "_"))
        g.add((paper_uri, EX.hasKeyword, topic_uri))

#paper cites paper
with open("dataset_csv/edge_paper_paper.csv", newline='', encoding='utf-8') as cites:
    reader = csv.DictReader(cites)
    for row in reader:
        paper_uri_1 = uri("paper", row['id_paper'])
        paper_uri_2 = uri("paper", row['cites_value'])
        g.add((paper_uri_1, EX.cites, paper_uri_2))

#paper - volume
with open("dataset_csv/edge_paper_volume.csv", newline='', encoding='utf-8') as paper_volume:
    reader = csv.DictReader(paper_volume)
    for row in reader:
        paper_uri = uri("paper", row['id_paper'])
        volume_uri = uri("volume", row['volume'])
        g.add((paper_uri, EX.publishedIn, volume_uri))

#volume - journal
with open("dataset_csv/edge_volume_journal.csv", newline='', encoding='utf-8') as volume_journal_file:
    reader = csv.DictReader(volume_journal_file)
    for row in reader:
        volume_uri = uri("volume", row['volume'])
        journal_uri = uri("journal", clean_uri_string(row['journal_name']))
        g.add((journal_uri, EX.hasEdition, volume_uri))  


g.serialize(destination="B2_research_publications_abox.ttl")
print("ABOX serialised")

stats = [
    ["Num. of classes", 13],  # As defined in your TBOX
    ["Num. of object properties", 12],  # As defined in your TBOX
    ["Num. of datatype properties", 4],  # As defined in your TBOX
    ["Num. of authors", len(set(g.subjects(RDF.type, EX.Author)))],
    ["Num. of papers", len(set(g.subjects(RDF.type, EX.Paper)))],
    ["Num. of conferences", len(set(g.subjects(RDF.type, EX.Conference)))],
    ["Num. of conference editions", len(set(g.subjects(RDF.type, EX.ConferenceEdition)))],
    ["Num. of journals", len(set(g.subjects(RDF.type, EX.PublicationVenue)))],
    ["Num. of journal volumes", len(set(g.subjects(RDF.type, EX.JournalVolume)))],
    ["Num. of cities", len(set(g.subjects(RDF.type, EX.City)))],
    ["Num. of topics", len(set(g.subjects(RDF.type, EX.Topic)))],
    ["Num. of reviews", len(set(g.subjects(RDF.type, EX.Review)))],
    ["Total Num. of triples", len(g)],
    ["Num. of 'writes' triples", len(list(g.triples((None, EX.writes, None))))],
    ["Num. of 'correspondingAuthor' triples", len(list(g.triples((None, EX.correspondingAuthor, None))))],
    ["Num. of 'hasEdition' triples", len(list(g.triples((None, EX.hasEdition, None))))],
    ["Num. of 'publishedIn' triples", len(list(g.triples((None, EX.publishedIn, None))))],
    ["Num. of 'hasKeyword' triples", len(list(g.triples((None, EX.hasKeyword, None))))],
    ["Num. of 'cites' triples", len(list(g.triples((None, EX.cites, None))))],
    ["Num. of 'heldInCity' triples", len(list(g.triples((None, EX.heldInCity, None))))],
    ["Num. of 'heldDuring' triples", len(list(g.triples((None, EX.heldDuring, None))))],
    ["Num. of 'hasReview' triples", len(list(g.triples((None, EX.hasReview, None))))],
    ["Num. of 'reviewer' triples", len(list(g.triples((None, EX.reviewer, None))))],
    ["Num. of 'reviewsPaper' triples", len(list(g.triples((None, EX.reviewsPaper, None))))],
]

stats_df = pd.DataFrame(stats, columns=["Statistic", "Value"])
stats_df.to_csv("B2_4_abox_stats.csv", index=False)