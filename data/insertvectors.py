
import sys
sys.path.insert(0, "C:\\Users\\Andrew\\lab-project\\model")

from rundoc2vec import Doc2VecModel
from datagenerator import Article


class ArticleVectors (Article): 

    def __init__(self, database="lab_project"):
        Article.__init__(self)
        self.primary = "ArticleInformation"
        self.reference = "ArticleVectors"

    def create_table(self):
        self.di.add_related_table(self.reference, "articleID", "TEXT", 
                                  self.primary)

        self.di.add_column(self.reference, "vector", "NUMPY")

    def insert_data(self, model):
        """Loads a model and inserts a key and vector into the database."""
        d2v = Doc2VecModel(model)
        d2v.load_model()

        # Create the array of (id, vector) tuples 
        s = d2v.docnumber()
        data = [(d2v.get_doctag(i), d2v.get_docvec(i)) for i in range(s)]

        self.di.bulk_insert_np_row(data)

    def get_vector(self):
        q = """SELECT * FROM ArticleVectors"""
        for articleID, vector in self.di.execute_query(q):
            print("%s %s" % (articleID, type(vector)))

if __name__ == "__main__":
    av = ArticleVectors()
    av.insert_data("basicmodel")
