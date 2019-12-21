package fr.ceri;

import fr.ceri.entities.*;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.search.SearchHit;
import org.json.JSONObject;
import org.json.XML;

import java.io.*;
import java.util.Arrays;
import java.util.List;

public class Main
{
    public static void main(String[] args) throws IOException
    {
        WriterToFS writerToFS = new WriterToFS();

//       String field = "hashtags";
//
//       ElasticQuery query = new ElasticQuery("localhost", 9200, "http");
//       SearchRequest request = query.buildElasticQuery(new String[]{field}, null);
//       List<SearchHit> hits = query.sendElasticQuery(request);
//
//       HashtagProcessor hashProc = new HashtagProcessor();
//
//       hashProc.convertToHashtagMap(hits, field);
//       hashProc.displayHashtagMap();
//       writerToFS.writeToFS(hashProc.getHashMap(), hashProc.getTargetDataFile());

         WordProcessor wordProc = new WordProcessor();
         wordProc.convertToWordMapAndFormat();
         writerToFS.writeToFS(wordProc.getWordList(), wordProc.getTargetDataFile());

        //TRUC SVM
//        try
//        {
//            System.out.println("Tweets");
//            String testFile = new File("src/fr/ceri/data/unlabeled.xml").toString();
//            System.out.println(testFile);
//
//            FileInputStreamll fis = new FileInputStream("src/fr/ceri/data/unlabeled.xml");
//            BufferedReader reader = new BufferedReader(new InputStreamReader(fis));
//
//            JSONObject myJsonObj = XML.toJSONObject(reader, true);
////        System.out.println();
//
//            BufferedWriter writer = new BufferedWriter(new FileWriter("src/fr/ceri/data/unlabeled_test_string.json"));
//            writer.write(myJsonObj.toString(4));
//            writer.close();
//
//            LexiqueCreator lexLuthor = new LexiqueCreator();
//            lexLuthor.writeLexiqueToFile();
//            lexLuthor.transformTweets(new File("src/fr/ceri/data/task1-train.csv"));
//        }
//        catch (Exception ex)
//        {
//            System.out.println("Exception caught:" + ex.getMessage());
//            System.out.println("Stack trace:" + Arrays.toString(ex.getStackTrace()));
//        }
//        try
//        {
//            System.out.println("Tweets");
//
//            LexiqueCreator lexLuthor = new LexiqueCreator();
//            lexLuthor.writeLexiqueToFile();
//            lexLuthor.transformTweets(new File("src/fr/ceri/data/task1-train.csv"));
//        }
//        catch (Exception ex)
//        {
//            System.out.println("Exception caught:" + ex.getMessage());
//            System.out.println("Stack trace:" + Arrays.toString(ex.getStackTrace()));
//        }
        }
}
