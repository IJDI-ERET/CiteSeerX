import MySQLdb
from paper import paper
import pprint
import elasticpython
from author import author
from cluster import cluster

#returns the first 'n' number of paper ids from the SQL db in the form of a list
def get_ids(cur, n):	

	statement = "SELECT id FROM papers LIMIT %d;" % (n)

	cur.execute(statement)

	return [tup[0] for tup in cur.fetchall()]

#connects to the citeseerx database and returns cursor
def connect_to_citeseerx_db():
	db = MySQLdb.connect(host="csxdb02.ist.psu.edu",
                        user="csx-prod",
                        passwd="csx-prod",
                        db="citeseerx",
			charset='utf8')

	return db.cursor()

#connects to the citegraph database and returns cursor
def connect_to_csx_citegraph():
	db = MySQLdb.connect(host="csxdb02.ist.psu.edu",
                        user="csx-prod",
                        passwd="csx-prod",
                        db="csx_citegraph",
			charset='utf8')

	return db.cursor()

#prepares the data to be upserted into the authors index in elasticsearch
#Upserting means insert if it doesn't exist and update if it does
def authorHelperUpsert(paper, citeseerx_db_cur):

	for auth in paper.values_dict['authors']:

			author1 = author(auth['author_id'])

			author1.values_dict['clusters'] = [auth['cluster']]
			author1.values_dict['name'] = auth['name']
			author1.values_dict['papers'] = [paper.values_dict['paper_id']]

			author1.authors_table_fields(citeseerx_db_cur)

			elasticpython.update_authors_document(es, index='authors', doc_id=author1.values_dict['author_id'],
										doc_type='author', data=author1.values_dict)


#prepares the data to be upserted into the clusters index in elasticsearch
#Upserting means insert if it doesn't exist and update if it does
def clusterHelperUpsert(paper):

	cluster1 = cluster(paper.values_dict['cluster'])

	cluster1.values_dict['included_papers'] = [paper.values_dict['paper_id']]

	list_of_author_names = [auth['name'] for auth in paper.values_dict['authors']]

	cluster1.values_dict['included_authors'] = list_of_author_names

	elasticpython.update_clusters_document(es, index='clusters', doc_id=cluster1.values_dict['cluster_id'],
											doc_type='cluster', data=cluster1.values_dict)



#Main function in script 
if __name__ == "__main__":
	

	citeseerx_db_cur = connect_to_citeseerx_db()

	csx_citegraph_cur = connect_to_csx_citegraph()

	es = elasticpython.establish_ES_connection()

	elasticpython.test_ES_connection()

	number_of_papers_to_index = 200000

	list_of_paper_ids = get_ids(citeseerx_db_cur, number_of_papers_to_index)

	#with open('paper_ids_text_file.txt', 'w') as f:
		#for item in list_of_paper_ids:
			#f.write("%s\n" % item)

	#print("just wrote text file")	

	paper_count = 0

	#iterate through each of the paper_ids selected and add them to the index
	for paper_id in list_of_paper_ids:

		if paper_count % 10:
			print('Total paper count: ', str(paper_count))

		#extract all the fields neccessary for the paper type from the MySQL DBs
		paper1 = paper(paper_id)
		paper1.paper_table_fields(citeseerx_db_cur)
		paper1.authors_table_fields(citeseerx_db_cur)
		paper1.keywords_table_fields(citeseerx_db_cur)
		paper1.csx_citegraph_query(csx_citegraph_cur)
		paper1.retrieve_full_text()

		#Load the paper JSON data into ElasticSearch
		
		elasticpython.create_document(es, index='citeseerx', doc_id=paper1.values_dict['paper_id'], doc_type='paper', data=paper1.values_dict)


		#We also need to update the other types located in our index such as author and cluster
		#By using the update and upserts command in ElasticSearch, we can do this easily
		authorHelperUpsert(paper1, citeseerx_db_cur)

		clusterHelperUpsert(paper1)

		#pprint.pprint(paper1.values_dict)

		paper_count += 1



